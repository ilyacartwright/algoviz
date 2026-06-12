import random
from app.core.schemas import Step


# Метаданные сложности

COMPLEXITY: dict[str, dict[str, str]] = {
    "bubble": {"time": "O(n^2)", "space": "O(1)", "stable": "да"},
    "selection": {"time": "O(n^2)", "space": "O(1)", "stable": "нет"},
    "insertion": {"time": "O(n^2)", "space": "O(1)", "stable": "да"},
    "merge": {"time": "O(n log n)", "space": "O(n)", "stable": "да"},
    "quick": {"time": "O(n log n)", "space": "O(log n)", "stable": "нет"},
    "heap": {"time": "O(n log n)", "space": "O(1)", "stable": "нет"},
}

# Вспом. ф-ции

def random_array(size: int) -> list[int]:
    return [random.randint(10, 99) for _ in range(size)]

def _step(idx: int, msg: str, arr: list[int], **kwargs) -> Step:
    """
    Объект Step с текущим сост. массива

    Args:
        idx: Порядковый номер шага.
        msg: Описание операции для лог-панели.
        arr: Текущее состояние массива (копируется автоматически через list()).
        **kwargs: Дополнительные поля data: type, comparing, swapping, pivot, sorted_from, highlight.
    """
    return Step(index=idx, message=msg, data={"array": list(arr), **kwargs})

def bubble_sort(arr: list[int]) -> list[Step]:
    """
    Сортировка пузырьком.

    Оптимизация: ранний выход если проход прошёл без обменов (массив уже отсортирован).
    """
    a = list(arr)
    n = len(a)
    steps: list[Step] = []
    idx = 0
    sorted_from = n

    for i in range(n - 1):
        swapped = False

        for j in range(n - i - 1):
            steps.append(_step(
                idx, f"Сравниваем a[{j}]={a[j]} и a[{j+1}]={a[j+1]}",
                a, type="compare", comparing=[j, j + 1], sorted_from=sorted_from,
            ))
            idx += 1

            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                steps.append(_step(
                    idx, f"Обмен: {a[j+1]} ↔ {a[j]}",
                    a, type="swap", swapping=[j, j + 1], sorted_from=sorted_from,
                ))
                idx += 1

        # После прохода правый элемент встал на место
        sorted_from = n - i - 1

        # Ранний выход: массив уже отсортирован
        if not swapped:
            break

    steps.append(_step(idx, "Сортировка пузырьком завершена", a, type="done", sorted_from=0))
    return steps


def selection_sort(arr: list[int]) -> list[Step]:
    """
    Сортировка выбором.

    Особенность: ровно n-1 обмен независимо от входных данных.
    """
    a = list(arr)
    n = len(a)
    steps: list[Step] = []
    idx = 0

    for i in range(n - 1):
        min_idx = i

        for j in range(i + 1, n):
            steps.append(_step(
                idx,
                f"Ищем минимум: a[{j}]={a[j]} vs текущий мин a[{min_idx}]={a[min_idx]}",
                a, type="compare", comparing=[min_idx, j], pivot=i,
            ))
            idx += 1
            if a[j] < a[min_idx]:
                min_idx = j

        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            steps.append(_step(
                idx, f"Ставим минимум {a[i]} на позицию {i}",
                a, type="swap", swapping=[i, min_idx],
            ))
            idx += 1

    steps.append(_step(idx, "Сортировка выбором завершена", a, type="done", sorted_from=0))
    return steps


def insertion_sort(arr: list[int]) -> list[Step]:
    """
    Сортировка вставками.
    """
    a = list(arr)
    n = len(a)
    steps: list[Step] = []
    idx = 0

    for i in range(1, n):
        j = i
        # Сдвигаем элемент влево пока он меньше предыдущего
        while j > 0:
            steps.append(_step(
                idx, f"Сравниваем a[{j-1}]={a[j-1]} и a[{j}]={a[j]}",
                a, type="compare", comparing=[j - 1, j],
            ))
            idx += 1

            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                steps.append(_step(
                    idx, f"Вставка: сдвигаем {a[j]} влево",
                    a, type="swap", swapping=[j - 1, j],
                ))
                idx += 1
                j -= 1
            else:
                break  # элемент на правильной позиции

    steps.append(_step(idx, "Сортировка вставками завершена", a, type="done", sorted_from=0))
    return steps


def merge_sort(arr: list[int]) -> list[Step]:
    """
    Сортировка слиянием.
    """
    a = list(arr)
    steps: list[Step] = []
    counter = [0]

    def _merge(arr: list[int], l: int, r: int) -> None:
        """Рекурсивно сортирует подмассив arr[l..r] включительно."""
        if l >= r:
            return

        m = (l + r) // 2
        _merge(arr, l, m)
        _merge(arr, m + 1, r)

        left  = arr[l:m + 1]
        right = arr[m + 1:r + 1]
        i = j = 0
        k = l

        while i < len(left) and j < len(right):
            steps.append(_step(
                counter[0],
                f"Слияние: сравниваем {left[i]} и {right[j]}",
                arr, type="compare", comparing=[l + i, m + 1 + j],
            ))
            counter[0] += 1

            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1

            steps.append(_step(
                counter[0], f"Помещаем {arr[k]} на позицию {k}",
                arr, type="place", highlight=[k],
            ))
            counter[0] += 1
            k += 1

        # Копируем оставшиеся элементы
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

    _merge(a, 0, len(a) - 1)
    steps.append(_step(counter[0], "Сортировка слиянием завершена", a, type="done", sorted_from=0))
    return steps


def quick_sort(arr: list[int]) -> list[Step]:
    """
    Быстрая сортировка (схема Lomuto).
    """
    a = list(arr)
    steps: list[Step] = []
    counter = [0]

    def _partition(arr: list[int], l: int, r: int) -> int:
        """
        Разбивает подмассив arr[l..r] относительно пивота arr[r].

        Возвращает финальную позицию пивота.
        """
        pivot = arr[r]
        steps.append(_step(
            counter[0], f"Пивот = {pivot} (позиция {r})",
            arr, type="pivot", pivot=r,
        ))
        counter[0] += 1

        i = l - 1

        for j in range(l, r):
            steps.append(_step(
                counter[0], f"Сравниваем {arr[j]} с пивотом {pivot}",
                arr, type="compare", comparing=[j, r], pivot=r,
            ))
            counter[0] += 1

            if arr[j] <= pivot:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    steps.append(_step(
                        counter[0], f"Обмен {arr[j]} ↔ {arr[i]}",
                        arr, type="swap", swapping=[i, j], pivot=r,
                    ))
                    counter[0] += 1

        arr[i + 1], arr[r] = arr[r], arr[i + 1]
        steps.append(_step(
            counter[0], f"Пивот {pivot} встаёт на позицию {i + 1}",
            arr, type="swap", swapping=[i + 1, r],
        ))
        counter[0] += 1
        return i + 1

    def _quick(arr: list[int], l: int, r: int) -> None:
        """Рекурсивно сортирует подмассив arr[l..r]."""
        if l < r:
            p = _partition(arr, l, r)
            _quick(arr, l, p - 1)
            _quick(arr, p + 1, r)

    _quick(a, 0, len(a) - 1)
    steps.append(_step(counter[0], "Быстрая сортировка завершена", a, type="done", sorted_from=0))
    return steps


def heap_sort(arr: list[int]) -> list[Step]:
    """
    Пирамидальная сортировка.
    """
    a = list(arr)
    n = len(a)
    steps: list[Step] = []
    counter = [0]

    def _heapify(arr: list[int], heap_size: int, root: int) -> None:
        """
        Восстанавливает свойство max-heap для поддерева с корнем root.

        Args:
            heap_size: Размер активной части кучи (остаток уже отсортирован).
            root: Индекс корня поддерева для восстановления.
        """
        largest = root
        left    = 2 * root + 1
        right   = 2 * root + 2

        cmp_idx = left if left < heap_size else root
        steps.append(_step(
            counter[0], f"Heapify: проверяем узел {root} (значение {arr[root]})",
            arr, type="compare", comparing=[root, cmp_idx],
            sorted_from=heap_size,
        ))
        counter[0] += 1

        if left < heap_size and arr[left] > arr[largest]:
            largest = left
        if right < heap_size and arr[right] > arr[largest]:
            largest = right

        if largest != root:
            arr[root], arr[largest] = arr[largest], arr[root]
            steps.append(_step(
                counter[0], f"Обмен {arr[largest]} ↔ {arr[root]}",
                arr, type="swap", swapping=[root, largest],
                sorted_from=heap_size,
            ))
            counter[0] += 1
            _heapify(arr, heap_size, largest)

    # Фаза 1: построение max-heap (обходим внутренние узлы снизу вверх)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(a, n, i)

    # Фаза 2: извлекаем максимум n-1 раз
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        steps.append(_step(
            counter[0], f"Извлекаем максимум {a[i]} → позиция {i}",
            a, type="swap", swapping=[0, i], sorted_from=i,
        ))
        counter[0] += 1
        _heapify(a, i, 0)

    steps.append(_step(counter[0], "Пирамидальная сортировка завершена", a, type="done", sorted_from=0))
    return steps


# Диспетчер

SORT_ALGORITHMS: dict[str, callable] = {
    'bubble': bubble_sort,
    'selection': selection_sort,
    'insertion': insertion_sort,
    'merge': merge_sort,
    'quick': quick_sort,
    'heap': heap_sort,
}


def run_sort(algorithm: str, arr: list[int]) -> list[Step]:
    """
    Запускает указанный алгоритм сортировки и возвращает историю шагов.

    Args:
        algorithm: Идентификатор алгоритма (ключ из SORT_ALGORITHMS).
        arr: Исходный массив для сортировки.

    Returns:
        Список Step от первого сравнения до финального состояния.

    Raises:
        ValueError: Если алгоритм не найден в SORT_ALGORITHMS.
    """
    fn = SORT_ALGORITHMS.get(algorithm)
    if not fn:
        raise ValueError(
            f"Неизвестный алгоритм сортировки: '{algorithm}'. "
            f"Доступные: {list(SORT_ALGORITHMS.keys())}"
        )
    return fn(arr)