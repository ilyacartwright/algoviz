from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum

# ENUMS

class SortAlgo(str, Enum):
    """Поддерживаемые алгоритмы сортировки"""
    bubble = 'bubble'
    selection = 'selection'
    insertion = 'insertion'
    merge = 'merge'
    quick = 'quick'
    heap = 'heap'

class GraphAlgo(str, Enum):
    """алг. обхода и поиска пути в графе"""
    bfs = 'bfs' # обход в шир.
    dfs = 'dfs' # оход в глуб.
    dijkstra = 'dijkstra' # кратчайший путь (неотриц. веса)
    bellman = 'bellman' # кратч. путь (любые веса) 

class TreeType(str, Enum):
    """структуры данных на основе деревьев"""
    bst = 'bst'
    avl = 'avl'
    max_heap = 'max_heap' # двоичная куча


class DPAlgo(str, Enum):
    """задачи динамического программирования"""
    lcs = 'lcs'
    edit = 'edit'
    knapsack = 'knapsack' 
    fib = 'fib'


class Step(BaseModel):
    """
    Один шаг визуализации алгоритма.

    Алг. возращают список Step - фронт. воспроизводит их 
    последовательно, обновляя состояние визуализации.

    Attributes:
        index: порядковый номер шага (0-based)
        message: Описание происходящего на людском яз.
        data: Состояние структуру данных на этом шаге.
            Содержимое зависит от модуля:
            - Сортировка: {"array": [...], "type": "compare", "comparing": [i, j]}
            - графы: {"node_states": {...}, "edge_states": {...}}
            - деревья: {"nodes": [...], "edges": [...], "highlight": val}
            - DP: {"dp": [[...]], "current": [i, j], "path": [...]}
    """

    index: str
    message: str
    data: dict[str, Any]

# SORT

class SortRequest(BaseModel):
    """
    Запрос на выполнение алгоритма сортировки

    Attributes:
        algorithm: Идентификатор алгоритма из SortAlgo
        array: исходных массив для сортировки. Если не передан генерируется рандомный.
        size: Размер случайного массива (исп. если array не задан). Диапазон: 4-100.
    """

    algorithm: SortAlgo
    array: Optional[list[int]] = Field(
        None,
        description='Исходный массив. Если не передан - генерируется случайный.'
    )
    size: int = Field(20, ge=4, le=100, description='Размер случайного массива')


class SortResponse(BaseModel):
    """
    Ответ с полной историей шагов

    Attrs:
        algorithm: исп. алг.
        array: исх. массив (до сорт.)
        steps: список шагов от 1 сравнения до фин. сост.
        total_steps: общее кол-во шагов
        complexity: Словарь {"time": "...", "space": "...", "stable": "..."}.
    """

    algorithm: SortAlgo
    array: list[int]
    steps: list[Step]
    total_steps: int
    complexity: dict[str, str]


# GRAPHS

class GraphEdge(BaseModel):
    """
    Ребра взвешенного неориентированного графа

    Attrs:
        u: индекс первой вершины
        v: индекс второй вершины
        w: вес ребра (по умолчанию 1)
    """

    u: int
    v: int
    w: int = 1


class GraphNode(BaseModel):
    """
    Вершина графа с координатами для SVG-рендеринга.
 
    Attrs:
        id: Уникальный числовой идентификатор.
        label: Буквенная метка (A, B, C, ...).
        x: Координата X в пространстве SVG (0–560).
        y: Координата Y в пространстве SVG (0–320).
    """

    id: int
    label: str
    x: float
    y: float


class GraphRequest(BaseModel):
    """
    Запрос на выполнение алгоритма на графе.
 
    Attrs:
        algorithm: Алгоритм обхода или поиска пути.
        nodes: Список вершин. Если не переданы - граф генерируется случайно.
        edges: Список рёбер. Если не переданы - граф генерируется случайно.
        node_count: Количество вершин при случайной генерации. Диапазон: 3–16.
        start_node: Индекс стартовой вершины для обхода/поиска пути.
    """
    algorithm: GraphAlgo
    nodes: Optional[list[GraphNode]] = None
    edges: Optional[list[GraphEdge]] = None
    node_count: int = Field(8, ge=3, le=16)
    start_node: int = 0

class GraphResponse(BaseModel):
    """
    Ответ с графом и историей шагов алгоритма.
 
    Attrs:
        algorithm: Исп. алгоритм.
        nodes: Вершины графа (с координатами для рендеринга).
        edges: Рёбра графа.
        steps: Шаги алгоритма. Каждый шаг содержит node_states и edge_states -
                     словари {id: статус}, где статус ∈ {default, start, current, queued, visited}.
        total_steps: Общее количество шагов.
        complexity: Временная и пространственная сложность.
    """
    algorithm: GraphAlgo
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    steps: list[Step]
    total_steps: int
    comlexity: dict[str, str]

# TREE

class TreeRequest(BaseModel):
    """
    Запрос на построение дерева из списка значений.
 
    Алгоритм вставляет значения по одному, фиксируя состояние дерева после каждой вставки как отдельный шаг.
 
    Attrs:
        tree_type: Тип структуры данных (BST, AVL, Max-Heap).
        values: Список целых чисел для вставки. Порядок важен. Ограничение: 1–50 элементов.
    """

    tree_type: TreeType
    values: list[int] = Field(..., min_length=1, max_length=50)


class TreeNodeData(BaseModel):
    """
    Узел дерева с координатами для SVG-рендеринга.
 
    Attrs:
        val: Значение узла.
        x: Координата X центра узла.
        y: Координата Y центра узла.
        left: Индекс левого потомка в списке nodes (или None).
        right: Индекс правого потомка в списке nodes (или None).
        height: Высота поддерева в этом узле (используется для AVL-балансировки).
    """
    val: int
    x: float
    y: float
    left: Optional[int] = None
    right: Optional[int] = None
    height: float


class TreeResponse(BaseModel):
    """
    Ответ с деревом и пошаговой историей вставок.

    Attrs:
        tree_type: Тип построенного дерева.
        nodes: Финальный список узлов с координатами.
        edges: Список рёбер в формате {"from": i, "to": j, "fx":..., "fy":..., "tx":..., "ty":...}.
        steps: Каждый шаг - состояние дерева после одной вставки.
        total_steps: Равно len(values) из запроса.
        complexity: Сложность операций для данного типа дерева.
    """
    tree_type: TreeType
    nodes: list[TreeNodeData]
    edges: list[dict[str, int]]
    steps: list[Step]
    total_steps: int
    complexity: dict[str, str]


# DP

class DPRequest(BaseModel):
    """З
    апрос на выполнение задачи динамического программирования.
 
    Поля заполняются в зависимости от алгоритма:
        lcs, edit: string1, string2
        knapsack: weights, values, capacity
        fib: n
 
    Если параметры не переданы - сервер генерирует случайные данные.
 
    Attrs:
        algorithm: Задача DP из DPAlgo.
        string1: Первая строка (для LCS и Edit Distance). Макс. 12 символов.
        string2: Вторая строка (для LCS и Edit Distance). Макс. 12 символов.
        weights: Веса предметов (для Knapsack). Длина должна совпадать с values.
        values: Ценности предметов (для Knapsack).
        capacity: Ёмкость рюкзака (для Knapsack).
        n: Количество чисел Фибоначчи. Диапазон: 2–20.
    """    
    algorithm: DPAlgo
    string1: Optional[str] = None
    string2: Optional[str] = None
    weights: Optional[list[int]] = None
    values: Optional[list[int]] = None
    capacity: Optional[int] = None
    n: Optional[int] = Field(None, ge=2, le=20)
    

class DPResponse(BaseModel):
    """
    Ответ с таблицей DP и пошаговой историей заполнения.
 
    Attrs:
        algorithm: Исп. задача DP.
        steps: Шаги заполнения таблицы. Каждый шаг содержит:
            dp - текущее состояние таблицы,
            current - координата [i, j] заполняемой ячейки,
            path - список координат оптимального пути (финальный шаг).
        total_steps: Общее количество шагов.
        result: Финальный ответ задачи (длина LCS, расстояние, макс. ценность, F(n)).
        complexity: Временная и пространственная сложность.
        meta: Входные данные задачи (строки, веса, ёмкость и т.д.) для отображения в шапке интерфейса.
    """

    algorithm: DPAlgo
    steps: list[Step]
    total_steps: int
    result: Any
    complexity: dict[str, str]
    meta: dict[str, Any]

# Share

class ShareRequest(BaseModel):
    """
    Запрос на сохранение состояния сессии визуализации.
 
    Используется для создания permalink - короткой ссылки.
 
    Attrs:
        module: Модуль визуализации (sorting / graphs / trees / dp).
        algorithm: Идентификатор алгоритма.
        state: Произвольный словарь с состоянием (массив, шаг, граф и т.д.).
    """
    module: str
    algorithm: str
    state: dict[str, Any]


class ShareResponse(BaseModel):
    """
    Ответ с данными созданной сессии.
 
    Attrs:
        session_id: Короткий уникальный ID сессии (8 символов).
        url: Относительный URL для загрузки сессии (/share/{session_id}).
    """
    session_id: str
    url: str


class SessionResponse(BaseModel):
    """
    Полные данные сохранённой сессии.
 
    Возвращается при GET /share/{session_id}.
 
    Attrs:
        session_id: Уникальный ID сессии.
        module: Модуль визуализации.
        algorithm: Идентификатор алгоритма.
        state: Сохранённое состояние визуализации.
        created_at: Время создания в формате ISO (UTC).
    """
    session_id: str
    module: str
    algorithm: str
    state: dict[str, Any]
    created_at: str