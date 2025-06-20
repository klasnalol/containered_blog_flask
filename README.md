# Containerized Blog with Flask

This project is a small blog platform split into separate frontend and backend containers.
Two PostgreSQL databases store user accounts and blog posts. The services are orchestrated
with **Docker Compose**.

## Features

- User registration and login with session support
- Admin users can create and delete posts
- Regular users can add comments and upload images
- Theme toggle and animated transitions for a smoother UI
- HTTPS support (self-signed certificates are generated on startup)


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

4. Too post you need to be with admin tag, add it manualy in mydb to any account you created.

Stop everything with:

```bash
docker compose down
```

## Directory Structure

- `backend/` – Flask API implementation
- `frontend/` – static site served by Nginx
- `docker-compose.yml` – service definitions
- `README.md` – project documentation

Self‑signed HTTPS certificates are generated automatically when the frontend
container starts. The site is available on port **443** and any plain HTTP
requests are redirected to HTTPS.
Prometheus and Grafana are also served over HTTPS using separate Nginx proxies
that generate their own self‑signed certificates on startup.

## Downloading the Certificate

When the frontend container starts it creates `selfsigned.crt`. Visit the feed
page and use the **Download Certificate** link to grab the file. Import this
certificate into your operating system or browser trust store (Chrome:
`Settings › Privacy and security › Security › Manage certificates` → Authorities)
so the demo site is treated as trusted HTTPS.

## Monitoring with Prometheus and Grafana

The backend exposes Prometheus metrics at `/metrics`. Prometheus and Grafana are
included in the Compose stack so they start automatically when you run
`docker compose up`.

Prometheus loads `prometheus.yml` which already scrapes the backend and the
included Node Exporter container. Once everything is running:

1. Visit `https://localhost:9090` to view Prometheus targets and query metrics.
2. Visit `https://localhost:3000` to access Grafana (default credentials:
   `admin`/`admin`). Add Prometheus (available at `http://prometheus:9090`) as a
   data source and create a dashboard showing the `app_cpu_percent` and
   `app_memory_mb` metrics.

## CI/CD

GitHub Actions is configured in `.github/workflows/ci.yml`. Every push builds the
Docker images and runs a basic syntax check of the backend code.