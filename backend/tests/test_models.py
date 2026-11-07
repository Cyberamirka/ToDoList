from backend.app import models


def test_create_and_list_tasks(db_session):
    first = models.create_task(db_session, title="  A  ", description="  desc  ")
    second = models.create_task(db_session, title="B")

    assert first.id is not None
    assert first.title == "A"
    assert first.description == "desc"
    assert first.completed is False
    assert first.position == 0
    assert second.position == 1

    tasks = models.list_tasks(db_session)
    assert [task.id for task in tasks] == [first.id, second.id]


def test_get_task(db_session):
    created = models.create_task(db_session, title="Find me")
    found = models.get_task(db_session, created.id)
    missing = models.get_task(db_session, 99999)

    assert found is not None
    assert found.id == created.id
    assert missing is None


def test_update_task(db_session):
    task = models.create_task(db_session, title="Old", description="old")
    updated = models.update_task(
        db_session,
        task,
        title="  New  ",
        description="  next  ",
        completed=True,
    )

    assert updated.title == "New"
    assert updated.description == "next"
    assert updated.completed is True


def test_delete_task(db_session):
    task = models.create_task(db_session, title="Remove")
    task_id = task.id

    models.delete_task(db_session, task)

    assert models.get_task(db_session, task_id) is None
    assert models.list_tasks(db_session) == []


def test_reorder_tasks(db_session):
    first = models.create_task(db_session, title="One")
    second = models.create_task(db_session, title="Two")
    third = models.create_task(db_session, title="Three")

    reordered = models.reorder_tasks(db_session, [third.id, first.id, second.id])

    assert reordered is not None
    assert [task.id for task in reordered] == [third.id, first.id, second.id]
    assert [task.position for task in reordered] == [0, 1, 2]


def test_reorder_tasks_missing_id(db_session):
    task = models.create_task(db_session, title="Only")
    result = models.reorder_tasks(db_session, [task.id, 99999])

    assert result is None
    assert models.list_tasks(db_session)[0].position == 0
