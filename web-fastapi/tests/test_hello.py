import pytest


@pytest.mark.anyio
async def test_hello(client):
    response = await client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello FastAPI"}
