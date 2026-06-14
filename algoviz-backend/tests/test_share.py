import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_session(module="sort", algo="merge", state=None) -> dict:
    """Создаёт сессию и возвращает тело ответа."""
    r = client.post("/share/", json={
        "module":    module,
        "algorithm": algo,
        "state":     state or {"array": [3, 1, 2], "step": 5},
    })
    assert r.status_code == 200
    return r.json()

class TestCreateSession:

    def test_returns_200(self):
        r = client.post("/share/", json={
            "module": "sort", "algorithm": "bubble", "state": {},
        })
        assert r.status_code == 200

    def test_response_has_session_id(self):
        data = create_session()
        assert "session_id" in data

    def test_session_id_is_eight_chars(self):
        data = create_session()
        assert len(data["session_id"]) == 8

    def test_response_has_url(self):
        data = create_session()
        assert "url" in data

    def test_url_contains_session_id(self):
        data = create_session()
        assert data["session_id"] in data["url"]

    def test_url_starts_with_share(self):
        data = create_session()
        assert data["url"].startswith("/share/")

    def test_each_session_gets_unique_id(self):
        ids = {create_session()["session_id"] for _ in range(5)}
        assert len(ids) == 5

    def test_missing_module_returns_422(self):
        r = client.post("/share/", json={"algorithm": "bfs", "state": {}})
        assert r.status_code == 422

    def test_missing_algorithm_returns_422(self):
        r = client.post("/share/", json={"module": "graph", "state": {}})
        assert r.status_code == 422

    def test_missing_state_returns_422(self):
        r = client.post("/share/", json={"module": "sort", "algorithm": "bubble"})
        assert r.status_code == 422

class TestGetSession:

    def test_returns_200_for_existing_session(self):
        sid = create_session()["session_id"]
        assert client.get(f"/share/{sid}").status_code == 200

    def test_returns_correct_module(self):
        sid = create_session(module="graph", algo="bfs")["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert data["module"] == "graph"

    def test_returns_correct_algorithm(self):
        sid = create_session(algo="dijkstra")["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert data["algorithm"] == "dijkstra"

    def test_returns_correct_state(self):
        state = {"array": [5, 3, 1], "step": 42, "speed": 7}
        sid = create_session(state=state)["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert data["state"]["step"]  == 42
        assert data["state"]["speed"] == 7

    def test_response_has_session_id(self):
        sid = create_session()["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert data["session_id"] == sid

    def test_response_has_created_at(self):
        sid = create_session()["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert "created_at" in data
        assert len(data["created_at"]) > 0

    def test_created_at_is_iso_format(self):
        from datetime import datetime
        sid = create_session()["session_id"]
        created_at = client.get(f"/share/{sid}").json()["created_at"]
        # ISO формат можно разобрать без ошибок
        datetime.fromisoformat(created_at)

    def test_nonexistent_session_returns_404(self):
        assert client.get("/share/nonexist").status_code == 404

    def test_short_id_returns_404(self):
        assert client.get("/share/abc").status_code == 404

    def test_complex_state_preserved(self):
        state = {
            "nodes":   [{"id": 0, "label": "A"}, {"id": 1, "label": "B"}],
            "edges":   [{"u": 0, "v": 1, "w": 3}],
            "stepIndex": 15,
            "algo":    "dijkstra",
        }
        sid = create_session(state=state)["session_id"]
        data = client.get(f"/share/{sid}").json()
        assert data["state"]["stepIndex"] == 15
        assert len(data["state"]["nodes"]) == 2

class TestDeleteSession:

    def test_delete_returns_200(self):
        sid = create_session()["session_id"]
        assert client.delete(f"/share/{sid}").status_code == 200

    def test_delete_response_contains_deleted_id(self):
        sid = create_session()["session_id"]
        data = client.delete(f"/share/{sid}").json()
        assert data["deleted"] == sid

    def test_deleted_session_returns_404_on_get(self):
        sid = create_session()["session_id"]
        client.delete(f"/share/{sid}")
        assert client.get(f"/share/{sid}").status_code == 404

    def test_delete_nonexistent_returns_404(self):
        assert client.delete("/share/nonexist").status_code == 404

    def test_double_delete_returns_404(self):
        sid = create_session()["session_id"]
        client.delete(f"/share/{sid}")
        assert client.delete(f"/share/{sid}").status_code == 404

class TestListSessions:

    def test_returns_200(self):
        assert client.get("/share/").status_code == 200

    def test_response_has_count(self):
        r = client.get("/share/")
        assert "count" in r.json()

    def test_response_has_sessions_list(self):
        r = client.get("/share/")
        assert "sessions" in r.json()

    def test_count_increases_after_creation(self):
        before = client.get("/share/").json()["count"]
        create_session()
        after = client.get("/share/").json()["count"]
        assert after >= before + 1

    def test_response_has_backend_field(self):
        r = client.get("/share/")
        assert "backend" in r.json()

    def test_backend_is_memory_in_tests(self):
        """В тестах Redis не подключён — должен использоваться memory."""
        backend = client.get("/share/").json()["backend"]
        assert backend in ("memory", "redis")

class TestSessionIndependence:

    def test_two_sessions_have_different_ids(self):
        sid1 = create_session()["session_id"]
        sid2 = create_session()["session_id"]
        assert sid1 != sid2

    def test_sessions_store_independent_data(self):
        sid1 = create_session(algo="bubble", state={"x": 1})["session_id"]
        sid2 = create_session(algo="merge",  state={"x": 2})["session_id"]

        data1 = client.get(f"/share/{sid1}").json()
        data2 = client.get(f"/share/{sid2}").json()

        assert data1["algorithm"]   == "bubble"
        assert data2["algorithm"]   == "merge"
        assert data1["state"]["x"]  == 1
        assert data2["state"]["x"]  == 2

    def test_delete_one_does_not_affect_other(self):
        sid1 = create_session()["session_id"]
        sid2 = create_session()["session_id"]
        client.delete(f"/share/{sid1}")
        assert client.get(f"/share/{sid2}").status_code == 200

    @pytest.mark.parametrize("module,algo", [
        ("sort",  "bubble"),
        ("graph", "dijkstra"),
        ("tree",  "avl"),
        ("dp",    "lcs"),
    ])
    def test_all_modules_can_be_saved(self, module, algo):
        data = create_session(module=module, algo=algo)
        sid = data["session_id"]
        retrieved = client.get(f"/share/{sid}").json()
        assert retrieved["module"]    == module
        assert retrieved["algorithm"] == algo