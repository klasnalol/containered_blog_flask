# Containerized Blog with Flask

This project is a small blog platform split into separate frontend and backend containers.
Two PostgreSQL databases store user accounts and blog posts. The services are orchestrated
with **Docker Compose**.

## Features

- User registration and login with session support
- Admin users can create and delete posts
- Regular users can add comments and upload images
- Theme toggle and animated transitions for a smoother UI
- HTTPS support via included self‑signed certificates

## Quick Start

1. Ensure Docker and Docker Compose are installed.
2. Build and start the stack:

   ```bash
   docker compose up --build
   ```

3. Visit `https://localhost` (or `http://localhost`) in your browser.
   The frontend runs on Nginx and connects to the Flask backend API.

Use the **Register** page to create an account, log in, and start posting.
Uploaded images are stored in the `uploads` volume.

Stop everything with:

```bash
docker compose down
```

## Directory Structure

- `backend/` – Flask API implementation
- `frontend/` – static site served by Nginx
- `docker-compose.yml` – service definitions
- `README.md` – project documentation

HTTPS certificates are located in `frontend/selfsigned.crt` and
`frontend/selfsigned.key`. They are copied into the frontend image so the
site can be accessed securely on port **443**.
