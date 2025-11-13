# LiveKit Configuration for TrendKe

## Docker Compose Setup (Self-hosted)

```yaml
version: '3.8'

services:
  livekit:
    image: livekit/livekit-server:latest
    command: --config /etc/livekit.yaml
    ports:
      - "7880:7880"  # HTTP
      - "7881:7881"  # RTC
      - "7882:7882/udp"  # TURN/UDP
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml
    environment:
      - LIVEKIT_KEYS=${LIVEKIT_API_KEY}:${LIVEKIT_API_SECRET}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Configuration File (livekit.yaml)

```yaml
port: 7880
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
  
redis:
  address: redis:6379

keys:
  # Will be loaded from environment variables
  
room:
  empty_timeout: 300  # 5 minutes
  max_participants: 50

logging:
  level: info
```

## Running Locally

```bash
# 1. Create .env file
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# 2. Start services
docker-compose up -d

# 3. Access at ws://localhost:7880
```

## Production Deployment

### Railway
1. Create new project
2. Add Docker service
3. Configure environment variables
4. Deploy

### Render
1. Create new Web Service
2. Use Docker
3. Configure environment
4. Deploy
