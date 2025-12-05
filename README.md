# Django MQTT WebSocket Backend Template

Universal backend template for IoT/MQTT projects.

## 🎯 Core Components

- ✅ Django Backend
- ✅ MQTT Handler (async, multi-worker)
- ✅ MQTT Commander (publish from Django)
- ✅ WebSocket (real-time updates)
- ✅ PostgreSQL, Redis, EMQX
- ✅ Docker Compose

## 🏗️ Architecture

```
MQTT Device → EMQX Broker → MQTT Workers → PostgreSQL
                                ↓
                            Channel Layer (Redis)
                                ↓
                            WebSocket Clients

---------------------------------------------------

Websocket Clients → Channel Layer (Redis) → PostgreSQL
                                ↓
                            MQTT Commander
                                ↓
                            EMQX Broker
                                ↓
                            MQTT Device


---------------------------------------------------

Scheluled Tasks → MQTT Commander → EMQX Broker →
→ MQTT Device → EMQX Broker → MQTT Workers → PostgreSQL
                                ↓
                            Channel Layer (Redis)
                                ↓
                            WebSocket Clients
```

## 🚀 Quick Start

```bash
# Install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Edit .env with your settings

# Start infrastructure
docker compose up -d
```
