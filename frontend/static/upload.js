document.getElementById('uploadForm').addEventListener('submit', async e => {
  e.preventDefault();
  const msgEl = document.getElementById('msg');
  msgEl.style.color = 'red';
  msgEl.textContent = 'Uploading…';
  const form = document.getElementById('uploadForm');
  const fd = new FormData(form);
  const res = await fetch('http://localhost:5000/posts', {
    method: 'POST',
    credentials: 'include',
    body: fd
  });
  const data = await res.json();
  msgEl.style.color = res.ok ? 'green' : 'red';
  msgEl.textContent = data.message;
});
