import pytest
from pipelines.connectors.lever import LeverConnector

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        import httpx
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://test")
            raise httpx.HTTPStatusError("Error", request=request, response=self)

class MockClient:
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def get(self, url, **kwargs):
        if "fail" in url:
            return MockResponse({}, 404)
        return MockResponse([
            {
                "text": "Data Analyst",
                "id": "L456",
                "country": "LK",
                "categories": {
                    "team": "Analytics",
                    "location": "Colombo, Sri Lanka",
                    "commitment": "Full-time"
                },
                "createdAt": 1723555555000
            }
        ])

@pytest.fixture
def connector(monkeypatch):
    import httpx
    monkeypatch.setattr(httpx, "Client", MockClient)
    return LeverConnector("lever_test", {"boards": ["testboard"]})

def test_lever_fetch_success(connector):
    jobs = connector.fetch()
    assert len(jobs) == 1
    assert jobs[0]["text"] == "Data Analyst"
    assert jobs[0]["_board_source"] == "testboard"

def test_lever_fetch_404(connector):
    connector.boards = ["failboard"]
    jobs = connector.fetch()
    assert len(jobs) == 0

def test_lever_normalize(connector):
    raw = [{
        "_board_source": "testboard",
        "text": "Data Analyst",
        "id": "L456",
        "country": "LK",
        "categories": {
            "team": "Analytics",
            "location": "Colombo, Sri Lanka",
            "commitment": "Full-time"
        },
        "createdAt": 1723555555000
    }]
    norm = connector.normalize(raw)
    assert len(norm) == 1
    assert norm[0]["job_id"] == "lever_testboard_L456"
    assert norm[0]["source"] == "Lever"
    assert norm[0]["company"] == "testboard"
    assert norm[0]["country"] == "Sri Lanka"
    assert norm[0]["role_category"] == "Data & Analytics"
