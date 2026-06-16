from unittest.mock import MagicMock, patch


from src.modules.cld.test_connection import validate_cloud_endpoint


@patch("src.modules.cld.test_connection.requests.get")
def test_validate_cloud_endpoint_success(mock_get):
    mock_resp = MagicMock()
    mock_get.return_value = mock_resp

    result = validate_cloud_endpoint("http://example.com")

    assert result is True
    mock_resp.raise_for_status.assert_called_once()
