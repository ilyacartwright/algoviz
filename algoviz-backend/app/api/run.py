from fastapi import APIRouter, HTTPException
from app.core.schemas import SortRequest, SortResponse
from app.algorithms.sorting.algorithms import (
    run_sort,
    random_array,
    COMPLEXITY as SORT_C,
)

router = APIRouter()

@router.post(
    '/sort',
    response_model=SortResponse,
    summary='Запустить алгоритм сортировки',
    response_description='Исходный массив и полная история шагов'
)
async def run_sort_endpoint(req: SortRequest) -> SortResponse:
    """
    Выполняет алгоритм сортировки и возвращает все шаги для визуализации.

    Если массив не передан в теле запроса - генерируется случайный массив в диапазоне [10, 99].

    Пример запроса:
        POST /run/sort
        {"algorithm": "bubble", "size": 20}

    Пример запроса с собственным массивом:
        POST /run/sort
        {"algorithm": "merge", "array": [5, 3, 8, 1, 9, 2]}

    Args:
        req: Тело запроса с алгоритмом и опциональным массивом.

    Returns:
        SortResponse с исходным массивом, шагами и метаданными сложности.

    Raises:
        HTTPException 400: Если передан неизвестный алгоритм.
    """
    # Используем переданный массив или генерируем случайный
    arr = req.array if req.array else random_array(req.size)

    try:
        steps = run_sort(req.algorithm.value, arr)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return SortResponse(
        algorithm=req.algorithm,
        array=arr,
        steps=steps,
        total_steps=len(steps),
        complexity=SORT_C[req.algorithm.value]
    )