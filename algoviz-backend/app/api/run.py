from fastapi import APIRouter, HTTPException
from app.core.schemas import (
    SortRequest, SortResponse,
    GraphRequest, GraphResponse,
    TreeRequest, TreeResponse,
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