import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.algorithms.dp.algorithms import (
    lcs, edit_distance, knapsack, fibonacci,
    random_lcs, random_edit, random_knapsack,
    COMPLEXITY,
)

client = TestClient(app)

class TestLCS:
    def test_known_result_abcbdab_bdcab(self):
        _, result, _ = lcs("ABCBDAB", "BDCAB")
        assert result == 4

    def test_known_result_aggtab_gxtxayb(self):
        _, result, _ = lcs("AGGTAB", "GXTXAYB")
        assert result == 4

    def test_empty_first_string(self):
        _, result, _ = lcs("", "ABC")
        assert result == 0

    def test_empty_second_string(self):
        _, result, _ = lcs("ABC", "")
        assert result == 0

    def test_both_strings_empty(self):
        _, result, _ = lcs("", "")
        assert result == 0

    def test_identical_strings(self):
        s = "HELLO"
        _, result, _ = lcs(s, s)
        assert result == len(s)

    def test_no_common_subsequence(self):
        _, result, _ = lcs("AAA", "BBB")
        assert result == 0

    def test_single_char_match(self):
        _, result, _ = lcs("A", "A")
        assert result == 1

    def test_single_char_no_match(self):
        _, result, _ = lcs("A", "B")
        assert result == 0

    def test_steps_have_dp_table(self):
        steps, _, _ = lcs("AB", "AB")
        for step in steps:
            assert "dp" in step.data

    def test_steps_have_row_and_col_headers(self):
        steps, _, _ = lcs("AB", "CD")
        for step in steps:
            assert "row_hdr" in step.data
            assert "col_hdr" in step.data

    def test_final_step_has_path(self):
        steps, _, _ = lcs("ABCBDAB", "BDCAB")
        assert "path" in steps[-1].data

    def test_final_step_no_current(self):
        steps, _, _ = lcs("AB", "AB")
        assert steps[-1].data["current"] is None

    def test_intermediate_steps_have_current(self):
        steps, _, _ = lcs("AB", "AB")
        middle_steps = [s for s in steps if s.data.get("current") is not None]
        assert len(middle_steps) > 0

    def test_meta_contains_input_strings(self):
        _, _, meta = lcs("HELLO", "WORLD")
        assert meta["string1"] == "HELLO"
        assert meta["string2"] == "WORLD"

    def test_dp_table_dimensions(self):
        m, n = 3, 4
        s1 = "A" * m
        s2 = "B" * n
        steps, _, _ = lcs(s1, s2)
        final_dp = steps[-1].data["dp"]
        assert len(final_dp) == m + 1
        assert len(final_dp[0]) == n + 1

    def test_indices_are_sequential(self):
        steps, _, _ = lcs("ABC", "AC")
        for i, s in enumerate(steps):
            assert s.index == i

class TestEditDistance:
    def test_horse_to_ros(self):
        _, d, _ = edit_distance("HORSE", "ROS")
        assert d == 3

    def test_intention_to_execution(self):
        _, d, _ = edit_distance("INTENTION", "EXECUTION")
        assert d == 5

    def test_same_strings(self):
        _, d, _ = edit_distance("HELLO", "HELLO")
        assert d == 0

    def test_empty_to_string(self):
        _, d, _ = edit_distance("", "HELLO")
        assert d == 5

    def test_string_to_empty(self):
        _, d, _ = edit_distance("HELLO", "")
        assert d == 5

    def test_single_insertion(self):
        _, d, _ = edit_distance("A", "AB")
        assert d == 1

    def test_single_deletion(self):
        _, d, _ = edit_distance("AB", "A")
        assert d == 1

    def test_single_substitution(self):
        _, d, _ = edit_distance("A", "B")
        assert d == 1

    def test_boundary_conditions_in_dp(self):
        """dp[i][0] = i и dp[0][j] = j."""
        steps, _, _ = edit_distance("ABC", "XY")
        first_dp = steps[0].data["dp"]
        for i in range(len(first_dp)):
            assert first_dp[i][0] == i
        for j in range(len(first_dp[0])):
            assert first_dp[0][j] == j

    def test_meta_contains_strings(self):
        _, _, meta = edit_distance("FROM", "TO")
        assert meta["string1"] == "FROM"
        assert meta["string2"] == "TO"

    def test_steps_have_dp_and_current(self):
        steps, _, _ = edit_distance("AB", "CD")
        middle = [s for s in steps if s.data.get("current") is not None]
        assert len(middle) > 0
        for s in middle:
            assert "dp" in s.data

class TestKnapsack:

    def test_known_result(self):
        _, result, _ = knapsack(4, 8, [2, 3, 4, 5], [3, 4, 5, 6])
        assert result == 10

    def test_zero_capacity(self):
        _, result, _ = knapsack(3, 0, [1, 2, 3], [4, 5, 6])
        assert result == 0

    def test_all_items_too_heavy(self):
        _, result, _ = knapsack(3, 1, [5, 6, 7], [10, 20, 30])
        assert result == 0

    def test_take_all_items(self):
        _, result, _ = knapsack(3, 10, [1, 2, 3], [4, 5, 6])
        assert result == 15

    def test_single_item_fits(self):
        _, result, _ = knapsack(1, 5, [3], [7])
        assert result == 7

    def test_single_item_does_not_fit(self):
        _, result, _ = knapsack(1, 2, [5], [7])
        assert result == 0

    def test_steps_have_dp_table(self):
        steps, _, _ = knapsack(2, 5, [2, 3], [3, 4])
        for step in steps:
            assert "dp" in step.data

    def test_dp_table_dimensions(self):
        n, W = 3, 6
        steps, _, _ = knapsack(n, W, [1, 2, 3], [2, 4, 6])
        final_dp = steps[-1].data["dp"]
        assert len(final_dp) == n + 1
        assert len(final_dp[0]) == W + 1

    def test_meta_contains_input_data(self):
        _, _, meta = knapsack(2, 5, [2, 3], [3, 4])
        assert meta["items"]    == 2
        assert meta["capacity"] == 5
        assert meta["weights"]  == [2, 3]
        assert meta["values"]   == [3, 4]

    def test_result_is_nonnegative(self):
        for _ in range(5):
            n, W, w, v = random_knapsack()
            _, result, _ = knapsack(n, W, w, v)
            assert result >= 0

class TestFibonacci:
    @pytest.mark.parametrize("n,expected", [
        (2,  1),
        (3,  2),
        (4,  3),
        (5,  5),
        (6,  8),
        (7,  13),
        (8,  21),
        (10, 55),
        (12, 144),
        (15, 610),
    ])
    def test_known_values(self, n, expected):
        _, result, _ = fibonacci(n)
        assert result == expected, f"F({n}) должно быть {expected}"

    def test_sequence_in_meta(self):
        _, _, meta = fibonacci(6)
        assert meta["sequence"][6] == 8

    def test_meta_contains_n(self):
        _, _, meta = fibonacci(7)
        assert meta["n"] == 7

    def test_steps_count(self):
        for n in [2, 5, 10]:
            steps, _, _ = fibonacci(n)
            assert len(steps) == n + 1, \
                f"n={n}: ожидали {n+1} шагов, получили {len(steps)}"

    def test_steps_have_dp(self):
        steps, _, _ = fibonacci(5)
        for step in steps:
            assert "dp" in step.data

    def test_row_header_length(self):
        n = 8
        steps, _, _ = fibonacci(n)
        assert len(steps[0].data["row_hdr"]) == n + 1

    def test_indices_sequential(self):
        steps, _, _ = fibonacci(6)
        for i, s in enumerate(steps):
            assert s.index == i

class TestRandomGenerators:
    def test_random_lcs_returns_nonempty_strings(self):
        for _ in range(5):
            s1, s2 = random_lcs()
            assert isinstance(s1, str) and len(s1) > 0
            assert isinstance(s2, str) and len(s2) > 0

    def test_random_edit_returns_nonempty_strings(self):
        for _ in range(5):
            s1, s2 = random_edit()
            assert isinstance(s1, str) and len(s1) > 0

    def test_random_knapsack_valid_structure(self):
        n, W, weights, values = random_knapsack()
        assert n == len(weights) == len(values)
        assert W > 0
        assert all(w > 0 for w in weights)
        assert all(v > 0 for v in values)

    def test_complexity_covers_all_algorithms(self):
        for algo in ["lcs", "edit", "knapsack", "fib"]:
            assert algo in COMPLEXITY
            assert {"time", "space", "stable"} <= set(COMPLEXITY[algo])

class TestDPEndpoint:
    def test_lcs_with_strings(self):
        r = client.post("/run/dp", json={
            "algorithm": "lcs",
            "string1":   "ABCBDAB",
            "string2":   "BDCAB",
        })
        assert r.status_code == 200
        assert r.json()["result"] == 4

    def test_edit_distance_with_strings(self):
        r = client.post("/run/dp", json={
            "algorithm": "edit",
            "string1":   "HORSE",
            "string2":   "ROS",
        })
        assert r.status_code == 200
        assert r.json()["result"] == 3

    def test_knapsack_with_params(self):
        r = client.post("/run/dp", json={
            "algorithm": "knapsack",
            "weights":   [2, 3, 4, 5],
            "values":    [3, 4, 5, 6],
            "capacity":  8,
        })
        assert r.status_code == 200
        assert r.json()["result"] == 10

    def test_fibonacci_with_n(self):
        r = client.post("/run/dp", json={"algorithm": "fib", "n": 10})
        assert r.status_code == 200
        assert r.json()["result"] == 55

    @pytest.mark.parametrize("algo", ["lcs", "edit", "knapsack", "fib"])
    def test_random_data_when_no_params(self, algo):
        r = client.post("/run/dp", json={"algorithm": algo})
        assert r.status_code == 200
        assert r.json()["total_steps"] > 0

    def test_response_has_all_required_fields(self):
        r = client.post("/run/dp", json={"algorithm": "fib", "n": 5})
        for f in ["algorithm", "steps", "total_steps", "result", "complexity", "meta"]:
            assert f in r.json()

    def test_total_steps_matches_steps_length(self):
        r = client.post("/run/dp", json={"algorithm": "lcs"})
        data = r.json()
        assert data["total_steps"] == len(data["steps"])

    def test_complexity_has_required_fields(self):
        r = client.post("/run/dp", json={"algorithm": "fib", "n": 5})
        c = r.json()["complexity"]
        assert {"time", "space", "stable"} <= set(c)

    def test_algorithm_in_response_matches_request(self):
        r = client.post("/run/dp", json={"algorithm": "fib", "n": 5})
        assert r.json()["algorithm"] == "fib"

    def test_invalid_algorithm_returns_422(self):
        assert client.post("/run/dp", json={"algorithm": "unknown"}).status_code == 422

    def test_fibonacci_n_below_minimum_returns_422(self):
        assert client.post("/run/dp", json={"algorithm": "fib", "n": 1}).status_code == 422

    def test_fibonacci_n_above_maximum_returns_422(self):
        assert client.post("/run/dp", json={"algorithm": "fib", "n": 25}).status_code == 422

    def test_missing_algorithm_returns_422(self):
        assert client.post("/run/dp", json={"string1": "ABC"}).status_code == 422