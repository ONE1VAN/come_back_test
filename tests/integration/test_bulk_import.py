import json


def _json_file(rows: list[dict]) -> dict:
    return {"file": ("books.json", json.dumps(rows), "application/json")}


AUTHOR = {"first_name": "Zed", "last_name": "Q"}


async def test_bulk_all_valid_inserts(client, auth_headers):
    rows = [
        {"title": "Dune", "genre": "science", "year": 1965, "author": {"first_name": "Frank", "last_name": "Herbert"}},
        {
            "title": "Dune Messiah",
            "genre": "science",
            "year": 1969,
            "author": {"first_name": "Frank", "last_name": "Herbert"},
        },
        {
            "title": "Foundation",
            "genre": "science",
            "year": 1951,
            "author": {"first_name": "Isaac", "last_name": "Asimov"},
        },
    ]
    r = await client.post("/api/v1/books/bulk", files=_json_file(rows), headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["inserted"] == 3

    listed = (await client.get("/api/v1/books/?limit=100")).json()
    assert len(listed) == 3


async def test_bulk_duplicate_file_returns_409(client, auth_headers):
    rows = [{"title": "A", "genre": "fiction", "year": 2001, "author": AUTHOR}]
    await client.post("/api/v1/books/bulk", files=_json_file(rows), headers=auth_headers)
    r = await client.post("/api/v1/books/bulk", files=_json_file(rows), headers=auth_headers)
    assert r.status_code == 409


async def test_bulk_one_bad_row_inserts_nothing(client, auth_headers):
    rows = [
        {"title": "Good", "genre": "fiction", "year": 2001, "author": AUTHOR},
        {"title": "", "genre": "fiction", "year": 2001, "author": AUTHOR},
    ]
    r = await client.post("/api/v1/books/bulk", files=_json_file(rows), headers=auth_headers)
    assert r.status_code == 422
    assert len(r.json()["errors"]) == 1
    assert (await client.get("/api/v1/books/?title=Good")).json() == []
