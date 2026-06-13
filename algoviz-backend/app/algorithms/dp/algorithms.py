import random
from app.core.schemas import Step


# Метаданные сложности

COMPLEXITY: dict[str, dict[str, str]] = {
    "lcs": {
        "time": "O(m*n)", 
        "space": "O(m*n)", 
        "stable": "да"
    },
    "edit": {
        "time": "O(m*n)", 
        "space": "O(m*n)", 
        "stable": "да"
    },
    "knapsack": {
        "time": "O(n*W)", 
        "space": "O(n*W)", 
        "stable": "да"
    },
    "fib": {
        "time": "O(n)",
        "space": "O(n)", 
        "stable": "да"
    },
}

# Примеры для случайной генерации
_LCS_SAMPLES  = [("ABCBDAB", "BDCAB"), ("AGGTAB", "GXTXAYB")]
_EDIT_SAMPLES = [("HORSE", "ROS"), ("INTENTION", "EXECUTION")]

def _step(idx: int, msg: str, **kwargs) -> Step:
    """Создаёт шаг с произвольными полями data."""
    return Step(index=idx, message=msg, data=kwargs)

def lcs(s1: str, s2: str) -> tuple[list[Step], int, dict]:
    """
    Наибольшая общая подпоследовательность

    Args:
        s1: Первая строка
        s2: Вторая строка

    Returns:
        Кортеж (steps, result, meta):
            steps: история заполнения таблицы
            result: длина LCS
            meta: входные строки и заголовки таблицы
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    steps: list[Step] = []
    idx = 0

    row_hdr = [""] + list(s2)  # заголовки столбцов: символы s2
    col_hdr = [""] + list(s1)  # заголовки строк: символы s1

    steps.append(_step(
        idx, "LCS: инициализация — границы заполнены нулями",
        dp=[r[:] for r in dp], current=None,
        row_hdr=row_hdr, col_hdr=col_hdr,
    ))
    idx += 1

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            steps.append(_step(
                idx, f"Сравниваем '{s1[i-1]}' и '{s2[j-1]}'",
                dp=[r[:] for r in dp], current=[i, j],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                msg = (
                    f"Совпадение '{s1[i-1]}': "
                    f"dp[{i}][{j}] = dp[{i-1}][{j-1}]+1 = {dp[i][j]}"
                )
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                msg = (
                    f"Нет совпадения: "
                    f"dp[{i}][{j}] = max({dp[i-1][j]}, {dp[i][j-1]}) = {dp[i][j]}"
                )

            steps.append(_step(
                idx, msg,
                dp=[r[:] for r in dp], current=[i, j],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

    # Восстановление оптимального пути (обратный ход)
    path: set[str] = set()
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            path.add(f"{i},{j}")
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    steps.append(_step(
        idx, f"LCS длина = {dp[m][n]}",
        dp=[r[:] for r in dp], current=None,
        path=list(path), row_hdr=row_hdr, col_hdr=col_hdr,
    ))

    meta = {"string1": s1, "string2": s2, "row_hdr": row_hdr, "col_hdr": col_hdr}
    return steps, dp[m][n], meta


def edit_distance(s1: str, s2: str) -> tuple[list[Step], int, dict]:
    """
    Расстояние редактирования

    Args:
        s1: Исходная строка
        s2: Целевая строка

    Returns:
        Кортеж (steps, result, meta)
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Граничные условия: превращение пустой строки
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    steps: list[Step] = []
    idx = 0
    row_hdr = [""] + list(s2)
    col_hdr = [""] + list(s1)

    steps.append(_step(
        idx, "Edit Distance: инициализация граничных условий",
        dp=[r[:] for r in dp], current=None,
        row_hdr=row_hdr, col_hdr=col_hdr,
    ))
    idx += 1

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = s1[i - 1] == s2[j - 1]
            steps.append(_step(
                idx,
                f"'{s1[i-1]}' {'==' if match else '!='} '{s2[j-1]}': "
                f"{'совпадение' if match else 'выбираем минимум операций'}",
                dp=[r[:] for r in dp], current=[i, j],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

            if match:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1],
                )

            steps.append(_step(
                idx, f"dp[{i}][{j}] = {dp[i][j]}",
                dp=[r[:] for r in dp], current=[i, j],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

    steps.append(_step(
        idx, f"Edit Distance = {dp[m][n]}",
        dp=[r[:] for r in dp], current=None,
        row_hdr=row_hdr, col_hdr=col_hdr,
    ))

    meta = {"string1": s1, "string2": s2, "row_hdr": row_hdr, "col_hdr": col_hdr}
    return steps, dp[m][n], meta

def knapsack(
    n: int, W: int,
    weights: list[int], values: list[int],
) -> tuple[list[Step], int, dict]:
    """
    Задача о рюкзаке 0/1

    Args:
        n: Количество предметов.
        W: Максимальная ёмкость рюкзака.
        weights: Веса предметов (индексация с 0).
        values: Ценности предметов (индексация с 0).

    Returns:
        Кортеж (steps, result, meta).
    """
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    steps: list[Step] = []
    idx = 0

    row_hdr = [str(i) for i in range(W + 1)]
    col_hdr = ["∅"] + [f"i{i+1}" for i in range(n)]

    steps.append(_step(
        idx,
        f"Knapsack: {n} предметов, ёмкость {W}. "
        f"Веса: {weights}, ценности: {values}",
        dp=[r[:] for r in dp], current=None,
        row_hdr=row_hdr, col_hdr=col_hdr,
    ))
    idx += 1

    for i in range(1, n + 1):
        w_i = weights[i - 1]
        v_i = values[i - 1]
        for w in range(W + 1):
            steps.append(_step(
                idx,
                f"Предмет {i} (вес={w_i}, ценность={v_i}), ёмкость={w}",
                dp=[r[:] for r in dp], current=[i, w],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                dp[i][w] = dp[i - 1][w]

            steps.append(_step(
                idx, f"dp[{i}][{w}] = {dp[i][w]}",
                dp=[r[:] for r in dp], current=[i, w],
                row_hdr=row_hdr, col_hdr=col_hdr,
            ))
            idx += 1

    steps.append(_step(
        idx, f"Максимальная ценность = {dp[n][W]}",
        dp=[r[:] for r in dp], current=None,
        row_hdr=row_hdr, col_hdr=col_hdr,
    ))

    meta = {
        "items": n, "capacity": W,
        "weights": weights, "values": values,
        "row_hdr": row_hdr, "col_hdr": col_hdr,
    }
    return steps, dp[n][W], meta

def fibonacci(n: int) -> tuple[list[Step], int, dict]:
    """
    Числа Фибоначчи через динамическое программирование (мемоизация снизу вверх)

    Args:
        n: Количество чисел Фибоначчи для вычисления (2 <= n <= 20)

    Returns:
        Кортеж (steps, result, meta):
            result: значение F(n)
    """
    dp = [0] * (n + 1)
    dp[1] = 1  # F(0) = 0, F(1) = 1

    steps: list[Step] = []
    idx = 0
    row_hdr = [str(i) for i in range(n + 1)]

    steps.append(_step(
        idx, "Fibonacci: F(0)=0, F(1)=1 — базовые случаи",
        dp=[list(dp)], current=[0, 0],
        row_hdr=row_hdr, col_hdr=["F"],
    ))
    idx += 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        steps.append(_step(
            idx,
            f"F({i}) = F({i-1}) + F({i-2}) = {dp[i-1]} + {dp[i-2]} = {dp[i]}",
            dp=[list(dp)], current=[0, i],
            row_hdr=row_hdr, col_hdr=["F"],
        ))
        idx += 1

    steps.append(_step(
        idx, f"F({n}) = {dp[n]} — готово",
        dp=[list(dp)], current=None,
        row_hdr=row_hdr, col_hdr=["F"],
    ))

    meta = {"n": n, "sequence": dp, "row_hdr": row_hdr}
    return steps, dp[n], meta


# Генераторы случайных данных

def random_lcs() -> tuple[str, str]:
    """Возвращает случайную пару строк для задачи LCS."""
    return random.choice(_LCS_SAMPLES)


def random_edit() -> tuple[str, str]:
    """Возвращает случайную пару строк для задачи Edit Distance."""
    return random.choice(_EDIT_SAMPLES)


def random_knapsack() -> tuple[int, int, list[int], list[int]]:
    """Генерирует случайные данные для задачи о рюкзаке."""
    n = 5
    W = 10
    weights = [random.randint(1, 5) for _ in range(n)]
    values  = [random.randint(1, 8) for _ in range(n)]
    return n, W, weights, values