import pytest
from httpx import ASGITransport, AsyncClient

from loredeck.main import create_app


@pytest.mark.integration
@pytest.mark.asyncio
async def test_readiness_check_returns_database_status() -> None:
    application = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=application),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "available",
    }
