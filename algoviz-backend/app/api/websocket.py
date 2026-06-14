import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.algorithms.sorting.algorithms import run_sort, random_array
from app.algorithms.graphs.algorithms import run_graph, generate_random_graph
from app.algorithms.trees.algorithms import build_tree
from app.algorithms.dp.algorithms import (
    lcs, edit_distance, knapsack, fibonacci,
    random_lcs, random_edit, random_knapsack
)

router = APIRouter()

def _speed_to_delay(speed: int) -> float:
    """
    Конвертирует скорости (1-10) в задержку между шагами в секунду
    Линейная интерполяция:
        speed=1  -> 1.5 сек (очень медленно, для объяснения)
        speed=5  -> ~0.75 сек (комфортный темп)
        speed=10 -> 0.05 сек (максимальная скорость)
    """
    speed = max(1, min(10, speed))
    return round(1.5 - (speed - 1) * (1.45 / 9), 3)


@router.websocket('/stream')
async def ws_stream(ws: WebSocket) -> None:
    """WebSocket эндпоинт для live-стриминга шагов алгоритма."""
    await ws.accept()

    try:
        raw = await ws.receive_text()
        cfg = json.loads(raw)
    except Exception as e:
        await ws.send_json({"type": "error", "message": f"Неверный формат: {e}"})
        await ws.close()
        return
    
    module = cfg.get('module', 'sort')
    algorithm = cfg.get('algorithm', 'bubble')
    speed = cfg.get('speed', 5)
    delay = _speed_to_delay(speed)

    try:
        if module == 'sort':
            arr = cfg.get('array') or random_array(int(cfg.get('size', 20)))
            steps = run_sort(algorithm, arr)
            await ws.send_json({"type": "init", "array": arr, "total": len(steps)})
        elif module == 'graph':
            raw_nodes = cfg.get('nodes')
            raw_edges = cfg.get('edges')
            if raw_nodes and raw_edges:
                from app.core.schemas import GraphNode, GraphEdge
                nodes = [GraphNode(**n) for n in raw_nodes]
                edges = [GraphEdge(**e) for e in raw_edges]
            else:
                nodes, edges = generate_random_graph(int(cfg.get('node_count', 8)))
            start = int(cfg.get("start_node", 0))
            steps = run_graph(algorithm, nodes, edges, start)
            await ws.send_json({
                "type": "init",
                "nodes": [n.model_dump() for n in nodes],
                "edges": [e.model_dump() for e in edges],
                "total": len(steps),
            })
        elif module == "tree":
            tree_type = cfg.get("tree_type", "bst")
            values = cfg.get("values", [50, 30, 70, 20, 40, 60, 80])
            result = build_tree(tree_type, values)
            steps = result["steps"]
            await ws.send_json({"type": "init", "total": len(steps)})
        elif module == "dp":
            if algorithm == "lcs":
                s1 = cfg.get("string1") or random_lcs()[0]
                s2 = cfg.get("string2") or random_lcs()[1]
                steps, _, meta = lcs(s1, s2)
            elif algorithm == "edit":
                s1 = cfg.get("string1") or random_edit()[0]
                s2 = cfg.get("string2") or random_edit()[1]
                steps, _, meta = edit_distance(s1, s2)
            elif algorithm == "knapsack":
                w = cfg.get("weights")
                v = cfg.get("values")
                c = cfg.get("capacity")
                if w and v and c:
                    steps, _, meta = knapsack(len(w), c, w, v)
                else:
                    n, W, ww, vv = random_knapsack()
                    steps, _, meta = knapsack(n, W, ww, vv)
            elif algorithm == "fib":
                steps, _, meta = fibonacci(int(cfg.get("n", 12)))
            else:
                raise ValueError(f"Неизвестный DP алгоритм: {algorithm}")
            await ws.send_json({"type": "init", "total": len(steps), "meta": meta})
        else:
            await ws.send_json({"type": "error", "message": f"Неизвестный модуль: {module}"})
            return
    except Exception as e:
        await ws.send_json({"type": "error", "message": str(e)})
        await ws.close()
        return
    
    paused = False

    async def _listen_commands() -> None:
        """Фоновая задача: слушает команды от клиента во время стриминга."""
        nonlocal paused, delay
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
                cmd = json.loads(msg)
                if cmd.get('cmd') == 'pause':
                    paused = True
                elif cmd.get('cmd') == 'resume':
                    paused = False
                elif cmd.get('cmd') == 'speed':
                    delay = _speed_to_delay(int(cmd.get('value', 5)))
            except asyncio.TimeoutError:
                pass # нет команды
            except Exception:
                break

    listener = asyncio.create_task(_listen_commands())

    try:
        for step in steps:
            while paused:
                await asyncio.sleep(0.1)

            await ws.send_json({
                'type': 'step',
                'index': step.index,
                'total': len(steps),
                'message': step.message,
                'data': step.data,
            })
            await asyncio.sleep(delay)

        await ws.send_json({'type': 'done', 'total': len(steps)})
    except WebSocketDisconnect:
        pass
    finally:
        listener.cancel()