from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from app.core.schemas import Step, TreeNodeData

# Метаданные сложности
COMPLEXITY: dict[str, dict[str, str]] = {
    "bst": {
        "time": "O(log n) avg", 
        "space": "O(n)", 
        "stable": "да"
    },
    "avl": {
        "time": "O(log n)",
        "space": "O(n)", 
        "stable": "да"
    },
    "max_heap": {
        "time": "O(log n)",
        "space": "O(n)",
        "stable": "нет"
    },
}

@dataclass
class _Node:
    '''
    Внутреннее представление узла двоичного дерева.

    Attributes:
        val: Значение узла.
        left: Левый потомок (None для листа).
        right: Правый потомок (None для листа).
        height: Высота поддерева (обновляется при AVL-ротациях).
    '''
    val: int
    left: Optional[_Node] = field(default=None, repr=False)
    right: Optional[_Node] = field(default=None, repr=False) 
    height: int = 1


# Утилиты AVL

def _h(n: Optional[_Node]) -> int:
    """Высота узла"""
    return n.height if n else 0

def _update_h(n: _Node) -> None:
    """Пересчёт высоты узла на основе потомков"""
    n.height = 1 + max(_h(n.left), _h(n.right))

def _balance_factor(n: Optional[_Node]) -> int:
    """
    Фактор баланса AVL-узла = высота левого - высота правого поддерева.

    Дерево сбалансировано если |balance| <= 1 для каждого узла.
    """
    return _h(n.left) - _h(n.right) if n else 0

def _rotate_right(y: _Node) -> _Node:
    '''
    Правый поворот вокруг узла y

    Используется когда левое поддерево перегружено (balance > 1)
    '''
    x = y.left
    y.left = x.right
    x.right = y
    _update_h(y)
    _update_h(x)
    return x

def _rotate_left(x: _Node) -> _Node:
    '''
    Левый поворот вокруг узла x

    Используется когда правое поддерево перегружено (balance < -1)
    '''
    y = x.right
    x.right = y.left
    y.left = x
    _update_h(x)
    _update_h(y)
    return y

# bst

def _bst_insert(node: Optional[_Node], val: int) -> _Node:
    '''Вставка в двоичное дерево поиска (без балансировки)'''
    if not node:
        return _Node(val)
    if val < node.val:
        node.left = _bst_insert(node.left, val)
    elif val > node.val:
        node.right = _bst_insert(node.right, val)
    return node

def _bst_min(node: _Node) -> _Node:
    """Находит узел с минимальным значением (крайний левый)."""
    while node.left:
        node = node.left
    return node

def _bst_delete(node: Optional[_Node], val: int) -> Optional[_Node]:
    """
    Удаление из BST.

    Три случая:
        1. Нет левого потомка -> заменяем правым.
        2. Нет правого потомка -> заменяем левым.
        3. Два потомка -> заменяем in-order successor (минимум правого поддерева).
    """
    if not node:
        return None
    if val < node.val:
        node.left = _bst_delete(node.left, val)
    elif val > node.val:
        node.right = _bst_delete(node.right, val)
    else:
        if not node.left:
            return node.right
        if not node.right:
            return node.left
        successor = _bst_min(node.right)
        node.val = successor.val
        node.right = _bst_delete(node.right, successor.val)

    return node

# AVL

def _avl_insert(node: Optional[_Node], val: int) -> _Node:
    """Вставка в AVL-дерево с автоматической балансировкой"""
    if not node:
        return _Node(val)
    if val < node.val:
        node.left = _avl_insert(node.left, val)
    elif val > node.val:
        node.right = _avl_insert(node.right, val)
    else:
        return node
    
    _update_h(node)
    b = _balance_factor(node)

    # Left-left
    if b > 1 and val < node.left.val:
        return _rotate_right(node)
    # Right-Right
    if b < -1 and val > node.right.val:
        return _rotate_left(node)
    # Left-right
    if b > 1 and val > node.left.val:
        node.left = _rotate_left(node.left)
        return _rotate_right(node)
    # Right-Left
    if b < -1 and val < node.right.val:
        node.right = _rotate_right(node.right)
        return _rotate_left(node)
    
    return node


# MAX-HEAP

def _heap_insert(heap: list[int], val: int) -> list[int]:
    """Вставка в max-heap (массовое представление)"""
    heap.append(val)
    i = len(heap) - 1
    while i > 0:
        parent = (i - 1) // 2
        if heap[parent] < heap[i]:
            heap[parent], heap[i] = heap[i], heap[parent]
            i = parent
        else:
            break
    return heap


def _heap_to_node(arr: list[int], i: int) -> Optional[_Node]:
    """
    Конвертирует массовое представление кучи в дерево _Node.

    Элемент i имеет потомков 2i+1 (левый) и 2i+2 (правый).
    """
    if i >= len(arr):
        return None
    node = _Node(arr[i])
    node.left  = _heap_to_node(arr, 2 * i + 1)
    node.right = _heap_to_node(arr, 2 * i + 2)
    return node


# layout дерево -> координаты

def _assign_positions(
    node: Optional[_Node],
    level: int,
    left: float,
    right: float,
    positions: dict[int, tuple[float, float]],
    id_map: dict[int, int],
    counter: list[int],
) -> None:
    """
    Рекурсивно назначает координаты (x, y) каждому узлу.

    Args:
        node: Текущий узел
        level: Уровень в дереве (0 = корень)
        left: Левая граница горизонтального диапазона
        right: Правая граница горизонтального диапазона
        positions: Словарь {id(node): (x, y)} - заполняется рекурсивно.
        id_map: Словарь {id(node): порядковый_индекс} для ссылок left/right.
        counter: Одноэлементный список для счётчика (мутабельный в рекурсии).
    """
    if not node:
        return

    node_id = counter[0]
    id_map[id(node)] = node_id
    counter[0] += 1

    x = (left + right) / 2
    y = level * 60 + 28
    positions[id(node)] = (x, y)

    mid = (left + right) / 2
    _assign_positions(node.left,  level + 1, left, mid,   positions, id_map, counter)
    _assign_positions(node.right, level + 1, mid,  right, positions, id_map, counter)


def _count(node: Optional[_Node]) -> int:
    """Подсчитывает количество узлов в дереве."""
    return 0 if not node else 1 + _count(node.left) + _count(node.right)


def _depth(node: Optional[_Node]) -> int:
    """Вычисляет глубину (высоту) дерева."""
    return 0 if not node else 1 + max(_depth(node.left), _depth(node.right))


def _tree_to_data(
    root: Optional[_Node],
    highlight: Optional[int] = None,
    canvas_w: float = 560.0,
) -> tuple[list[TreeNodeData], list[dict]]:
    """
    Конвертирует дерево в плоские списки узлов и рёбер для SVG-рендеринга

    Args:
        root: Корень дерева.
        highlight: Значение узла для подсветки (последняя вставка).
        canvas_w: Ширина SVG-холста (используется для разбиения диапазона).

    Returns:
        Кортеж (nodes_data, edges_data):
            nodes_data: список TreeNodeData с координатами и ссылками.
            edges_data: список словарей с координатами рёбер для <line>.
    """
    if not root:
        return [], []

    positions: dict[int, tuple[float, float]] = {}
    id_map:    dict[int, int] = {}
    counter = [0]
    _assign_positions(root, 0, 0, canvas_w, positions, id_map, counter)

    nodes_data: list[TreeNodeData] = []
    edges_data: list[dict] = []

    def _collect(node: Optional[_Node]) -> None:
        if not node:
            return

        nid = id_map[id(node)]
        x, y = positions[id(node)]
        left_id  = id_map.get(id(node.left))  if node.left  else None
        right_id = id_map.get(id(node.right)) if node.right else None

        nodes_data.append(TreeNodeData(
            val=node.val,
            x=round(x, 1),
            y=round(y, 1),
            left=left_id,
            right=right_id,
            height=node.height,
        ))

        # Рёбра с координатами обоих концов для SVG <line>
        if node.left:
            lx, ly = positions[id(node.left)]
            edges_data.append({
                "from": nid, "to": id_map[id(node.left)],
                "fx": round(x, 1), "fy": round(y, 1),
                "tx": round(lx, 1), "ty": round(ly, 1),
            })
        if node.right:
            rx, ry = positions[id(node.right)]
            edges_data.append({
                "from": nid, "to": id_map[id(node.right)],
                "fx": round(x, 1), "fy": round(y, 1),
                "tx": round(rx, 1), "ty": round(ry, 1),
            })

        _collect(node.left)
        _collect(node.right)

    _collect(root)
    return nodes_data, edges_data


# Публичный API
def build_tree(tree_type: str, values: list[int]) -> dict:
    """
    Строит дерево из списка значений с записью шага после каждой вставки

    Args:
        tree_type: Тип дерева
        values: Список значений для вставки (порядок важен)

    Returns:
        Словарь с ключами:
            nodes: Финальный список узлов с координатами.
            edges: Финальный список рёбер.
            steps: История вставок (len == len(values)).
            node_count: Количество узлов в итоговом дереве.
            depth: Глубина итогового дерева.

    Raises:
        ValueError: Если передан неизвестный tree_type.
    """
    if tree_type not in COMPLEXITY:
        raise ValueError(
            f"Неизвестный тип дерева: '{tree_type}'. "
            f"Доступные: {list(COMPLEXITY.keys())}"
        )
    
    root: Optional[_Node] = None
    heap: list[int] = []
    steps: list[Step] = []
    idx = 0

    for val in values:
        if tree_type == "bst":
            root = _bst_insert(root, val)
            msg = f"BST: вставляем {val}"
        elif tree_type == "avl":
            root = _avl_insert(root, val)
            msg = (
                f"AVL: вставляем {val}, "
                f"высота дерева = {_h(root)}, "
                f"баланс корня = {_balance_factor(root)}"
            )
        else:  # max_heap
            heap = _heap_insert(heap, val)
            root = _heap_to_node(heap, 0)
            msg = f"Max-Heap: вставляем {val}, максимум = {heap[0]}"

        nodes_data, edges_data = _tree_to_data(root, highlight=val)
        steps.append(Step(
            index=idx,
            message=msg,
            data={
                "nodes": [n.model_dump() for n in nodes_data],
                "edges": edges_data,
                "highlight": val,
                "node_count": _count(root),
                "depth": _depth(root),
            },
        ))
        idx += 1

    nodes_data, edges_data = _tree_to_data(root)
    return {
        "nodes": nodes_data,
        "edges": edges_data,
        "steps": steps,
        "node_count": _count(root),
        "depth":  _depth(root),
    }