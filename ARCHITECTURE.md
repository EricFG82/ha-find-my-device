# Architecture Documentation

This document describes the architecture and design decisions for the Google Find My Device Home Assistant integration project.

## Overview

The project consists of two main components:

1. **REST API Service**: A Python FastAPI service that wraps the GoogleFindMyTools library
2. **Home Assistant Integration**: A custom component that consumes the REST API

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Google Find My Device Integration            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │ Config Flow  │  │   Sensors    │  │  Trackers  │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  │           │                │                 │        │  │
│  │           └────────────────┴─────────────────┘        │  │
│  │                          │                            │  │
│  │                   ┌──────▼──────┐                     │  │
│  │                   │ Coordinator │                     │  │
│  │                   └──────┬──────┘                     │  │
│  │                          │                            │  │
│  └──────────────────────────┼────────────────────────────┘  │
│                             │ HTTP/REST                     │
└─────────────────────────────┼─────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   REST API Service │
                    │     (FastAPI)      │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Device Service    │
                    │   (Caching Layer)  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ GoogleFindMyTools  │
                    │      Library       │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Google Find My    │
                    │   Device Network   │
                    └────────────────────┘
```

## Component Details

### 1. REST API Service

#### Technology Stack
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Deployment**: Docker

#### Design Decisions

**Why FastAPI?**
- Native async/await support for better performance
- Automatic OpenAPI documentation generation
- Type hints and validation with Pydantic
- Easy to test and maintain
- Better suited for API services than Flask

**Why Python?**
- GoogleFindMyTools is written in Python
- Direct integration without language barriers
- Rich ecosystem for API development
- Easy deployment with Docker

#### Architecture Layers

```
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │      API Endpoints            │  │
│  │  - GET /api/v1/devices        │  │
│  │  - GET /api/v1/devices/{id}   │  │
│  │  - GET /health                │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │      Device Service           │  │
│  │  - Caching (60s TTL)          │  │
│  │  - Data transformation        │  │
│  │  - Error handling             │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   GoogleFindMyTools Library   │  │
│  │  - Authentication             │  │
│  │  - API calls                  │  │
│  │  - Decryption                 │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### Key Features

1. **Caching**: 60-second cache to reduce API calls and improve performance
2. **Async Operations**: Non-blocking I/O for better concurrency
3. **Error Handling**: Comprehensive error handling with proper HTTP status codes
4. **Health Checks**: Built-in health check endpoint for monitoring
5. **Documentation**: Auto-generated OpenAPI/Swagger documentation

#### Data Flow

```
Request → FastAPI → Device Service → Cache Check
                                    ↓ (if miss)
                                    GoogleFindMyTools
                                    ↓
                                    Google API
                                    ↓
                                    Parse & Transform
                                    ↓
                                    Update Cache
                                    ↓
Response ← FastAPI ← Device Service ← Cached Data
```

### 2. Home Assistant Integration

#### Technology Stack
- **Platform**: Home Assistant
- **Language**: Python 3.11+
- **Integration Type**: Custom Component with Config Flow

#### Design Decisions

**Why Custom Component?**
- Full control over entity creation and updates
- Better user experience with UI configuration
- Native Home Assistant integration
- Proper device and entity registry integration

**Why Config Flow?**
- Modern Home Assistant standard
- User-friendly UI configuration
- No YAML editing required
- Better validation and error handling

#### Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│              Home Assistant Core                    │
│  ┌───────────────────────────────────────────────┐  │
│  │         Integration (__init__.py)             │  │
│  │  - Setup and initialization                   │  │
│  │  - API client creation                        │  │
│  │  - Coordinator setup                          │  │
│  └───────────┬───────────────────────────────────┘  │
│              │                                       │
│  ┌───────────▼───────────────────────────────────┐  │
│  │      Data Update Coordinator                  │  │
│  │  - Periodic updates (60s)                     │  │
│  │  - Data fetching and caching                  │  │
│  │  - Error handling                             │  │
│  └───────────┬───────────────────────────────────┘  │
│              │                                       │
│  ┌───────────┴───────────────────────────────────┐  │
│  │                                               │  │
│  ▼                                               ▼  │
│  ┌──────────────────┐              ┌──────────────┐│
│  │  Sensor Platform │              │   Tracker    ││
│  │  - Battery       │              │   Platform   ││
│  │  - Last Seen     │              │  - Location  ││
│  └──────────────────┘              └──────────────┘│
└─────────────────────────────────────────────────────┘
```

#### Key Components

1. **Config Flow** (`config_flow.py`)
   - UI-based configuration
   - API connection validation
   - Unique ID management

2. **Coordinator** (`__init__.py`)
   - Centralized data fetching
   - Update scheduling
   - State management

3. **Sensor Platform** (`sensor.py`)
   - Battery level sensors
   - Last seen timestamp sensors
   - Device attributes

4. **Device Tracker Platform** (`device_tracker.py`)
   - GPS location tracking
   - Map integration
   - Zone detection

#### Data Flow

```
Timer (60s) → Coordinator → API Client → REST API
                ↓
            Parse Data
                ↓
        Update Entities
                ↓
    ┌───────────┴───────────┐
    ▼                       ▼
Sensors                 Trackers
    ↓                       ↓
Home Assistant State Machine
```

## Communication Protocol

### REST API Endpoints

#### GET /api/v1/devices
Returns a list of all devices with basic information.

**Response:**
```json
[
  {
    "device_id": "abc123",
    "name": "My Tracker",
    "device_type": "TRACKER",
    "last_seen": "2024-01-15T10:30:00Z",
    "status": "ACTIVE"
  }
]
```

#### GET /api/v1/devices/{device_id}
Returns detailed information for a specific device.

**Response:**
```json
{
  "device_id": "abc123",
  "name": "My Tracker",
  "device_type": "TRACKER",
  "model": "ESP32",
  "battery_level": 85,
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 10.5,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "last_seen": "2024-01-15T10:30:00Z",
  "status": "ACTIVE"
}
```

## Performance Considerations

### Caching Strategy

**REST API Service:**
- Cache TTL: 60 seconds
- Cache invalidation: Time-based
- Cache scope: All devices

**Home Assistant:**
- Update interval: 60 seconds
- Coordinator-based updates
- Shared data across entities

### Scalability

**Current Limitations:**
- Single Google account
- Polling-based updates
- No real-time notifications

**Future Improvements:**
- Multi-account support
- Webhook support for real-time updates
- Configurable update intervals
- Rate limiting

## Security Considerations

### Authentication

**REST API:**
- No authentication (local-only deployment)
- Relies on network security
- Future: Add API key authentication

**Google Account:**
- OAuth2 authentication
- Credentials stored in `secrets.json`
- Encrypted communication with Google

### Data Privacy

- All data stays local (except Google API calls)
- No third-party services
- User controls all data

### Recommendations

1. Run on local network only
2. Use firewall rules to restrict access
3. Consider VPN for remote access
4. Keep `secrets.json` secure
5. Use HTTPS with reverse proxy for remote access

## Deployment Options

### Option 1: Docker (Recommended)
- Easy setup and updates
- Isolated environment
- Consistent across platforms

### Option 2: Local Python
- Direct installation
- Better for development
- More control over environment

### Option 3: Docker Compose with Home Assistant
- Single deployment
- Shared network
- Simplified management

## Error Handling

### REST API
- HTTP status codes for different errors
- Detailed error messages
- Logging for debugging

### Home Assistant
- Entity unavailability on errors
- Coordinator retry logic
- User-friendly error messages

## Testing Strategy

### REST API
- Unit tests for service layer
- Integration tests for endpoints
- Manual testing with curl/Postman

### Home Assistant
- Integration testing in HA dev environment
- Manual testing with real devices
- Log analysis for issues

## Future Enhancements

1. **Authentication**: Add API key support
2. **Webhooks**: Real-time updates instead of polling
3. **Actions**: Support for device actions (ring, lock)
4. **History**: Store location history
5. **Geofencing**: Advanced zone detection
6. **MQTT**: Alternative communication protocol
7. **Multi-account**: Support multiple Google accounts
8. **HACS**: Publish to Home Assistant Community Store

## Maintenance

### Updating GoogleFindMyTools
1. Update Docker image to pull latest version
2. Test API compatibility
3. Update integration if needed

### Updating Home Assistant Integration
1. Update version in manifest.json
2. Test with latest Home Assistant
3. Update documentation

## Monitoring

### Health Checks
- REST API: `/health` endpoint
- Docker: Built-in health check
- Home Assistant: Entity availability

### Logging
- REST API: Structured logging with levels
- Home Assistant: Integration logs in HA
- Docker: Container logs

## Troubleshooting

See individual README files for detailed troubleshooting:
- [REST API Troubleshooting](rest-api/README.md#troubleshooting)
- [Home Assistant Troubleshooting](homeassistant-integration/README.md#troubleshooting)

