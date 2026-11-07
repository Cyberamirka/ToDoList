def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_empty(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Купить молоко", "description": "2 литра"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Купить молоко"
    assert data["description"] == "2 литра"
    assert data["completed"] is False
    assert data["position"] == 0


def test_create_task_requires_title(client):
    response = client.post("/api/tasks", json={"title": "", "description": "x"})
    assert response.status_code == 422


def test_update_task(client):
    created = client.post("/api/tasks", json={"title": "Старое", "description": ""}).json()

    response = client.patch(
        f"/api/tasks/{created['id']}",
        json={"title": "Новое", "description": "подробности", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новое"
    assert data["description"] == "подробности"
    assert data["completed"] is True


def test_update_task_empty_title(client):
    created = client.post("/api/tasks", json={"title": "Есть", "description": ""}).json()
    response = client.patch(f"/api/tasks/{created['id']}", json={"title": "   "})
    assert response.status_code == 422
    assert response.json()["detail"] == "Title cannot be empty"


def test_update_missing_task(client):
    response = client.patch("/api/tasks/99999", json={"completed": True})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task(client):
    created = client.post("/api/tasks", json={"title": "Удалить", "description": ""}).json()

    response = client.delete(f"/api/tasks/{created['id']}")
    assert response.status_code == 204

    listed = client.get("/api/tasks")
    assert listed.json() == []


def test_delete_missing_task(client):
    response = client.delete("/api/tasks/99999")
    assert response.status_code == 404


def test_reorder_tasks(client):
    first = client.post("/api/tasks", json={"title": "A", "description": ""}).json()
    second = client.post("/api/tasks", json={"title": "B", "description": ""}).json()
    third = client.post("/api/tasks", json={"title": "C", "description": ""}).json()

    response = client.put(
        "/api/tasks/reorder",
        json={"task_ids": [third["id"], first["id"], second["id"]]},
    )
    assert response.status_code == 200
    data = response.json()
    assert [task["id"] for task in data] == [third["id"], first["id"], second["id"]]
    assert [task["position"] for task in data] == [0, 1, 2]


def test_reorder_missing_task(client):
    created = client.post("/api/tasks", json={"title": "A", "description": ""}).json()
    response = client.put(
        "/api/tasks/reorder",
        json={"task_ids": [created["id"], 99999]},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "One or more tasks were not found"


def test_full_flow_persists_across_requests(client):
    client.post("/api/tasks", json={"title": "One", "description": "1"})
    client.post("/api/tasks", json={"title": "Two", "description": "2"})

    tasks = client.get("/api/tasks").json()
    assert len(tasks) == 2

    client.patch(f"/api/tasks/{tasks[0]['id']}", json={"completed": True})
    client.delete(f"/api/tasks/{tasks[1]['id']}")

    remaining = client.get("/api/tasks").json()
    assert len(remaining) == 1
    assert remaining[0]["title"] == "One"
    assert remaining[0]["completed"] is True
