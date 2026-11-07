# Taskboard — Список задач

Простое веб-приложение To-Do List: FastAPI + SQLite (SQLAlchemy) на бэкенде и чистый HTML/CSS/JS на фронтенде.

## Возможности

- добавление задач (модальное окно с названием и описанием)
- отметка выполненных задач
- редактирование и удаление
- изменение порядка задач перетаскиванием
- сохранение в SQLite — данные переживают обновление страницы и перезапуск контейнера

## Стек

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Запуск:** Docker Compose, образ `python:3.12-alpine` (один сервис отдаёт API и статику)

## Быстрый старт

```bash
docker compose up --build
```

Откройте [http://localhost:8000](http://localhost:8000).

База SQLite хранится в `./data/todos.db` (volume).

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/tasks` | Список задач |
| POST | `/api/tasks` | Создать задачу |
| PATCH | `/api/tasks/{id}` | Обновить задачу |
| DELETE | `/api/tasks/{id}` | Удалить задачу |
| PUT | `/api/tasks/reorder` | Сохранить новый порядок |

## Тесты backend

```bash
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pytest
```

Покрыты CRUD в `models.py` и HTTP API (`/api/health`, create/list/update/delete/reorder + ошибки 404/400/422).

## AI-инструменты

Проект собран в **Cursor** (Composer). История запросов — в `AI_LOG.md`.
