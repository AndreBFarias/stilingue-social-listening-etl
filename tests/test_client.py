import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import requests

from src.api.client import HTTPClient, RetryableHTTPError

FIXTURES = Path(__file__).parent / "fixtures" / "mock_responses"


def _mock_config():
    mock = MagicMock()
    mock.BASE_URL = "https://api.stilingue.com.br"
    mock.API_TOKEN = "123456789"
    mock.REQUEST_TIMEOUT = 60
    return mock


def _load_fixture(name: str) -> dict:
    with open(FIXTURES / f"{name}.json") as f:
        return json.load(f)


def _mock_response_ok(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


def _mock_response_status(status_code: int) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status.side_effect = requests.HTTPError(f"{status_code} Server Error")
    return mock


@patch("src.api.client.config", _mock_config())
def test_build_url():
    client = HTTPClient()
    url = client._build_url("visao_geral")
    assert url == "https://api.stilingue.com.br/wrapi/visao_geral/123456789"
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_sucesso():
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    mock_response = _mock_response_ok(mock_data)

    with patch.object(client._session, "get", return_value=mock_response):
        result = client.get("visao_geral", params={"date_range": "1d"})

    assert result["collected_mentions"] == 9875
    assert result["general_sentiment"]["negative_value"] == 4500
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_timeout_retry():
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    mock_response_ok = _mock_response_ok(mock_data)

    with patch.object(
        client._session,
        "get",
        side_effect=[requests.Timeout("timeout"), mock_response_ok],
    ):
        result = client.get("visao_geral")

    assert result["collected_mentions"] == 9875
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_5xx_retry():
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    resp_500 = _mock_response_status(500)
    resp_ok = _mock_response_ok(mock_data)

    with patch.object(
        client._session,
        "get",
        side_effect=[resp_500, resp_ok],
    ):
        result = client.get("visao_geral")

    assert result["collected_mentions"] == 9875
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_5xx_exaure_retries():
    client = HTTPClient()
    resp_502 = _mock_response_status(502)

    with patch.object(client._session, "get", return_value=resp_502):
        with pytest.raises(RetryableHTTPError):
            client.get("visao_geral")

    client.close()


@patch("src.api.client.config", _mock_config())
@patch("src.api.client.time.sleep")
def test_get_429_retry(mock_sleep):
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    resp_429 = _mock_response_status(429)
    resp_429.status_code = 429
    resp_ok = _mock_response_ok(mock_data)

    with patch.object(
        client._session,
        "get",
        side_effect=[resp_429, resp_ok],
    ):
        result = client.get("visao_geral")

    mock_sleep.assert_any_call(30)
    assert result["collected_mentions"] == 9875
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_503_retry():
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    resp_503 = _mock_response_status(503)
    resp_503.status_code = 503
    resp_ok = _mock_response_ok(mock_data)

    with patch.object(
        client._session,
        "get",
        side_effect=[resp_503, resp_ok],
    ):
        result = client.get("visao_geral")

    assert result["collected_mentions"] == 9875
    client.close()


@patch("src.api.client.config", _mock_config())
def test_get_connection_error_retry():
    client = HTTPClient()
    mock_data = _load_fixture("visao_geral")
    resp_ok = _mock_response_ok(mock_data)

    with patch.object(
        client._session,
        "get",
        side_effect=[requests.ConnectionError("conn refused"), resp_ok],
    ):
        result = client.get("visao_geral")

    assert result["collected_mentions"] == 9875
    client.close()
