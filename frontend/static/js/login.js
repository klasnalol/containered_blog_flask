document.getElementById('loginForm').addEventListener('submit', async e => {
  e.preventDefault();
  const msgEl = document.getElementById('msg');
  msgEl.textContent = 'Working…';

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    credentials: 'include',
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  msgEl.style.color = res.ok ? 'green' : 'red';
  msgEl.textContent = data.message;
  if (res.ok) setTimeout(() => window.location = '/', 800);
});
