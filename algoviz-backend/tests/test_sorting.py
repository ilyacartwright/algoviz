import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.algorithms.sorting.algorithms import (
    bubble_sort, selection_sort, insertion_sort,
    merge_sort, quick_sort, heap_sort,
    run_sort, random_array, SORT_ALGORITHMS, COMPLEXITY,
)

client = TestClient(app)


def last_array(steps) -> list[int]:
    return steps[-1].data["array"]


def all_step_types(steps) -> set[str]:
    return {s.data.get("type") for s in steps}


class TestSortingAlgorithms:
    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_result_is_sorted(self, algo_fn):
        arr = [5, 2, 8, 1, 9, 3]
        steps = algo_fn(arr)
        assert last_array(steps) == sorted(arr)

    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_returns_steps(self, algo_fn):
        steps = algo_fn([3, 1, 2])
        assert len(steps) > 0

    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_last_step_is_done(self, algo_fn):
        steps = algo_fn([4, 2, 7, 1])
        assert steps[-1].data["type"] == "done"

    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_step_has_required_fields(self, algo_fn):
        steps = algo_fn([3, 1, 2])
        for step in steps:
            assert isinstance(step.index, int)
            assert isinstance(step.message, str)
            assert "array" in step.data
            assert "type" in step.data

    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_step_indices_are_sequential(self, algo_fn):
        steps = algo_fn([5, 3, 1, 4, 2])
        for i, step in enumerate(steps):
            assert step.index == i

    @pytest.mark.parametrize("algo_fn", [
        bubble_sort, selection_sort, insertion_sort,
        merge_sort, quick_sort, heap_sort,
    ])
    def test_original_array_not_modified(self, algo_fn):
        arr = [3, 1, 4, 1, 5]
        original = list(arr)
        algo_fn(arr)
        assert arr == original

    def test_bubble_has_compare_and_swap_steps(self):
        steps = bubble_sort([3, 1, 2])
        types = all_step_types(steps)
        assert "compare" in types
        assert "swap" in types

    def test_merge_has_place_steps(self):
        steps = merge_sort([4, 2, 3, 1])
        types = all_step_types(steps)
        assert "place" in types

    def test_quick_has_pivot_steps(self):
        steps = quick_sort([4, 2, 3, 1])
        types = all_step_types(steps)
        assert "pivot" in types

    def test_already_sorted_array(self):
        arr = [1, 2, 3, 4, 5]
        for algo_fn in [
            bubble_sort, selection_sort, insertion_sort,
            merge_sort, quick_sort, heap_sort
        ]:
            steps = algo_fn(arr)
            assert last_array(steps) == arr

    def test_reverse_sorted_array(self):
        arr = [5, 4, 3, 2, 1]
        for algo_fn in [
            bubble_sort, selection_sort, insertion_sort,
            merge_sort, quick_sort, heap_sort
        ]:
            steps = algo_fn(arr)
            assert last_array(steps) == sorted(arr)

    def test_single_element(self):
        arr = [42]
        for algo_fn in [
            bubble_sort, selection_sort, insertion_sort,
            merge_sort, quick_sort, heap_sort
        ]:
            steps = algo_fn(arr)
            assert last_array(steps) == [42]

    def test_two_elements(self):
        for algo_fn in [
            bubble_sort, selection_sort, insertion_sort,
            merge_sort, quick_sort, heap_sort
        ]:
            assert last_array(algo_fn([2, 1])) == [1, 2]
            assert last_array(algo_fn([1, 2])) == [1, 2]

    def test_duplicate_elements(self):
        arr = [3, 1, 3, 2, 1]
        for algo_fn in [
            bubble_sort, selection_sort, insertion_sort,
            merge_sort, quick_sort, heap_sort
        ]:
            assert last_array(algo_fn(arr)) == sorted(arr)


class TestHelpers:

    def test_random_array_length(self):
        arr = random_array(15)
        assert len(arr) == 15

    def test_random_array_range(self):
        arr = random_array(100)
        assert all(10 <= x <= 99 for x in arr)

    def test_run_sort_dispatcher(self):
        arr = [3, 1, 2]
        for algo in SORT_ALGORITHMS:
            steps = run_sort(algo, arr)
            assert last_array(steps) == sorted(arr)

    def test_run_sort_unknown_algorithm(self):
        with pytest.raises(ValueError, match="Неизвестный алгоритм"):
            run_sort("unknown_algo", [1, 2, 3])

    def test_complexity_has_all_algorithms(self):
        for algo in SORT_ALGORITHMS:
            assert algo in COMPLEXITY
            assert "time" in COMPLEXITY[algo]
            assert "space" in COMPLEXITY[algo]
            assert "stable" in COMPLEXITY[algo]


class TestSortEndpoint:

    @pytest.mark.parametrize("algo", [
        "bubble", "selection", "insertion",
        "merge", "quick", "heap"
    ])
    def test_random_array_all_algorithms(self, algo):
        r = client.post("/run/sort", json={
            "algorithm": algo,
            "size": 10
        })
        assert r.status_code == 200
        data = r.json()
        last = data["steps"][-1]["data"]["array"]
        assert last == sorted(last)

    def test_custom_array(self):
        arr = [5, 3, 8, 1, 9, 2]
        r = client.post("/run/sort", json={
            "algorithm": "merge",
            "array": arr
        })
        assert r.status_code == 200
        last = r.json()["steps"][-1]["data"]["array"]
        assert last == sorted(arr)

    def test_response_schema(self):
        r = client.post("/run/sort", json={
            "algorithm": "bubble",
            "size": 8
        })
        assert r.status_code == 200
        data = r.json()
        assert "algorithm" in data
        assert "array" in data
        assert "steps" in data
        assert "total_steps" in data
        assert "complexity" in data

    def test_total_steps_matches_steps_length(self):
        r = client.post("/run/sort", json={
            "algorithm": "quick",
            "size": 12
        })
        data = r.json()
        assert data["total_steps"] == len(data["steps"])

    def test_complexity_fields(self):
        r = client.post("/run/sort", json={
            "algorithm": "heap",
            "size": 5
        })
        c = r.json()["complexity"]
        assert "time" in c
        assert "space" in c
        assert "stable" in c

    def test_invalid_algorithm(self):
        r = client.post("/run/sort", json={
            "algorithm": "unknown",
            "size": 5
        })
        assert r.status_code == 422

    def test_size_too_small(self):
        r = client.post("/run/sort", json={
            "algorithm": "bubble",
            "size": 2
        })
        assert r.status_code == 422

    def test_size_too_large(self):
        r = client.post("/run/sort", json={
            "algorithm": "bubble",
            "size": 200
        })
        assert r.status_code == 422

    def test_steps_have_correct_structure(self):
        r = client.post("/run/sort", json={
            "algorithm": "insertion",
            "size": 6
        })
        for step in r.json()["steps"]:
            assert "index" in step
            assert "message" in step
            assert "data" in step
            assert "array" in step["data"]