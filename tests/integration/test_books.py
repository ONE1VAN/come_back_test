import pytest

INVALID_BOOKS = [
    {"title": "", "genre": "fiction", "year": 2000, "author": {"first_name": "A", "last_name": "B"}},
    {"title": "T", "genre": "fiction", "year": 3000, "author": {"first_name": "A", "last_name": "B"}},
    {"title": "T", "genre": "fiction", "year": 1700, "author": {"first_name": "A", "last_name": "B"}},
    {"title": "T", "genre": "cooking", "year": 2000, "author": {"first_name": "A", "last_name": "B"}},
    {"title": "T", "genre": "fiction", "year": 2000},
]


async def test_create_then_get(client, auth_headers):
    payload = {
        "title": "Dune",
        "genre": "science",
        "year": 1965,
        "author": {"first_name": "Frank", "last_name": "Herbert"},
    }
    r = await client.post("/api/v1/books/", json=payload, headers=auth_headers)
    assert r.status_code == 201
    book_id = r.json()["id"]
    r2 = await client.get(f"/api/v1/books/{book_id}")
    assert r2.json()["author"]["lastName"] == "Herbert"


async def test_duplicate_returns_409(client, auth_headers):
    payload = {"title": "X", "genre": "fiction", "year": 2000, "author": {"first_name": "Jane", "last_name": "Y"}}
    await client.post("/api/v1/books/", json=payload, headers=auth_headers)
    r = await client.post("/api/v1/books/", json=payload, headers=auth_headers)
    assert r.status_code == 409


async def test_write_requires_auth(client):
    payload = {"title": "X", "genre": "fiction", "year": 2000, "author": {"first_name": "A", "last_name": "B"}}
    r = await client.post("/api/v1/books/", json=payload)
    assert r.status_code == 401


async def test_invalid_token_returns_401(client):
    payload = {"title": "T", "genre": "fiction", "year": 2000, "author": {"first_name": "A", "last_name": "B"}}
    headers = {"Authorization": "Bearer not-a-real-token"}
    r = await client.post("/api/v1/books/", json=payload, headers=headers)
    assert r.status_code == 401


@pytest.mark.parametrize("bad", INVALID_BOOKS)
async def test_create_invalid_returns_422(client, auth_headers, bad):
    r = await client.post("/api/v1/books/", json=bad, headers=auth_headers)
    assert r.status_code == 422
