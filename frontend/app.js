const API = "/api/tasks";

const taskListEl = document.getElementById("task-list");
const emptyStateEl = document.getElementById("empty-state");
const taskCountEl = document.getElementById("task-count");
const openCreateBtn = document.getElementById("open-create");
const modalEl = document.getElementById("task-modal");
const modalTitleEl = document.getElementById("modal-title");
const modalSubmitEl = document.getElementById("modal-submit");
const formEl = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const descriptionInput = document.getElementById("task-description");
const toastEl = document.getElementById("toast");

let tasks = [];
let editingId = null;
let dragId = null;
let toastTimer = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Ошибка запроса";
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "Ошибка запроса");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function showToast(message) {
  toastEl.textContent = message;
  toastEl.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastEl.hidden = true;
  }, 2400);
}

function pluralTasks(count) {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return `${count} задача`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} задачи`;
  return `${count} задач`;
}

function render() {
  taskListEl.innerHTML = "";
  emptyStateEl.hidden = tasks.length > 0;
  taskCountEl.textContent = tasks.length
    ? `${pluralTasks(tasks.length)} · перетащите за ручку слева, чтобы менять порядок`
    : "Список пуст";

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = `task-item${task.completed ? " completed" : ""}`;
    li.dataset.id = String(task.id);
    li.draggable = true;

    li.innerHTML = `
      <div class="task-row">
        <button type="button" class="drag-handle" aria-label="Перетащить задачу" title="Перетащить">
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" focusable="false">
            <circle cx="4" cy="3" r="1.3" fill="currentColor"/>
            <circle cx="10" cy="3" r="1.3" fill="currentColor"/>
            <circle cx="4" cy="7" r="1.3" fill="currentColor"/>
            <circle cx="10" cy="7" r="1.3" fill="currentColor"/>
            <circle cx="4" cy="11" r="1.3" fill="currentColor"/>
            <circle cx="10" cy="11" r="1.3" fill="currentColor"/>
          </svg>
        </button>
        <input class="task-check" type="checkbox" ${task.completed ? "checked" : ""} aria-label="Отметить выполненной" />
        <p class="task-title"></p>
        <div class="task-actions">
          <button type="button" class="btn-small edit-btn">Изменить</button>
          <button type="button" class="btn-small btn-danger delete-btn">Удалить</button>
        </div>
      </div>
      <p class="task-description" hidden></p>
    `;

    li.querySelector(".task-title").textContent = task.title;
    const descEl = li.querySelector(".task-description");
    if (task.description) {
      descEl.hidden = false;
      descEl.textContent = task.description;
    }

    li.querySelector(".task-check").addEventListener("change", async (event) => {
      const completed = event.target.checked;
      try {
        const updated = await api(`${API}/${task.id}`, {
          method: "PATCH",
          body: JSON.stringify({ completed }),
        });
        tasks = tasks.map((item) => (item.id === task.id ? updated : item));
        render();
      } catch (error) {
        event.target.checked = !completed;
        showToast(error.message);
      }
    });

    li.querySelector(".edit-btn").addEventListener("click", () => openModal(task));
    li.querySelector(".delete-btn").addEventListener("click", () => deleteTask(task.id));

    li.addEventListener("dragstart", (event) => {
      dragId = task.id;
      li.classList.add("dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", String(task.id));
    });

    li.addEventListener("dragend", () => {
      dragId = null;
      li.classList.remove("dragging");
      taskListEl.querySelectorAll(".drag-over").forEach((el) => el.classList.remove("drag-over"));
    });

    li.addEventListener("dragover", (event) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
      li.classList.add("drag-over");
    });

    li.addEventListener("dragleave", () => {
      li.classList.remove("drag-over");
    });

    li.addEventListener("drop", async (event) => {
      event.preventDefault();
      li.classList.remove("drag-over");
      const sourceId = Number(event.dataTransfer.getData("text/plain") || dragId);
      const targetId = task.id;
      if (!sourceId || sourceId === targetId) return;

      const fromIndex = tasks.findIndex((item) => item.id === sourceId);
      const toIndex = tasks.findIndex((item) => item.id === targetId);
      if (fromIndex < 0 || toIndex < 0) return;

      const next = [...tasks];
      const [moved] = next.splice(fromIndex, 1);
      next.splice(toIndex, 0, moved);
      tasks = next;
      render();

      try {
        tasks = await api(`${API}/reorder`, {
          method: "PUT",
          body: JSON.stringify({ task_ids: next.map((item) => item.id) }),
        });
        render();
      } catch (error) {
        showToast(error.message);
        await loadTasks();
      }
    });

    taskListEl.appendChild(li);
  }
}

function openModal(task = null) {
  editingId = task ? task.id : null;
  modalTitleEl.textContent = task ? "Изменить задачу" : "Новая задача";
  modalSubmitEl.textContent = task ? "Сохранить" : "Добавить";
  titleInput.value = task ? task.title : "";
  descriptionInput.value = task ? task.description || "" : "";
  modalEl.hidden = false;
  titleInput.focus();
}

function closeModal() {
  modalEl.hidden = true;
  editingId = null;
  formEl.reset();
}

async function loadTasks() {
  try {
    tasks = await api(API);
    render();
  } catch (error) {
    taskCountEl.textContent = "Не удалось загрузить";
    showToast(error.message);
  }
}

async function deleteTask(id) {
  const confirmed = window.confirm("Удалить эту задачу?");
  if (!confirmed) return;

  try {
    await api(`${API}/${id}`, { method: "DELETE" });
    tasks = tasks.filter((task) => task.id !== id);
    render();
    showToast("Задача удалена");
  } catch (error) {
    showToast(error.message);
  }
}

openCreateBtn.addEventListener("click", () => openModal());

modalEl.querySelectorAll("[data-close]").forEach((el) => {
  el.addEventListener("click", closeModal);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modalEl.hidden) {
    closeModal();
  }
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: titleInput.value.trim(),
    description: descriptionInput.value.trim(),
  };

  if (!payload.title) {
    showToast("Введите название задачи");
    return;
  }

  modalSubmitEl.disabled = true;
  try {
    if (editingId) {
      const updated = await api(`${API}/${editingId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      tasks = tasks.map((task) => (task.id === editingId ? updated : task));
      showToast("Задача обновлена");
    } else {
      const created = await api(API, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      tasks = [...tasks, created];
      showToast("Задача добавлена");
    }
    closeModal();
    render();
  } catch (error) {
    showToast(error.message);
  } finally {
    modalSubmitEl.disabled = false;
  }
});

loadTasks();
