"""FastAPI application entry-point."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.services.ip_ranges import (
    DEFAULT_REGION,
    DEFAULT_SERVICE,
    get_filtered_ip_ranges,
)

app = FastAPI(
    title="AWS IP Ranges API",
    description=(
        "REST API that fetches AWS IP ranges and filters them by region and service. "
        "By default returns EC2 prefixes for us-east-1 (North Virginia)."
    ),
    version="1.0.0",
)


@app.get("/health", summary="Health check")
async def health() -> JSONResponse:
    """Return a simple liveness response."""
    return JSONResponse({"status": "ok"})


@app.get(
    "/ip-ranges",
    summary="Get filtered AWS IP ranges",
    response_description="Filtered IPv4 and IPv6 prefix lists",
)
async def ip_ranges(
    region: str = Query(
        default=DEFAULT_REGION,
        description="AWS region identifier, e.g. us-east-1",
        examples=["us-east-1", "us-west-2", "eu-west-1"],
    ),
    service: str = Query(
        default=DEFAULT_SERVICE,
        description="AWS service name (case-insensitive), e.g. EC2, S3, CLOUDFRONT",
        examples=["EC2", "S3", "CLOUDFRONT"],
    ),
) -> JSONResponse:
    """Fetch and return AWS IP prefixes filtered by *region* and *service*.

    The data is sourced from
    ``https://ip-ranges.amazonaws.com/ip-ranges.json``.
    """
    try:
        data = await get_filtered_ip_ranges(region=region, service=service)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to retrieve AWS IP ranges: {exc}",
        ) from exc

    return JSONResponse(data)
