from fastapi import APIRouter, HTTPException
from app.core.schemas import (
    SortRequest, SortResponse,
    GraphRequest, GraphResponse,
    TreeRequest, TreeResponse,
    DPRequest, DPResponse
)
from app.algorithms.sorting.algorithms import (
    run_sort,
    random_array,
    COMPLEXITY as SORT_C,
)
from app.algorithms.graphs.algorithms import (
    run_graph, 
    generate_random_graph, 
    COMPLEXITY as GRAPH_C
)
from app.algorithms.trees.algorithms import (
    build_tree, COMPLEXITY as TREE_C
)

from app.algorithms.dp.algorithms import (
    lcs, edit_distance, knapsack, fibonacci,
    random_lcs, random_edit, random_knapsack,
    COMPLEXITY as DP_C
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

@router.post(
    '/graph',
    response_model=GraphResponse,
    summary='Запустить алгоритм на графе'
)
async def run_graph_endpoint(req: GraphRequest) -> GraphResponse:
    """
    Выполняет алгоритм обхода или поиска пути и возвращает шаги.

    Если nodes и edges не переданы — граф генерируется случайно из node_count вершин. Обход начинается с вершины start_node.
    """
    if req.nodes and req.edges:
        nodes, edges = req.nodes, req.edges
    else:
        nodes, edges = generate_random_graph(req.node_count)

    try:
        steps = run_graph(req.algorithm.value, nodes, edges, req.start_node)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return GraphResponse(
        algorithm=req.algorithm,
        nodes=nodes,
        edges=edges,
        steps=steps,
        total_steps=len(steps),
        complexity=GRAPH_C[req.algorithm.value],
    )


@router.post(
    '/tree',
    response_model=TreeResponse,
    summary='Построить дерево из списка значений',
)
async def run_tree_endpoint(req: TreeRequest) -> TreeResponse:
    """Строит дерево, вставляя значения по одному, и возвращает шаги."""
    try:
        result = build_tree(req.tree_type.value, req.values)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return TreeResponse(
        tree_type=req.tree_type,
        nodes=result["nodes"],
        edges=result["edges"],
        steps=result["steps"],
        total_steps=len(result["steps"]),
        complexity=TREE_C[req.tree_type.value],
    )



@router.post(
    '/dp',
    response_model=DPResponse,
    summary='Запустить задачу динамического программирования'
)
async def run_dp_endpoint(req: DPRequest) -> DPResponse:
    """
    Выполняет задачу ДП и возвращает пошаговое заполнение таблицы

    Параметры зависят от алгоритма:
        lcs, edit: string1, string2 (если не переданы — случайные)
        knapsack: weights, values, capacity (если не переданы — случайные)
        fib: n (если не передано — 12)

    Финальный шаг содержит поле path с координатами оптимального решения.
    """
    algo = req.algorithm.value
    try:
        if algo == "lcs":
            s1 = req.string1 or random_lcs()[0]
            s2 = req.string2 or random_lcs()[1]
            steps, result, meta = lcs(s1, s2)

        elif algo == "edit":
            s1 = req.string1 or random_edit()[0]
            s2 = req.string2 or random_edit()[1]
            steps, result, meta = edit_distance(s1, s2)

        elif algo == "knapsack":
            if req.weights and req.values and req.capacity:
                n = len(req.weights)
                steps, result, meta = knapsack(
                    n, req.capacity, req.weights, req.values
                )
            else:
                n, W, w, v = random_knapsack()
                steps, result, meta = knapsack(n, W, w, v)

        elif algo == "fib":
            steps, result, meta = fibonacci(req.n or 12)

        else:
            raise HTTPException(status_code=400, detail=f"Неизвестный алгоритм DP: {algo}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DPResponse(
        algorithm=req.algorithm,
        steps=steps,
        total_steps=len(steps),
        result=result,
        complexity=DP_C[algo],
        meta=meta,
    )