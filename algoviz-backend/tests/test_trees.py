import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.algorithms.trees.algorithms import (
    build_tree, COMPLEXITY,
    _bst_insert, _avl_insert, _heap_insert,
    _count, _depth, _balance_factor, _Node,
)

client = TestClient(app)

STANDARD_VALUES = [50, 30, 70, 20, 40, 60, 80]
ALL_TREE_TYPES  = ["bst", "avl", "max_heap"]


class TestBuildTree:
    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_steps_count_equals_values_count(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        assert len(result["steps"]) == len(STANDARD_VALUES)

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_node_count_matches_unique_values(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        assert result["node_count"] == len(set(STANDARD_VALUES))

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_each_step_has_nodes_field(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for step in result["steps"]:
            assert "nodes" in step.data

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_each_step_has_edges_field(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for step in result["steps"]:
            assert "edges" in step.data

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_each_step_has_highlight(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for i, step in enumerate(result["steps"]):
            assert step.data["highlight"] == STANDARD_VALUES[i]

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_each_step_has_node_count(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for i, step in enumerate(result["steps"]):
            assert step.data["node_count"] == i + 1

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_indices_are_sequential(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for i, step in enumerate(result["steps"]):
            assert step.index == i

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_result_has_depth(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        assert result["depth"] >= 1

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_final_nodes_have_coordinates(self, tree_type):
        result = build_tree(tree_type, STANDARD_VALUES)
        for node in result["nodes"]:
            assert hasattr(node, "x") and hasattr(node, "y")
            assert node.x >= 0
            assert node.y >= 0

    def test_unknown_tree_type_raises(self):
        with pytest.raises(ValueError, match="Неизвестный"):
            build_tree("unknown", [1, 2, 3])


class TestBST:
    def _build_bst(self, values) -> _Node:
        root = None
        for v in values:
            root = _bst_insert(root, v)
        return root

    def test_bst_maintains_order_property(self):
        def check(node, lo=float('-inf'), hi=float('inf')):
            if not node:
                return True
            assert lo < node.val < hi
            return check(node.left, lo, node.val) and check(node.right, node.val, hi)

        root = self._build_bst([50, 30, 70, 20, 40, 60, 80])
        assert check(root)

    def test_bst_ignores_duplicates(self):
        root = self._build_bst([5, 5, 5])
        assert _count(root) == 1

    def test_bst_single_node_is_root(self):
        root = _bst_insert(None, 42)
        assert root.val == 42
        assert root.left is None
        assert root.right is None

    def test_bst_depth_grows_with_insertions(self):
        small = build_tree("bst", [50])
        large = build_tree("bst", [50, 30, 70, 20, 40])
        assert large["depth"] > small["depth"]


class TestAVL:
    def _build_avl(self, values) -> _Node:
        root = None
        for v in values:
            root = _avl_insert(root, v)
        return root

    def test_avl_is_balanced_after_each_insertion(self):
        def check_balanced(node):
            if not node:
                return
            assert abs(_balance_factor(node)) <= 1, \
                f"Узел {node.val}: balance = {_balance_factor(node)}"
            check_balanced(node.left)
            check_balanced(node.right)

        values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]
        root = None
        for v in values:
            root = _avl_insert(root, v)
            check_balanced(root)

    def test_avl_worst_case_stays_balanced(self):
        root = None
        for v in range(1, 16):
            root = _avl_insert(root, v)
        assert abs(_balance_factor(root)) <= 1

    def test_avl_height_is_logarithmic(self):
        import math
        root = None
        n = 31
        for v in range(1, n + 1):
            root = _avl_insert(root, v)
        assert _depth(root) <= 2 * math.log2(n + 1)

    def test_avl_message_contains_height(self):
        result = build_tree("avl", [50, 30, 70])
        for step in result["steps"]:
            assert "высота" in step.message.lower()

class TestMaxHeap:
    def test_root_is_always_maximum(self):
        heap = []
        for v in [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]:
            heap = _heap_insert(heap, v)
        assert heap[0] == max(heap)

    def test_heap_property_after_each_insert(self):
        def check_heap(h):
            for i in range(1, len(h)):
                parent = (i - 1) // 2
                assert h[parent] >= h[i], \
                    f"heap[{parent}]={h[parent]} < heap[{i}]={h[i]}"

        heap = []
        for v in [5, 3, 8, 1, 9, 2, 7]:
            heap = _heap_insert(heap, v)
            check_heap(heap)

    def test_heap_message_contains_maximum(self):
        result = build_tree("max_heap", [3, 1, 4, 1, 5])
        for step in result["steps"][1:]:
            assert "максимум" in step.message.lower()

class TestUtilities:
    def test_count_full_tree(self):
        node = _Node(1, _Node(2), _Node(3))
        assert _count(node) == 3

    def test_count_none(self):
        assert _count(None) == 0

    def test_count_single(self):
        assert _count(_Node(42)) == 1

    def test_depth_single(self):
        assert _depth(_Node(1)) == 1

    def test_depth_chain(self):
        node = _Node(1, _Node(2, _Node(3)))
        assert _depth(node) == 3

    def test_depth_none(self):
        assert _depth(None) == 0

    def test_complexity_covers_all_tree_types(self):
        for tree_type in ALL_TREE_TYPES:
            assert tree_type in COMPLEXITY
            assert {"time", "space", "stable"} <= set(COMPLEXITY[tree_type])


class TestTreeEdgeCases:
    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_single_value(self, tree_type):
        result = build_tree(tree_type, [42])
        assert result["node_count"] == 1
        assert result["depth"] == 1
        assert len(result["steps"]) == 1

    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_two_values(self, tree_type):
        result = build_tree(tree_type, [10, 20])
        assert result["node_count"] == 2
        assert len(result["steps"]) == 2

    def test_bst_large_input(self):
        import random
        values = random.sample(range(1, 200), 30)
        result = build_tree("bst", values)
        assert result["node_count"] == 30

    def test_avl_large_input_stays_balanced(self):
        import random, math
        values = random.sample(range(1, 200), 40)
        result = build_tree("avl", values)
        assert result["depth"] <= 2 * math.log2(41)


class TestTreeEndpoint:
    @pytest.mark.parametrize("tree_type", ALL_TREE_TYPES)
    def test_all_tree_types_return_200(self, tree_type):
        r = client.post("/run/tree", json={
            "tree_type": tree_type,
            "values": STANDARD_VALUES,
        })
        assert r.status_code == 200

    def test_total_steps_equals_values_count(self):
        values = [50, 30, 70, 20, 40]
        r = client.post("/run/tree", json={"tree_type": "bst", "values": values})
        assert r.json()["total_steps"] == len(values)

    def test_response_has_all_required_fields(self):
        r = client.post("/run/tree", json={"tree_type": "avl", "values": [5, 3, 7]})
        for f in ["tree_type", "nodes", "edges", "steps", "total_steps", "complexity"]:
            assert f in r.json()

    def test_tree_type_in_response_matches_request(self):
        r = client.post("/run/tree", json={"tree_type": "avl", "values": [5, 3, 7]})
        assert r.json()["tree_type"] == "avl"

    def test_nodes_count_in_response(self):
        values = [50, 30, 70, 20, 40]
        r = client.post("/run/tree", json={"tree_type": "bst", "values": values})
        assert len(r.json()["nodes"]) == len(set(values))

    def test_complexity_has_required_fields(self):
        r = client.post("/run/tree", json={"tree_type": "avl", "values": [5, 3, 7]})
        c = r.json()["complexity"]
        assert {"time", "space", "stable"} <= set(c)

    def test_single_value(self):
        r = client.post("/run/tree", json={"tree_type": "bst", "values": [42]})
        assert r.status_code == 200
        assert r.json()["total_steps"] == 1

    def test_fifty_values(self):
        import random
        values = random.sample(range(1, 999), 50)
        r = client.post("/run/tree", json={"tree_type": "avl", "values": values})
        assert r.status_code == 200

    def test_invalid_tree_type_returns_422(self):
        r = client.post("/run/tree", json={"tree_type": "unknown", "values": [1, 2]})
        assert r.status_code == 422

    def test_empty_values_returns_422(self):
        r = client.post("/run/tree", json={"tree_type": "bst", "values": []})
        assert r.status_code == 422

    def test_missing_values_returns_422(self):
        r = client.post("/run/tree", json={"tree_type": "bst"})
        assert r.status_code == 422


