# Django + MQTT + WebSocket + Celery — IoT backend template

Bu loyiha IoT qurilmalarni (MQTT orqali) boshqarish, fon (background) tasklar va real-time (WebSocket) eventlar uchun tayyor backend template.

## Stack

- Django 5.2 (ASGI) + Channels (WebSocket)
- EMQX 5.8 (MQTT broker)
- aiomqtt (MQTT client)
- Celery + django-celery-beat (async + schedule)
- PostgreSQL 16
- Redis (cache + channels layer + celery broker/result + MQTT publish queue)
- Docker Compose (infra/app alohida)

## Arxitektura (qisqa)

```
Qurilma -> EMQX -> MQTT Handler(lar) [$share/handlers/from_device/+/...] -> Django logic -> WebSocket

Django view/Celery -> Redis queue (mqtt:publish_queue) -> MQTT Publisher -> EMQX -> Qurilma (to_device/<username>)
```

## MQTT topiclar (default)

- Qurilma -> backend:
    - `from_device/<username>/status`
    - `from_device/<username>/event`
- Backend -> qurilma:
    - `to_device/<username>`

MQTT handler default qilib `$share/handlers/from_device/+/status` va `$share/handlers/from_device/+/event` ga subscribe bo‘ladi.

## Ishga tushirish (Docker)

### 1) `.env` tayyorlash

```bash
cp .env.example .env
```

Muhim:
- Docker ichida `POSTGRES_HOST=postgres`, `REDIS_HOST=redis`, `MQTT_BROKER_HOST=emqx` bo‘lishi kerak.
- `DJANGO_DEBUG=True` bo‘lsa container `runserver` bilan start bo‘ladi; aks holda `gunicorn` (ASGI/uvicorn worker) ishlaydi.

### 2) Infra servislarni ishga tushirish

```bash
make run_infra
```

Bu `postgres`, `redis`, `emqx` va `my_shared_network` ni ko‘taradi.

### 3) App servislarni ishga tushirish

```bash
make run_app
```

Bu quyidagilarni ko‘taradi:
- Django (`django-app`) — `http://localhost:8000`
- MQTT handler (`mqtt-handler-1`)
- MQTT publisher (`mqtt-publisher-1`)
- Celery worker/beat
- Flower — `http://localhost:5555`

### 4) Admin user ochish

```bash
docker exec -it django-app python manage.py createsuperuser
```

## Web UI orqali qurilma boshqarish (minimal flow)

Bu template’da Web UI uchun tayanchlar bor:

1) Qurilmalarni ro‘yxatdan o‘tkazish (Django Admin)
- `http://localhost:8000/admin/` ga kiring
- `Devices -> Devices` dan `username` va `password` bilan device yarating
    - admin forma parolni `password_hash + salt` ko‘rinishida saqlaydi

2) Real-time eventlar (WebSocket)
- WebSocket endpoint: `ws(s)://<host>/ws/connect/`
- Consumer faqat autentifikatsiyadan o‘tgan user’ni qabul qiladi (cookie session kerak).
- Backend’dan WS ga yuborish:
    - `src/websocket/utils/senders.py` dagi `websocket_sender` orqali

3) Qurilmaga buyruq yuborish (MQTT publish queue)
- Django kodidan (view/task) publish qilish:

```python
from apps.mqtt_service.mqtt_publisher import mqtt_publisher

mqtt_publisher.publish(
        topic="to_device/device_001",
        payload={"cmd": "reboot"},
        qos=1,
)
```

MQTT Publisher service Redis queue’dan olib, EMQX ga publish qiladi.

## Background tasklar (Celery)

- Namuna task: `src/apps/main/tasks.py` dagi `example_task`
- Beat scheduler: `django_celery_beat` (jadvalni admin paneldan boshqarasiz)

Misol:

```python
from apps.main.tasks import example_task
example_task.delay("Hello")
```

WebSocket’ga event yuborish misoli:

```python
from websocket.utils.senders import websocket_sender

websocket_sender.send_to_user(user_id=1, payload={"type": "device.event", "data": {"ok": True}})
```

## Monitoring va foydali URLlar

- Django: `http://localhost:8000/`
- Healthcheck: `http://localhost:8000/health/`
- Django Admin: `http://localhost:8000/admin/`
- EMQX Dashboard: `http://localhost:18083/` (`MQTT_ROOT_USERNAME`/`MQTT_ROOT_PASSWORD`)
- Flower: `http://localhost:5555/`

Loglar:

```bash
docker compose -p app -f docker-compose.app.yml logs -f
docker compose -p infra -f docker-compose.infra.yml logs -f emqx
```

## MQTT Auth/ACL haqida eslatma

- EMQX authentication 2 xil:
    - built-in database (dashboard/root user)
    - PostgreSQL (qurilmalar) — `devices_device` jadvalidan `password_hash` va `salt` ni o‘qiydi.
- ACL fayl: `compose/emqx/acl.conf`.
    - Qurilmalar default qilib faqat o‘z topiclariga publish qiladi (`from_device/<username>/...`) va o‘z command topic’iga subscribe qiladi (`to_device/<username>`).
    - Backend (handler/publisher) uchun kengroq ruxsat kerak bo‘lsa, ACL’ni loyihangiz talabiga ko‘ra yangilang.

## Make komandalar

```bash
make ls
make run_infra
make down_infra
make run_app
make down_app
```
