import random
import heapq
from app.core.schemas import Step, GraphNode, GraphEdge

# Метаданные сложности

COMPLEXITY: dict[str, dict[str, str]] = {
    'bfs': {
        'time': 'O(V+E)',
        'space': 'O(V)',
        'stable': 'нет'
    },
    'dfs': {
        'time': 'O(V+E)',
        'space': 'O(V)',
        'stable': 'нет'
    },
    'dijkstra': {
        'time': 'O((V+E) log V)',
        'space': 'O(V)',
        'stable': 'нет'
    },
    'bellman': {
        'time': 'O(V*E)',
        'space': 'O(V)',
        'stable': 'нет'
    },
}

# Генерация случайного графа

def generate_random_graph(n: int) -> tuple[list[GraphNode], list[GraphEdge]]:
    '''
    Генерирует случайный связный неориентированный взвешенный граф. 

    Каждая вершина получает 2-3 случайных соседа. 
    Гарантируется, что вершина 0 имеет хотя бы одно ребро.

    Args:
        n: количество вершин (3-16).

    Returns:
        Кортеж (nodes, edges) c координатами для SVG
    '''
    W, H = 560, 300
    labels = [chr(65 + i) for i in range(n)]

    nodes = [
        GraphNode(
            id=i,
            label=labels[i],
            x=round(60 + random.random() * (W - 120), 1),
            y=round(50 + random.random() * (H - 100), 1),
        )
        for i in range(n)
    ]

    edges: list[GraphEdge] = []
    edge_set: set[tuple[int, int]] = set()

    for i in range(n):
        neighbors = {i}
        degree = 2 + random.randint(0, 1)
        for _ in range(degree):
            j = random.randint(0, n - 1)
            if j not in neighbors:
                neighbors.add(j)
                key = (min(i, j), max(i, j))
                if key not in edge_set:
                    edge_set.add(key)
                    edges.append(GraphEdge(u=i, v=j, w=random.randint(1, 9)))

    if not any(e.u == 0 or e.v == 0 for e in edges):
        edges.append(GraphEdge(u=0, v=1, w=random.randint(1, 9)))

    return nodes, edges

# Вспом. ф-ции

def _build_adj(n: int, edges: list[GraphEdge]) -> list[list[tuple[int, int]]]:
    """
    Список смежности из списка рёбер.

    Args:
        n: кол-во вершин
        edges: список рёбер

    Returns:
        adj[u] = [(u,w), ...] - соседи вершины u с весамии
    """

    adj: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for e in edges:
        adj[e.u].append((e.v, e.w))
        adj[e.v].append((e.u, e.w))
    return adj

def _edge_key(u: int, v: int) -> str:
    '''Нормализованный ключ ребра - порядок вершин не важен'''
    return f'{min(u, v)}-{max(u,v)}'

def _step(
        idx: int,
        msg: str,
        node_states: dict[str, str],
        edge_states: dict[str, str],
        **kwargs
) -> Step:
    '''Создает шаг с текущем состоянием вершин и ребер'''
    return Step(
        index=idx,
        message=msg,
        data={
            'node_states': dict(node_states),
            'edge_states': dict(edge_states),
            **kwargs
        },
    )

# Алгоритмы 
def bfs(nodes: list[GraphNode], edges: list[GraphEdge],
        start: int = 0) -> list[Step]:
    '''
    Обход в ширину

    Args:
        nodes: список вершин с координатами
        edges: список рёбер
        start: индекс стартовой вершины
    
    Returns:
        Список шагов с изменениями node_states и edge_states
    '''
    n = len(nodes)
    adj = _build_adj(n, edges)
    visited = [False] * n
    queue = [start]
    visited[start] = True

    node_states: dict[str, str] = {str(start): 'start'}
    edge_states: dict[str, str] = {}
    steps: list[Step] = []
    idx = 0

    steps.append(_step(
        idx, f'BFS: начинаем с вершины {nodes[start].label}',
        node_states, edge_states
    ))
    idx += 1

    while queue:
        u = queue.pop(0)

        if u != start:
            node_states[str(u)] = 'current'

        for v, _ in adj[u]:
            key = _edge_key(u, v)
            edge_states[key] = 'active'

            steps.append(_step(
                idx, 
                f'BFS: рассматриваем ребро {nodes[u].label} -> {nodes[v].label}',
                node_states, edge_states,
            ))
            idx += 1

            if not visited[v]:
                visited[v] = True
                node_states[str(v)] = 'queued'
                queue.append(v)

            edge_states[key] = 'visited'

        if u != start:
            node_states[str(u)] = 'visited'

        steps.append(_step(
            idx, 
            f'BFS: вершина {nodes[u].label} обработана',
            node_states, edge_states
        ))
        idx += 1

    return steps

def dfs(nodes: list[GraphNode], edges: list[GraphEdge],
        start: int = 0) -> list[Step]:
    """
    Обход в глубину

    Args:
        nodes: Список вершин с координатами
        edges: Список рёбер
        start: Индекс стартовой вершины

    Returns:
        Список шагов с изменениями node_states и edge_states
    """
    n = len(nodes)
    adj = _build_adj(n, edges)
    visited = [False] * n

    node_states: dict[str, str] = {str(start): "start"}
    edge_states: dict[str, str] = {}
    steps: list[Step] = []
    counter = [0]

    def _dfs(u: int) -> None:
        """Рекурсивный обход из вершины u."""
        visited[u] = True
        if u != start:
            node_states[str(u)] = "current"

        steps.append(_step(
            counter[0],
            f"DFS: посещаем вершину {nodes[u].label}",
            node_states, edge_states,
        ))
        counter[0] += 1

        for v, _ in adj[u]:
            if not visited[v]:
                key = _edge_key(u, v)
                edge_states[key] = "visited"
                node_states[str(v)] = "queued"

                steps.append(_step(
                    counter[0],
                    f"DFS: идём {nodes[u].label}→{nodes[v].label}",
                    node_states, edge_states,
                ))
                counter[0] += 1
                _dfs(v)

        # Возврат: вершина полностью исследована
        if u != start:
            node_states[str(u)] = "visited"

        steps.append(_step(
            counter[0],
            f"DFS: возвращаемся из {nodes[u].label}",
            node_states, edge_states,
        ))
        counter[0] += 1

    _dfs(start)
    return steps


def dijkstra(nodes: list[GraphNode], edges: list[GraphEdge], start: int = 0) -> list[Step]:
    """
    Алгоритм Дейкстры - кратчайшие пути от стартовой вершины.

    Args:
        nodes: Список вершин с координатами
        edges: Список рёбер с весами
        start: Индекс стартовой вершины

    Returns:
        Список шагов. Каждый шаг содержит поле distances -
        текущие кратчайшие расстояния от стартовой вершины.
    """
    n = len(nodes)
    adj = _build_adj(n, edges)
    INF = float("inf")

    dist = [INF] * n
    dist[start] = 0
    visited = [False] * n
    pq = [(0, start)]  # (расстояние, вершина)

    node_states: dict[str, str] = {str(start): "start"}
    edge_states: dict[str, str] = {}
    steps: list[Step] = []
    idx = 0

    def dist_snapshot() -> dict[str, int]:
        """Снимок текущих расстояний (только достижимые вершины)."""
        return {str(i): d for i, d in enumerate(dist) if d < INF}

    steps.append(_step(
        idx,
        f"Dijkstra: dist[{nodes[start].label}]=0, остальные=∞",
        node_states, edge_states,
        distances=dist_snapshot(),
    ))
    idx += 1

    while pq:
        d, u = heapq.heappop(pq)

        if visited[u]:
            continue

        visited[u] = True
        if u != start:
            node_states[str(u)] = "current"

        for v, w in adj[u]:
            key = _edge_key(u, v)
            edge_states[key] = "active"
            new_d = dist[u] + w

            steps.append(_step(
                idx,
                f"Dijkstra: {nodes[u].label}→{nodes[v].label}, "
                f"dist={dist[u]}+{w}={new_d}",
                node_states, edge_states,
                distances=dist_snapshot(),
                relaxing=[u, v],
            ))
            idx += 1

            if new_d < dist[v]:
                dist[v] = new_d
                node_states[str(v)] = "queued"
                heapq.heappush(pq, (new_d, v))

            edge_states[key] = "visited"

        if u != start:
            node_states[str(u)] = "visited"

        steps.append(_step(
            idx,
            f"Dijkstra: кратчайший путь до {nodes[u].label} = {dist[u]}",
            node_states, edge_states,
            distances=dist_snapshot(),
        ))
        idx += 1

    return steps


def bellman_ford(nodes: list[GraphNode], edges: list[GraphEdge],
                 start: int = 0) -> list[Step]:
    """
    Алгоритм Беллмана–Форда

    Args:
        nodes: Список вершин с координатами
        edges: Список рёбер с весами
        start: Индекс стартовой вершины

    Returns:
        Список шагов с расстояниями после каждой успешной релаксации
    """
    n = len(nodes)
    INF = float("inf")
    dist = [INF] * n
    dist[start] = 0

    edge_list = [(e.u, e.v, e.w) for e in edges] + \
                [(e.v, e.u, e.w) for e in edges]

    node_states: dict[str, str] = {str(start): "start"}
    edge_states: dict[str, str] = {}
    steps: list[Step] = []
    idx = 0

    def dist_snapshot() -> dict[str, int]:
        return {str(i): d for i, d in enumerate(dist) if d < INF}

    steps.append(_step(
        idx,
        f"Bellman-Ford: dist[{nodes[start].label}]=0, остальные=∞",
        node_states, edge_states,
        distances=dist_snapshot(),
    ))
    idx += 1

    # V-1 итераций (гарантия нахождения всех кратчайших путей)
    for iteration in range(n - 1):
        updated = False

        for u, v, w in edge_list:
            if dist[u] < INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True

                node_states[str(u)] = "current"
                key = _edge_key(u, v)
                edge_states[key] = "active"

                steps.append(_step(
                    idx,
                    f"Итерация {iteration + 1}: "
                    f"dist[{nodes[v].label}] = {dist[v]}",
                    node_states, edge_states,
                    distances=dist_snapshot(),
                ))
                idx += 1

                edge_states[key] = "visited"
                node_states[str(v)] = "queued"

        if not updated:
            break

    for i in range(n):
        if dist[i] < INF:
            node_states[str(i)] = "visited" if i != start else "start"

    steps.append(_step(
        idx, "Bellman-Ford: все кратчайшие пути найдены",
        node_states, edge_states,
        distances=dist_snapshot(),
    ))
    return steps

# Диспетчер


GRAPH_ALGORITHMS: dict[str, callable] = {
    "bfs": bfs,
    "dfs": dfs,
    'dijkstra': dijkstra,
    'bellman': bellman_ford,
}

def run_graph(algorithm: str, nodes: list[GraphNode], edges: list[GraphEdge], start: int = 0) -> list[Step]:
    """
    Запускает указанный алгоритм на графе.

    Args:
        algorithm: Идентификатор алгоритма
        nodes: Вершины графа
        edges: Рёбра графа
        start: Индекс стартовой вершины

    Returns:
        Список шагов визуализации

    Raises:
        ValueError: Если алгоритм не найден
    """

    fn = GRAPH_ALGORITHMS.get(algorithm)
    if not fn:
        raise ValueError(
            f"Неизвестный алгоритм графа: '{algorithm}'. "
            f"Доступные: {list(GRAPH_ALGORITHMS.keys())}"
        )
    return fn(nodes, edges, start)