# timeserver

Tiny self-hosted web app that returns a PNG showing the current time, day,
timezone, and a sun/moon indicator based on configured working hours.
Designed for embedding via `<img>` in an email signature / out-of-office
auto-reply.

## URL format

Put this in your email signature:

```
<img src="https://your-domain/time.png?tz=America/New_York&start=09:00&end=17:00" alt="local time">
```

When the image is fetched, the server issues a `302` redirect to the same URL
with an extra `&ts=<epoch>` parameter and strong `no-cache` headers. This
defeats most caching layers; some email proxies (notably Gmail's) still cache
for a short window.

## Routes

| Path | Behavior |
|------|----------|
| `GET /` | 404 |
| `GET /healthz` | `200 OK` body `ok` |
| `GET /helper.html` | URL builder UI with live preview |
| `GET /time.png?tz=&start=&end=` | 302 → same URL with `&ts=<epoch>` |
| `GET /time.png?tz=&start=&end=&ts=` | rendered PNG |
| `GET /time.html?tz=&start=&end=` | HTML fallback |

Bad / missing parameters return `400` with a plain-text body. In email,
clients render this as a broken-image icon.

## Local development

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
uvicorn app.main:app --reload
```

Open `http://localhost:8000/helper.html` to build URLs and preview.

## Docker

```sh
docker compose build
docker compose up -d
curl -I "http://localhost:8000/time.png?tz=America/New_York&start=09:00&end=17:00"
```

## Deployment (Traefik)

Edit `docker-compose.yml` and uncomment the Traefik label/network block,
substituting your domain. The service exposes port 8000 internally.
