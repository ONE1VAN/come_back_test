async def test_register_login_refresh_flow(client):
    creds = {"username": "uuu", "email": "u@u.io", "password": "password123"}
    payload = {"title": "T", "genre": "fiction", "year": 2000, "author": {"first_name": "A", "last_name": "B"}}

    r = await client.post("/api/v1/auth/register", json=creds)
    assert r.status_code == 201
    tokens = r.json()

    headers = {"Authorization": f"Bearer {tokens['accessToken']}"}
    assert (await client.post("/api/v1/books/", json=payload, headers=headers)).status_code == 201

    assert (await client.post("/api/v1/auth/login", json=creds)).status_code == 200

    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refreshToken"]})
    assert r.status_code == 200
    new_headers = {"Authorization": f"Bearer {r.json()['accessToken']}"}
    payload2 = {**payload, "title": "T2", "year": 2001}
    assert (await client.post("/api/v1/books/", json=payload2, headers=new_headers)).status_code == 201

    bad = {"Authorization": f"Bearer {tokens['refreshToken']}"}
    assert (await client.post("/api/v1/books/", json=payload, headers=bad)).status_code == 401


async def test_login_wrong_password_returns_401(client):
    creds = {"username": "aaa", "email": "a@a.io", "password": "password123"}
    await client.post("/api/v1/auth/register", json=creds)
    r = await client.post("/api/v1/auth/login", json={"email": "a@a.io", "password": "wrong-password"})
    assert r.status_code == 401


async def test_login_unknown_email_returns_401(client):
    r = await client.post("/api/v1/auth/login", json={"email": "nobody@x.io", "password": "password123"})
    assert r.status_code == 401


async def test_register_duplicate_email_returns_409(client):
    creds = {"username": "bbb", "email": "b@b.io", "password": "password123"}
    assert (await client.post("/api/v1/auth/register", json=creds)).status_code == 201
    dup = {"username": "ccc", "email": "b@b.io", "password": "password123"}
    r = await client.post("/api/v1/auth/register", json=dup)
    assert r.status_code == 409


async def test_register_invalid_returns_422(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": "x", "email": "not-an-email", "password": "123"},
    )
    assert r.status_code == 422
