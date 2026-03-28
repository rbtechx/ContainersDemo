"""Tests for the IP ranges API."""

import json

import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.main import app

AWS_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"

MOCK_PAYLOAD = {
    "syncToken": "1234567890",
    "createDate": "2024-01-01-00-00-00",
    "prefixes": [
        {
            "ip_prefix": "3.80.0.0/12",
            "region": "us-east-1",
            "service": "EC2",
            "network_border_group": "us-east-1",
        },
        {
            "ip_prefix": "52.2.0.0/15",
            "region": "us-east-1",
            "service": "EC2",
            "network_border_group": "us-east-1",
        },
        {
            "ip_prefix": "52.94.0.0/22",
            "region": "us-east-1",
            "service": "S3",
            "network_border_group": "us-east-1",
        },
        {
            "ip_prefix": "13.32.0.0/15",
            "region": "eu-west-1",
            "service": "EC2",
            "network_border_group": "eu-west-1",
        },
    ],
    "ipv6_prefixes": [
        {
            "ipv6_prefix": "2600:1f18::/36",
            "region": "us-east-1",
            "service": "EC2",
            "network_border_group": "us-east-1",
        },
        {
            "ipv6_prefix": "2a05:d07c::/32",
            "region": "eu-west-1",
            "service": "EC2",
            "network_border_group": "eu-west-1",
        },
    ],
}

client = TestClient(app)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /ip-ranges — default params (us-east-1 / EC2)
# ---------------------------------------------------------------------------


@respx.mock
def test_ip_ranges_default():
    respx.get(AWS_URL).mock(
        return_value=Response(200, content=json.dumps(MOCK_PAYLOAD).encode())
    )

    response = client.get("/ip-ranges")

    assert response.status_code == 200
    data = response.json()

    assert data["region"] == "us-east-1"
    assert data["service"] == "EC2"
    assert "3.80.0.0/12" in data["ipv4_prefixes"]
    assert "52.2.0.0/15" in data["ipv4_prefixes"]
    # S3 prefix should not be present
    assert "52.94.0.0/22" not in data["ipv4_prefixes"]
    # eu-west-1 prefix should not be present
    assert "13.32.0.0/15" not in data["ipv4_prefixes"]
    assert data["ipv4_count"] == 2

    assert "2600:1f18::/36" in data["ipv6_prefixes"]
    assert data["ipv6_count"] == 1

    assert data["sync_token"] == "1234567890"
    assert data["create_date"] == "2024-01-01-00-00-00"


# ---------------------------------------------------------------------------
# /ip-ranges — custom region & service
# ---------------------------------------------------------------------------


@respx.mock
def test_ip_ranges_custom_region_service():
    respx.get(AWS_URL).mock(
        return_value=Response(200, content=json.dumps(MOCK_PAYLOAD).encode())
    )

    response = client.get("/ip-ranges?region=eu-west-1&service=EC2")

    assert response.status_code == 200
    data = response.json()

    assert data["region"] == "eu-west-1"
    assert data["service"] == "EC2"
    assert "13.32.0.0/15" in data["ipv4_prefixes"]
    assert data["ipv4_count"] == 1


@respx.mock
def test_ip_ranges_service_case_insensitive():
    """Service parameter should be normalised to upper-case."""
    respx.get(AWS_URL).mock(
        return_value=Response(200, content=json.dumps(MOCK_PAYLOAD).encode())
    )

    response = client.get("/ip-ranges?region=us-east-1&service=ec2")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "EC2"
    assert data["ipv4_count"] == 2


# ---------------------------------------------------------------------------
# /ip-ranges — upstream failure results in 502
# ---------------------------------------------------------------------------


@respx.mock
def test_ip_ranges_upstream_error():
    respx.get(AWS_URL).mock(return_value=Response(500))

    response = client.get("/ip-ranges")

    assert response.status_code == 502
    assert "Failed to retrieve" in response.json()["detail"]
