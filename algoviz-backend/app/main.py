from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import algorithms, run

app = FastAPI(
    title='AlgoViz API',
    description=(
        "REST API для визуализатора алгоритмов и структур данных."
        "Поддерживает сортировки, графы, деревья и задачи ДП"
        "Каждый алгоритм возвращает пошаговую историю для анимаии на фронте"
    ),
    version="0.2",
    docs_url='/docs',
    redoc_url='/redoc'
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://localhost:5173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Роутеры
app.include_router(
    algorithms.router,
    prefix='/algorithms',
    tags=['algorithms'],
)
app.include_router(
    run.router,
    prefix='/run', 
    tags=['run']
)

# HEALTH-эндпоинты

@app.get('/', tags=['health'], summary='Информация о сервисе')
async def root() -> dict:
    return {"status": "ok", "service": "AlgoViz API", "version": "0.2"}


@app.get("/health", tags=["health"], summary="Health check")
async def health() -> dict:
    return {"status": "healthy"}