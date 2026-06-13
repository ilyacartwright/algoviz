import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.algorithms.graphs.algorithms import (
    bfs, dfs, dijkstra, bellman_ford,
    run_graph, generate_random_graph,
    GRAPH_ALGORITHMS, COMPLEXITY, _edge_key,
)
from app.core.schemas import GraphNode, GraphEdge

client = TestClient(app)

@pytest.fixture
def small_graph():
    return generate_random_graph(5)


@pytest.fixture
def triangle_graph():
    nodes = [
        GraphNode(id=0, label="A", x=100.0, y=100.0),
        GraphNode(id=1, label="B", x=200.0, y=50.0),
        GraphNode(id=2, label="C", x=300.0, y=100.0),
    ]
    edges = [
        GraphEdge(u=0, v=1, w=1),
        GraphEdge(u=1, v=2, w=2),
        GraphEdge(u=0, v=2, w=4),
    ]
    return nodes, edges


ALL_GRAPH_FNS = [bfs, dfs, dijkstra, bellman_ford]
ALL_GRAPH_IDS = ["bfs", "dfs", "dijkstra", "bellman"]


class TestGraphStepStructure:

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_returns_nonempty_steps(self, fn, small_graph):
        nodes, edges = small_graph
        assert len(fn(nodes, edges)) > 0

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_indices_are_sequential(self, fn, small_graph):
        nodes, edges = small_graph
        steps = fn(nodes, edges)
        for i, s in enumerate(steps):
            assert s.index == i

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_each_step_has_node_and_edge_states(self, fn, small_graph):
        nodes, edges = small_graph
        for step in fn(nodes, edges):
            assert "node_states" in step.data
            assert "edge_states" in step.data

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_each_step_has_message(self, fn, small_graph):
        nodes, edges = small_graph
        for step in fn(nodes, edges):
            assert isinstance(step.message, str)
            assert len(step.message) > 0

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_start_node_always_in_states(self, fn, small_graph):
        nodes, edges = small_graph
        for step in fn(nodes, edges, start=0):
            assert "0" in step.data["node_states"]

class TestNodeStates:

    VALID_STATES = {"default", "start", "current", "queued", "visited"}

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_node_states_are_valid(self, fn, small_graph):
        nodes, edges = small_graph
        for step in fn(nodes, edges):
            for v in step.data["node_states"].values():
                assert v in self.VALID_STATES

    def test_start_node_state_is_start(self, triangle_graph):
        nodes, edges = triangle_graph
        first_step = bfs(nodes, edges, start=0)[0]
        assert first_step.data["node_states"]["0"] == "start"

    @pytest.mark.parametrize("fn", ALL_GRAPH_FNS)
    def test_last_step_has_visited_nodes(self, fn, small_graph):
        nodes, edges = small_graph
        last = fn(nodes, edges)[-1]
        states = set(last.data["node_states"].values())
        assert "visited" in states or "start" in states

class TestShortestPath:

    def test_dijkstra_start_distance_is_zero(self, triangle_graph):
        nodes, edges = triangle_graph
        steps = dijkstra(nodes, edges, start=0)
        last = steps[-1].data
        assert "distances" in last
        assert last["distances"]["0"] == 0

    def test_bellman_start_distance_is_zero(self, triangle_graph):
        nodes, edges = triangle_graph
        steps = bellman_ford(nodes, edges, start=0)
        last = steps[-1].data
        assert "distances" in last
        assert last["distances"]["0"] == 0

    def test_dijkstra_on_triangle_correct_distances(self, triangle_graph):
        """
        A→B = 1, B→C = 2, A→C = 4.
        Кратчайшие пути от A: до B=1, до C=3 (через B).
        """
        nodes, edges = triangle_graph
        last = dijkstra(nodes, edges, start=0)[-1].data
        assert last["distances"]["0"] == 0
        assert last["distances"]["1"] == 1
        assert last["distances"]["2"] == 3

    def test_bellman_on_triangle_correct_distances(self, triangle_graph):
        nodes, edges = triangle_graph
        last = bellman_ford(nodes, edges, start=0)[-1].data
        assert last["distances"]["0"] == 0
        assert last["distances"]["1"] == 1
        assert last["distances"]["2"] == 3

    def test_dijkstra_distances_present_in_intermediate_steps(self, triangle_graph):
        nodes, edges = triangle_graph
        steps_with_dist = [s for s in dijkstra(nodes, edges)
                           if "distances" in s.data]
        assert len(steps_with_dist) > 0

class TestGraphGeneration:

    @pytest.mark.parametrize("n", [3, 5, 8, 12])
    def test_node_count_matches(self, n):
        nodes, _ = generate_random_graph(n)
        assert len(nodes) == n

    def test_has_edges(self):
        _, edges = generate_random_graph(5)
        assert len(edges) > 0

    def test_node_zero_always_connected(self):
        for _ in range(10):
            _, edges = generate_random_graph(6)
            assert any(e.u == 0 or e.v == 0 for e in edges)

    def test_nodes_have_labels(self):
        nodes, _ = generate_random_graph(5)
        labels = [n.label for n in nodes]
        assert labels == ["A", "B", "C", "D", "E"]

    def test_nodes_have_coordinates_in_range(self):
        nodes, _ = generate_random_graph(8)
        for n in nodes:
            assert 0 <= n.x <= 560
            assert 0 <= n.y <= 320

    def test_edges_have_valid_weights(self):
        _, edges = generate_random_graph(6)
        for e in edges:
            assert 1 <= e.w <= 9

    def test_no_self_loops(self):
        _, edges = generate_random_graph(8)
        for e in edges:
            assert e.u != e.v

    def test_no_duplicate_edges(self):
        _, edges = generate_random_graph(8)
        keys = [_edge_key(e.u, e.v) for e in edges]
        assert len(keys) == len(set(keys))

class TestGraphDispatcher:

    def test_run_graph_all_algorithms(self, small_graph):
        nodes, edges = small_graph
        for name in GRAPH_ALGORITHMS:
            steps = run_graph(name, nodes, edges)
            assert len(steps) > 0

    def test_run_graph_unknown_raises(self, small_graph):
        nodes, edges = small_graph
        with pytest.raises(ValueError, match="Неизвестный"):
            run_graph("unknown", nodes, edges)

    def test_complexity_covers_all(self):
        for algo in GRAPH_ALGORITHMS:
            assert algo in COMPLEXITY
            assert {"time", "space", "stable"} <= set(COMPLEXITY[algo])

class TestGraphEndpoint:

    @pytest.mark.parametrize("algo", ALL_GRAPH_IDS)
    def test_all_algorithms_return_200(self, algo):
        r = client.post("/run/graph", json={"algorithm": algo, "node_count": 5})
        assert r.status_code == 200

    def test_response_has_all_required_fields(self):
        r = client.post("/run/graph", json={"algorithm": "bfs", "node_count": 5})
        for f in ["algorithm", "nodes", "edges", "steps", "total_steps", "complexity"]:
            assert f in r.json()

    def test_node_count_matches_request(self):
        for n in [4, 6, 8]:
            r = client.post("/run/graph", json={"algorithm": "dfs", "node_count": n})
            assert len(r.json()["nodes"]) == n

    def test_total_steps_matches_steps_length(self):
        r = client.post("/run/graph", json={"algorithm": "dijkstra", "node_count": 5})
        data = r.json()
        assert data["total_steps"] == len(data["steps"])

    def test_complexity_has_required_fields(self):
        r = client.post("/run/graph", json={"algorithm": "bfs", "node_count": 4})
        c = r.json()["complexity"]
        assert {"time", "space", "stable"} <= set(c)

    def test_steps_have_node_and_edge_states(self):
        r = client.post("/run/graph", json={"algorithm": "bfs", "node_count": 4})
        for step in r.json()["steps"]:
            assert "node_states" in step["data"]
            assert "edge_states" in step["data"]

    def test_minimum_node_count_returns_200(self):
        assert client.post("/run/graph", json={"algorithm": "bfs", "node_count": 3}).status_code == 200

    def test_maximum_node_count_returns_200(self):
        assert client.post("/run/graph", json={"algorithm": "dfs", "node_count": 16}).status_code == 200

    def test_invalid_algorithm_returns_422(self):
        assert client.post("/run/graph", json={"algorithm": "unknown", "node_count": 5}).status_code == 422

    def test_node_count_too_small_returns_422(self):
        assert client.post("/run/graph", json={"algorithm": "bfs", "node_count": 1}).status_code == 422

    def test_node_count_too_large_returns_422(self):
        assert client.post("/run/graph", json={"algorithm": "bfs", "node_count": 20}).status_code == 422

    def test_missing_algorithm_returns_422(self):
        assert client.post("/run/graph", json={"node_count": 5}).status_code == 422