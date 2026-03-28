"""IP Ranges service — fetches and filters AWS IP prefix data."""

from typing import Any

import httpx

AWS_IP_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"
DEFAULT_REGION = "us-east-1"
DEFAULT_SERVICE = "EC2"


async def fetch_ip_ranges(url: str = AWS_IP_RANGES_URL) -> dict[str, Any]:
    """Download the raw AWS IP ranges JSON."""
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_filtered_ip_ranges(
    region: str = DEFAULT_REGION,
    service: str = DEFAULT_SERVICE,
    url: str = AWS_IP_RANGES_URL,
) -> dict[str, Any]:
    """Return IPv4 and IPv6 prefixes filtered by *region* and *service*.

    Args:
        region: AWS region identifier (default ``"us-east-1"``).
        service: AWS service name, case-insensitive (default ``"EC2"``).
        url: URL to fetch the raw IP ranges from.

    Returns:
        A dict with keys ``sync_token``, ``create_date``, ``region``,
        ``service``, ``ipv4_prefixes``, and ``ipv6_prefixes``.
    """
    raw = await fetch_ip_ranges(url)

    service_upper = service.upper()

    ipv4 = [
        p["ip_prefix"]
        for p in raw.get("prefixes", [])
        if p.get("region") == region and p.get("service") == service_upper
    ]

    ipv6 = [
        p["ipv6_prefix"]
        for p in raw.get("ipv6_prefixes", [])
        if p.get("region") == region and p.get("service") == service_upper
    ]

    return {
        "sync_token": raw.get("syncToken"),
        "create_date": raw.get("createDate"),
        "region": region,
        "service": service_upper,
        "ipv4_prefixes": ipv4,
        "ipv6_prefixes": ipv6,
        "ipv4_count": len(ipv4),
        "ipv6_count": len(ipv6),
    }
