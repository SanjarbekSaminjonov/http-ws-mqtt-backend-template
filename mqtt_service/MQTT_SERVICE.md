# MQTT Service for Gate Management

## Overview

MQTT service async ravishda ishlovchi, multi-worker qo'llab-quvvatlovchi message handler service.

## Asosiy xususiyatlari

1. **Async MQTT Client** - `aiomqtt` kutubxonasidan foydalanadi
2. **Django ORM Integration** - `asgiref.sync.sync_to_async` orqali
3. **Shared Subscription** - Multi-worker setup da duplicate message oldini oladi
4. **Auto-reconnect** - Broker bilan aloqa uzilsa avtomatik qayta ulanadi
5. **Django Channels Integration** - WebSocket clientlarga real-time xabar yuborish

## Qanday ishlaydi?

### Shared Subscription

EMQX broker da shared subscription format:
```
$share/{group_name}/{topic}
```

Misol:
- Topic: `gate/gate_001/status`
- Shared: `$share/gate_workers/gate/gate_001/status`

Bu formatda har bir message faqat **bitta workerga** keladi (load balancing).

### Architecture

```
EMQX Broker
    ↓ (shared subscription)
    ├── MQTT Worker 1 → Django ORM → PostgreSQL
    ├── MQTT Worker 2 → Django ORM → PostgreSQL
    └── MQTT Worker N → Django ORM → PostgreSQL
```

## Foydalanish

### 1. Django Management Command orqali

```bash
# Single worker
python manage.py run_mqtt_service

# Custom worker ID bilan
python manage.py run_mqtt_service --worker-id worker_1
```

### 2. Standalone Runner orqali

```bash
python mqtt_service/runner.py
```

### 3. Docker Compose orqali (tavsiya etiladi)

```bash
docker compose up mqtt_worker_1 mqtt_worker_2
```

## Message Handler

`mqtt_service/handlers.py` da message handlerlarni yozish:

```python
async def handle_gate_status(self, topic: str, data: dict):
    # Extract gate_id from topic
    parts = topic.split("/")
    gate_id = parts[1]
    
    # Django ORM (sync_to_async bilan)
    await self.update_gate_status_db(gate_id, data)
    
    # WebSocket ga yuborish
    await self.channel_layer.group_send(
        f"gate_{gate_id}",
        {"type": "gate.status", "data": data}
    )

@sync_to_async
def update_gate_status_db(self, gate_id: str, data: dict):
    from main.models import Gate
    gate = Gate.objects.get(gate_id=gate_id)
    gate.status = data.get('status')
    gate.save()
```

## Testing

MQTT message yuborish:

```bash
# mosquitto_pub orqali
mosquitto_pub -h localhost -p 1883 -t "gate/gate_001/status" -m '{"status": "open"}'

# Python orqali
import asyncio
import aiomqtt

async def publish():
    async with aiomqtt.Client("localhost") as client:
        await client.publish("gate/gate_001/status", '{"status": "open"}')

asyncio.run(publish())
```

## Scaling

Worker sonini oshirish:

```yaml
# docker-compose.yml
mqtt_worker_3:
  build: .
  container_name: mqtt_worker_3
  command: python manage.py run_mqtt_service --worker-id worker_3
  environment:
    - MQTT_WORKER_ID=worker_3
```

Shared subscription orqali barcha workerlar bitta group da bo'lib, har bir message faqat bitta workerga keladi.

## Monitoring

Loglarni ko'rish:

```bash
# Specific worker
docker logs -f mqtt_worker_1

# All workers
docker compose logs -f mqtt_worker_1 mqtt_worker_2
```

## Dependencies

- `aiomqtt==2.4.0` - Async MQTT client
- `Django` - ORM va management commands
- `channels` - WebSocket integration
- `asgiref` - Async/sync bridge
