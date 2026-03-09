const form = document.getElementById('todo-form');
const input = document.getElementById('todo-input');
const list = document.getElementById('todo-list');
const itemsLeft = document.getElementById('items-left');
const clearBtn = document.getElementById('clear-completed');
const filterBtns = document.querySelectorAll('.filter-btn');

let todos = JSON.parse(localStorage.getItem('todos') || '[]');
let filter = 'all';

function save() {
  localStorage.setItem('todos', JSON.stringify(todos));
}

function render() {
  const visible = todos.filter(t => {
    if (filter === 'active') return !t.done;
    if (filter === 'completed') return t.done;
    return true;
  });

  list.innerHTML = '';

  if (visible.length === 0) {
    list.innerHTML = '<li class="empty-state">No tasks here!</li>';
  } else {
    visible.forEach(todo => {
      const li = document.createElement('li');
      li.className = 'todo-item' + (todo.done ? ' completed' : '');
      li.dataset.id = todo.id;

      li.innerHTML = `
        <input type="checkbox" ${todo.done ? 'checked' : ''} aria-label="Toggle task" />
        <span class="text">${escapeHtml(todo.text)}</span>
        <button class="delete-btn" aria-label="Delete task">&times;</button>
      `;

      li.querySelector('input').addEventListener('change', () => toggle(todo.id));
      li.querySelector('.delete-btn').addEventListener('click', () => remove(todo.id));

      list.appendChild(li);
    });
  }

  const active = todos.filter(t => !t.done).length;
  itemsLeft.textContent = `${active} item${active !== 1 ? 's' : ''} left`;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function addTodo(text) {
  todos.push({ id: Date.now(), text: text.trim(), done: false });
  save();
  render();
}

function toggle(id) {
  const todo = todos.find(t => t.id === id);
  if (todo) todo.done = !todo.done;
  save();
  render();
}

function remove(id) {
  todos = todos.filter(t => t.id !== id);
  save();
  render();
}

form.addEventListener('submit', e => {
  e.preventDefault();
  const text = input.value.trim();
  if (text) {
    addTodo(text);
    input.value = '';
  }
});

clearBtn.addEventListener('click', () => {
  todos = todos.filter(t => !t.done);
  save();
  render();
});

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filter = btn.dataset.filter;
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  });
});

render();
