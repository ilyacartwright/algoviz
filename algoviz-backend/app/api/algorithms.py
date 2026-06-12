from fastapi import APIRouter, HTTPException

router = APIRouter()

# Реестр алгоритмов
# Структура: module_id -> {label, algorithms: [{id, name, complexity}]}

REGISTRY: dict = {
    'sorting': {
        'algorithms': [
            {
                'id': 'bubble',
                'name': 'Bubble Sort',
                'complexity': {
                    "time": 'O(n^2)', 
                    'space': 'O(1)',
                    'stable': 'да'
                }
            },
            {
                'id': 'selection',
                'name': 'Selection Sort',
                'complexity': {
                    "time": 'O(n^2)', 
                    'space': 'O(1)',
                    'stable': 'нет'
                }
            },
            {
                'id': 'insertion',
                'name': 'Insertion Sort',
                'complexity': {
                    "time": 'O(n^2)', 
                    'space': 'O(1)',
                    'stable': 'да'
                }
            },
            {
                'id': 'merge',
                'name': 'Merge Sort',
                'complexity': {
                    "time": 'O(n log(n))', 
                    'space': 'O(n)',
                    'stable': 'да'
                }
            },
            {
                'id': 'quick',
                'name': 'Quick Sort',
                'complexity': {
                    "time": 'O(n log(n))', 
                    'space': 'O(log(n))',
                    'stable': 'нет'
                }
            },
            {
                'id': 'heap',
                'name': 'Heap Sort',
                'complexity': {
                    "time": 'O(n log(n))', 
                    'space': 'O(1)',
                    'stable': 'нет'
                }
            },
        ]
    },
    "graphs": {
        "label": "Графы",
        "algorithms": [
            {
                "id": "bfs",
                "name": "BFS - обход в ширину",
                "complexity": {
                    "time": "O(V+E)", 
                    "space": "O(V)", 
                    "stable": "нет"
                },
            },
            {
                "id": "dfs",
                "name": "DFS - обход в глубину",
                "complexity": {
                    "time": "O(V+E)", 
                    "space": "O(V)", 
                    "stable": "нет"
                },
            },
            {
                "id": "dijkstra",
                "name": "Алгоритм Дейкстры",
                "complexity": {
                    "time": "O((V+E) log V)", 
                    "space": "O(V)", 
                    "stable": "нет"
                },
            },
            {
                "id": "bellman",
                "name": "Bellman-Ford",
                "complexity": {
                    "time": "O(V*E)", 
                    "space": "O(V)", 
                    "stable": "нет"
                },
            },
        ],
    },
    "trees": {
        "label": "Деревья",
        "algorithms": [
            {
                "id": "bst",
                "name": "BST — двоичное дерево поиска",
                "complexity": {
                    "time": "O(log n) avg", 
                    "space": "O(n)", 
                    "stable": "да"
                },
            },
            {
                "id": "avl",
                "name": "AVL-дерево",
                "complexity": {
                    "time": "O(log n)", 
                    "space": "O(n)", 
                    "stable": "да"
                },
            },
            {
                "id": "max_heap",
                "name": "Max-Heap",
                "complexity": {
                    "time": "O(log n)", 
                    "space": "O(n)", 
                    "stable": "нет"
                },
            },
        ],
    },
    "dp": {
        "label": "Динамическое программирование",
        "algorithms": [
            {
                "id": "lcs",
                "name": "LCS - наибольшая общая подпоследовательность",
                "complexity": {
                    "time": "O(m*n)", 
                    "space": "O(m*n)", 
                    "stable": "да"
                },
            },
            {
                "id": "edit",
                "name": "Edit Distance - расстояние Левенштейна",
                "complexity": {
                    "time": "O(m*n)", 
                    "space": "O(m*n)", 
                    "stable": "да"
                },
            },
            {
                "id": "knapsack",
                "name": "0/1 Knapsack - задача о рюкзаке",
                "complexity": {
                    "time": "O(n*W)", 
                    "space": "O(n*W)", 
                    "stable": "да"
                },
            },
            {
                "id": "fib",
                "name": "Числа Фибоначчи",
                "complexity": {
                    "time": "O(n)", 
                    "space": "O(n)", 
                    "stable": "да"
                }
            }
        ]
    }
}

# Эндпоинты

@router.get(
    '/',
    summary='Полный реестр алгоритмов',
    response_description='Словарь всех модулей с их алгоритмами'
)
async def list_all() -> dict:
    """
    Возвращает полный реестр всех алгоритмов сгруппированных по модулям.
    """
    return REGISTRY

@router.get(
    '/{module}',
    summary='Алгоритмы одного модуля',
    response_description='Список алгоритмов с метаданными'
)
async def list_module(module: str) -> dict:
    """
    Возвращает алгоритмы одного модуля.
 
    Args:
        module: Идентификатор модуля.
 
    Raises:
        HTTPException 404: Если модуль не найден в реестре.
    """
    if module not in REGISTRY:
        raise HTTPException(
            status_code=404, 
            detail=f'Модуль "{module}" не найден. Доступные: {list(REGISTRY.keys())}'
        )
    return REGISTRY[module]


@router.get(
    '/{module}/{algo_id}',
    summary='Матеданные одного алгоритма',
    response_description='Объект алгоритма с id, name и complexity'
)
async def get_algo(module: str, algo_id: str) -> dict:
    """
    Возвращает метаданные конкретного алгоритма.
 
    Args:
        module: Идентификатор модуля
        algo_id: Идентификатор алгоритма 
 
    Raises:
        HTTPException 404: Если модуль или алгоритм не найден.
    """
    if module not in REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f'Модуль "{module}" не найден.'
        )
    
    for algo in REGISTRY[module]['algorithms']:
        if algo['id'] == algo_id:
            return algo
        
    raise HTTPException(
        status_code=404, 
        detail=f'Алгоритм "{algo_id}" не найден в модуле "{module}".'
    )