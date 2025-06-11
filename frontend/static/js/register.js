document.getElementById('regForm').addEventListener('submit', async e => {
  e.preventDefault();
  const msgEl = document.getElementById('message');
  msgEl.style.color = 'red';
  msgEl.textContent = 'Working…';

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch('http://localhost:5000/register', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username, password}),
    credentials: 'include'
  });
  const data = await res.json();
  msgEl.style.color = res.ok ? 'green' : 'red';
  msgEl.textContent = data.message;
});
