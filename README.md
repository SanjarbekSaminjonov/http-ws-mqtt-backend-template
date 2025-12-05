# Django MQTT WebSocket Backend Template

### Django + MQTT (aiomqtt, EMQX) + WebSocket (Channels) + Celery + PostgreSQL + Redis

Universal backend template for IoT/MQTT projects with Celery task queue.

## 🎯 Core Components

- ✅ Django 5.2.9 (ASGI + Channels)
- ✅ MQTT Handler (aiomqtt, multi-worker, shared subscription)
- ✅ MQTT Publisher (queue-based, persistent connection)
- ✅ WebSocket (real-time updates)
- ✅ Celery (async tasks + periodic scheduler)
- ✅ PostgreSQL 16, Redis, EMQX 5.8.8
- ✅ Docker Compose (development & production)

## 🏗️ Architecture

```
MQTT Devices → EMQX Broker → MQTT Handlers (shared subscription)
                                ↓
                            PostgreSQL + Channel Layer
                                ↓
                            WebSocket Clients (owners/admins)

Django Views/Celery → mqtt_publisher (Redis queue) → MQTT Publisher Client → EMQX → Devices

Celery Beat → Periodic Tasks → mqtt_publisher (Redis queue) → MQTT Publisher Client → EMQX → Devices
```

## 🚀 Quick Start

### Development (Local Django + Docker Services)

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env

# 3. Start third-party services only
docker compose -f docker-compose.thirdparty.yml up -d

# 4. Run migrations
python manage.py migrate
python manage.py migrate django_celery_beat

# 5. Create superuser
python manage.py createsuperuser

# 6. Run Django locally
python manage.py runserver

# 7. Run MQTT handler (separate terminal)
python manage.py run_mqtt_handler --handler-id handler_local_1

# 8. Run MQTT publisher (separate terminal)
python manage.py run_mqtt_publisher --publisher-id publisher_local_1

# 9. Run Celery worker (separate terminal)
celery -A config worker -l INFO

# 10. Run Celery beat (separate terminal)
celery -A config beat -l INFO

# 11. Run Celery Flower (separate terminal)
celery -A config flower --port=5555
```

### Production (Full Docker Deployment)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env (set DEBUG=False)

# 2. Build and start all services
docker compose -f docker-compose.production.yml up -d --build

# 3. Create superuser
docker exec -it django_app python manage.py createsuperuser

# Services:
# - Django: http://localhost:8000
# - EMQX Dashboard: http://localhost:18083
# - Celery Flower: http://localhost:5555
```

### Docker Compose Files

**`docker-compose.thirdparty.yml`** - Development (only infrastructure):
- PostgreSQL
- Redis
- EMQX

**`docker-compose.production.yml`** - Production (full stack):
- PostgreSQL
- Redis  
- EMQX
- Django App
- MQTT Handler
- MQTT Publisher
- Celery Worker
- Celery Beat
- Celery Flower

## 📁 Project Structure

```
├── config/              # Django settings, ASGI, Celery
├── main/                # Main Django app
│   ├── models.py        # Add your models here
│   ├── tasks.py         # Celery tasks
│   └── views.py
├── mqtt_service/        # MQTT services
│   ├── handler_client.py      # MQTTHandlerClient (subscriber/handler)
│   ├── publisher_client.py    # MQTTPublisherClient (queue-based publisher)
│   ├── mqtt_publisher.py      # mqtt_publisher interface (Django API)
│   ├── handlers.py            # Message handlers (customize here)
│   └── management/commands/   # run_mqtt_handler, run_mqtt_publisher
├── websocket/           # WebSocket consumers
│   ├── consumers.py     # WebSocket logic
│   └── routing.py       # WebSocket routes
├── compose/             # Docker scripts
│   ├── django/          # Django container scripts
│   └── redis/           # Redis config
└── docker-compose.*.yml # Docker configurations
```

## 🔧 Configuration

### MQTT Settings (`.env`)

```env
MQTT_BROKER_HOST=localhost  # or 'emqx' in Docker
MQTT_BROKER_PORT=1883
EMQX_BACKEND_USERNAME=backend
EMQX_BACKEND_PASSWORD=your_password
```

### Celery Settings

```python
# config/settings.py
CELERY_BROKER_URL = redis://...  # Redis DB2
CELERY_RESULT_BACKEND = redis://...  # Redis DB3
```

## 💡 Usage Examples

### 1. Create Celery Task

```python
# main/tasks.py
from celery import shared_task

@shared_task
def process_device_data(device_id, data):
    # Your logic
    return result

# Call task
from main.tasks import process_device_data
process_device_data.delay(123, {"temp": 25})
```

### 2. Publish MQTT from Django (queue + persistent publisher)

```python
# views.py or tasks.py
from mqtt_service import mqtt_publisher

mqtt_publisher.publish("from_device/001/event", {"action": "start"}, qos=1)
```

### 3. Handle MQTT Messages

```python
# mqtt_service/handlers.py
async def handle_message(self, topic: str, payload: str, message):
    data = json.loads(payload)
    
    # Your routing logic
    if topic.startswith("device/"):
        serial = topic.split("/")[1]
        # Process device message
        
    # Send to WebSocket
    await self.send_to_websocket(topic, data)
```

### 4. WebSocket Connection (Frontend)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/connect/');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('MQTT Update:', data);
};
```

## 🔍 Monitoring

- **Django Admin**: http://localhost:8000/admin
- **EMQX Dashboard**: http://localhost:18083 (admin/public)
- **Celery Flower**: http://localhost:5555
- **Logs**: `docker compose logs -f [service_name]`

## 🧪 Testing

```bash
# Test MQTT handler (local)
python manage.py run_mqtt_handler --worker-id handler_test_1

# Test MQTT publisher (local)
python manage.py run_mqtt_publisher --publisher-id publisher_test_1

# Test Celery task
python manage.py shell
>>> from main.tasks import example_task
>>> result = example_task.delay("test")
>>> result.ready()
```

## 📦 Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Django | 8000 | Main application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache + Channel Layer + Celery |
| EMQX | 1883 | MQTT Broker |
| EMQX Dashboard | 18083 | MQTT Management UI |
| Celery Flower | 5555 | Task monitoring |

## 🛠️ Common Commands

```bash
# Development
python manage.py runserver
python manage.py run_mqtt_handler --handler-id handler_dev_1
celery -A config worker -l INFO
celery -A config beat -l INFO
celery -A config flower --port=5555

# Production
docker compose -f docker-compose.production.yml up -d
docker compose -f docker-compose.production.yml logs -f
docker compose -f docker-compose.production.yml down

# Infrastructure only
docker compose -f docker-compose.thirdparty.yml up -d
docker compose -f docker-compose.thirdparty.yml down
```

## 📝 Notes

- **MQTT Handlers**: Use shared subscription (`$share/handlers/{topic}`) for load balancing
- **MQTT Publishers**: Publish messages to topics as needed
- **WebSocket**: Admins get all updates, regular users get only their device updates
- **Celery**: Tasks stored in Redis DB2, results in DB3
- **Channel Layer**: Uses Redis DB0 for WebSocket messages
- **Cache**: Uses Redis DB1 for Django caching
