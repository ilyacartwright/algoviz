from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealth:

    def test_root_returns_ok(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_root_has_service_name(self):
        r = client.get("/")
        assert "service" in r.json()

    def test_root_has_version(self):
        r = client.get("/")
        assert "version" in r.json()

    def test_health_returns_healthy(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

class TestAlgorithmsRegistry:

    def test_list_all_returns_four_modules(self):
        r = client.get("/algorithms/")
        assert r.status_code == 200
        assert set(r.json().keys()) == {"sorting", "graphs", "trees", "dp"}

    def test_sorting_module_has_six_algorithms(self):
        r = client.get("/algorithms/sorting")
        assert r.status_code == 200
        assert len(r.json()["algorithms"]) == 6

    def test_graphs_module_has_four_algorithms(self):
        r = client.get("/algorithms/graphs")
        assert r.status_code == 200
        assert len(r.json()["algorithms"]) == 4

    def test_trees_module_has_three_algorithms(self):
        r = client.get("/algorithms/trees")
        assert r.status_code == 200
        assert len(r.json()["algorithms"]) == 3

    def test_dp_module_has_four_algorithms(self):
        r = client.get("/algorithms/dp")
        assert r.status_code == 200
        assert len(r.json()["algorithms"]) == 4

    def test_each_algorithm_has_required_fields(self):
        r = client.get("/algorithms/")
        for module in r.json().values():
            for algo in module["algorithms"]:
                assert "id"         in algo
                assert "name"       in algo
                assert "complexity" in algo
                assert "time"       in algo["complexity"]
                assert "space"      in algo["complexity"]
                assert "stable"     in algo["complexity"]

    def test_get_single_algorithm(self):
        r = client.get("/algorithms/sorting/bubble")
        assert r.status_code == 200
        assert r.json()["id"] == "bubble"

    def test_get_single_algorithm_dijkstra(self):
        r = client.get("/algorithms/graphs/dijkstra")
        assert r.status_code == 200
        assert r.json()["id"] == "dijkstra"

    def test_unknown_module_returns_404(self):
        assert client.get("/algorithms/unknown").status_code == 404

    def test_unknown_algorithm_returns_404(self):
        assert client.get("/algorithms/sorting/unknown").status_code == 404

    def test_unknown_module_for_algo_returns_404(self):
        assert client.get("/algorithms/unknown/bubble").status_code == 404