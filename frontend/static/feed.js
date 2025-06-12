let isAdmin = false;
async function fetchMe() {
  const res = await fetch('http://localhost:5000/me', { credentials: 'include' });
  if (!res.ok) return;
  const data = await res.json();
  isAdmin = data.is_admin;
}
async function loadFeed() {
  await fetchMe();
  const res = await fetch('http://localhost:5000/feed', { credentials: 'include' });
  const posts = await res.json();
  const feedEl = document.getElementById('feed');
  feedEl.innerHTML = '';
  if (!posts.length) {
    feedEl.textContent = 'No posts yet.';
    return;
  }
  posts.forEach(p => {
    const div = document.createElement('div');
    div.classList.add('post');
    div.innerHTML = `
      <h2>${p.title}</h2>
      <p><em>by ${p.author} on ${new Date(p.created_at).toLocaleString()}</em></p>
      ${p.image_url ? `<img src="http://localhost:5000${p.image_url}" style="max-width:300px;" />` : ''}
      <p>${p.content}</p>
      <h3>Comments</h3>
      <div>${p.comments.map(c => `
          <p><strong>${c.author}</strong> (${new Date(c.created_at).toLocaleString()}): ${c.content}</p>
        `).join('')}</div>
      <form data-postid="${p.id}" class="commentForm">
        <input name="content" placeholder="Add a comment" required />
        <button type="submit">Comment</button>
      </form>
      ${isAdmin ? `<button class="deleteBtn" data-postid="${p.id}">Delete Post</button>` : ''}
      <hr/>
    `;
    feedEl.appendChild(div);
  });
  document.querySelectorAll('.commentForm').forEach(form => {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const postId = form.dataset.postid;
      const content = form.content.value;
      const resp = await fetch(`http://localhost:5000/posts/${postId}/comments`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        credentials: 'include',
        body: JSON.stringify({content})
      });
      if (resp.ok) loadFeed();
      else alert((await resp.json()).message);
    });
  });
  document.querySelectorAll('.deleteBtn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Delete this post?')) return;
      const postId = btn.dataset.postid;
      const resp = await fetch(`http://localhost:5000/posts/${postId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      alert((await resp.json()).message);
      if (resp.ok) loadFeed();
    });
  });
}
loadFeed();
