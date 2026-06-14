import os, uuid, json
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.schemas import ShareRequest, ShareResponse, SessionResponse

router = APIRouter()

REDIS_URL = os.getenv('REDIS_URL', '')

def _get_redis():
    """
    Пытается подключиться к Redis.

    Returns:
        Клиент Redis если REDIS_URL задан и соединение успешно, иначе None.
    """
    try:
        import redis
        if REDIS_URL:
            r = redis.from_url(REDIS_URL, decode_responses=True)
            r.ping()
            return r
    except Exception:
        pass
    return None

_redis = _get_redis()
_SESSIONS: dict[str, dict] = {}
_FALLBACK_FILE = Path('/tmp/algoviz_sessions.json')

def _load_fallback() -> None:
    '''Загрузка сессии (dev реж.)'''
    if _FALLBACK_FILE.exists():
        try:
            _SESSIONS.update(json.loads(_FALLBACK_FILE.read_text()))
        except Exception:
            pass

def _save_fallback() -> None:
    '''Сохранение сессии (dev)'''
    try:
        _FALLBACK_FILE.write_text(json.dumps(_SESSIONS, ensure_ascii=False))
    except Exception:
        pass

if not _redis:
    _load_fallback()


# CRUD операции

def _set_session(sid: str, data: dict) -> None:
    '''Сохраняет сессию'''
    if _redis:
        # TTL 24 часа
        _redis.setex(f"session:{sid}", 86400, json.dumps(data, ensure_ascii=False))
    else:
        _SESSIONS[sid] = data
        _save_fallback()


def _get_session(sid: str) -> dict | None:
    '''Возвращает данные сессии или None если не найдена.'''
    if _redis:
        raw = _redis.get(f"session:{sid}")
        return json.loads(raw) if raw else None
    return _SESSIONS.get(sid)


def _del_session(sid: str) -> None:
    '''Удаляет сессию.'''
    if _redis:
        _redis.delete(f"session:{sid}")
    else:
        _SESSIONS.pop(sid, None)
        _save_fallback()


# Эндпоинты
@router.post(
    "/",
    response_model=ShareResponse,
    summary="Сохранить сессию и получить permalink",
)
async def create_session(req: ShareRequest) -> ShareResponse:
    """Сохраняет состояние визуализации и возвращает короткий ID"""
    session_id = str(uuid.uuid4())[:8]
    data = {
        "session_id": session_id,
        "module":     req.module,
        "algorithm":  req.algorithm,
        "state":      req.state,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _set_session(session_id, data)
    return ShareResponse(session_id=session_id, url=f"/share/{session_id}")


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Загрузить сохранённую сессию",
)
async def get_session(session_id: str) -> SessionResponse:
    """
    Возвращает данные сессии по ID

    Raises:
        HTTPException 404: Если сессия не найдена или истёк TTL
    """
    session = _get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Сессия '{session_id}' не найдена или устарела.",
        )
    return SessionResponse(**session)


@router.delete(
    "/{session_id}",
    summary="Удалить сессию",
)
async def delete_session(session_id: str) -> dict:
    """Удаляет сессию по ID."""
    if not _get_session(session_id):
        raise HTTPException(status_code=404, detail=f"Сессия '{session_id}' не найдена.")
    _del_session(session_id)
    return {"deleted": session_id}


@router.get(
    "/",
    summary="Список активных сессий",
)
async def list_sessions() -> dict:
    """
    Возвращает список активных сессий.
    """
    if _redis:
        keys = _redis.keys("session:*")[:50]
        sessions = []
        for k in keys:
            raw = _redis.get(k)
            if raw:
                d = json.loads(raw)
                sessions.append({
                    "id": d["session_id"],
                    "module": d["module"],
                    "algorithm": d["algorithm"],
                    "created_at": d["created_at"],
                })
    else:
        sessions = [
            {
                "id": sid,
                "module": s["module"],
                "algorithm": s["algorithm"],
                "created_at": s["created_at"],
            }
            for sid, s in list(_SESSIONS.items())[:50]
        ]
    return {
        "count":   len(sessions),
        "backend": "redis" if _redis else "memory",
        "sessions": sessions,
    }