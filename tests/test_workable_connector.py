import pytest
from pipelines.connectors.workable import WorkableConnector

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
        return MockResponse({
            "jobs": [
                {
                    "title": "Software Engineer",
                    "shortcode": "W123",
                    "country": "Sri Lanka",
                    "city": "Colombo",
                    "employment_type": "Full-time",
                    "department": "Engineering"
                }
            ]
        })

@pytest.fixture
def connector(monkeypatch):
    import httpx
    monkeypatch.setattr(httpx, "Client", MockClient)
    return WorkableConnector("workable_test", {"boards": ["testboard"]})

def test_workable_fetch_success(connector):
    jobs = connector.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    assert jobs[0]["_board_source"] == "testboard"

def test_workable_fetch_404(connector):
    connector.boards = ["failboard"]
    jobs = connector.fetch()
    assert len(jobs) == 0

def test_workable_normalize(connector):
    raw = [{
        "_board_source": "testboard",
        "title": "Software Engineer",
        "shortcode": "W123",
        "country": "Sri Lanka",
        "city": "Colombo",
        "employment_type": "Full-time",
        "department": "Engineering"
    }]
    norm = connector.normalize(raw)
    assert len(norm) == 1
    assert norm[0]["job_id"] == "workable_testboard_W123"
    assert norm[0]["source"] == "Workable"
    assert norm[0]["company"] == "testboard"
    assert norm[0]["country"] == "Sri Lanka"
    assert norm[0]["role_category"] == "Software Engineering"
