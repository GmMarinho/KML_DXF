import pytest
import kml_processor.elev as elev

class MockResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

def test_get_elevations_ok(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(200, {"status": "OK", "results": [
            {"elevation": 100.0}, {"elevation": 200.0}
        ]})
    monkeypatch.setattr("requests.get", mock_get)
    points = [(-21.78, -46.57), (-21.79, -46.58)]
    result = elev.get_elevations(points, batch_size=2)
    print(f"\n[TEST] Elevações retornadas (OK): {result}")
    assert result == [100.0, 200.0]

def test_get_elevations_5xx_retry(monkeypatch):
    calls = []
    def mock_get(*args, **kwargs):
        calls.append(1)
        if len(calls) < 3:
            return MockResponse(500)
        return MockResponse(200, {"status": "OK", "results": [{"elevation": 123.4}]})
    monkeypatch.setattr("requests.get", mock_get)
    points = [(-21.78, -46.57)]
    result = elev.get_elevations(points, batch_size=1, max_retries=3)
    print(f"\n[TEST] Elevações após retry (5xx): {result}, tentativas: {len(calls)}")
    assert result == [123.4]
    assert len(calls) == 3

def test_get_elevations_4xx(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(404)
    monkeypatch.setattr("requests.get", mock_get)
    points = [(-21.78, -46.57)]
    result = elev.get_elevations(points, batch_size=1)
    print(f"\n[TEST] Elevações para erro 4xx: {result}")
    assert result == [None]
