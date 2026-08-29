# Architecture Documentation

This document describes the architecture and design decisions for the Google Find My Device Home Assistant integration.

## Overview

This repo holds the **Home Assistant custom integration**. It's one half of a
two-repo project: the integration talks over HTTP to a separate
**[google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api)**
REST API service (which wraps the GoogleFindMyTools library) - that service's
own architecture, including its in-browser VNC authentication subsystem, is
documented in its own repo.

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
                    │  (separate repo)   │
                    └────────────────────┘
```

Repo: github.com/EricFG82/google-find-my-device-rest-api

## Component Details

### Technology Stack
- **Platform**: Home Assistant
- **Language**: Python 3.11+
- **Integration Type**: Custom Component with Config Flow

### Design Decisions

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

### Architecture Layers

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

### Key Components

1. **Config Flow** (`config_flow.py`)
   - UI-based configuration
   - API connection validation
   - Unique ID management

2. **Coordinator** (`__init__.py`)
   - Centralized data fetching
   - Update scheduling
   - State management
   - Stale-device cleanup on setup/reload (removes devices the API no longer
     reports, e.g. after a tracker gets re-paired and issued a new ID)

3. **Sensor Platform** (`sensor.py`)
   - Battery level sensors (created only if/when `battery_level` data is available -
     currently always absent, since the API doesn't get this from Google today)
   - Last seen timestamp sensors
   - Device attributes
   - Entities are added dynamically via a coordinator listener as data becomes
     available, not all at once at setup

4. **Device Tracker Platform** (`device_tracker.py`)
   - GPS location tracking
   - Map integration
   - Zone detection
   - Same dynamic-add pattern as the sensor platform

### Data Flow

```
Timer (60s) → Coordinator → API Client → REST API (external service)
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

This integration is an HTTP client of the REST API - it doesn't import any of
its code, just calls these two endpoints. Full endpoint reference (including
`/health` and the authentication endpoints) lives in
[google-find-my-device-rest-api's ARCHITECTURE](https://github.com/EricFG82/google-find-my-device-rest-api)
docs.

### REST API Endpoints Used

#### GET /api/v1/devices
Returns a list of all devices with basic information.

**Response:**
```json
[
  {
    "device_id": "689a0735-0000-2f84-82f1-f403043a0b70",
    "name": "My Tracker",
    "device_type": "SPOT_DEVICE",
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
  "device_id": "689a0735-0000-2f84-82f1-f403043a0b70",
  "name": "My Tracker",
  "device_type": "SPOT_DEVICE",
  "model": "Fast Pair Model bbe0d0",
  "battery_level": null,
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

`device_type` is currently always `SPOT_DEVICE` in practice. `battery_level` is
currently always `null` - Google's Find My Device network doesn't expose a battery
percentage for these trackers in the reverse-engineered protocol the API uses.

## Performance Considerations

### Caching Strategy

- Update interval: 60 seconds
- Coordinator-based updates
- Shared data across entities

### Scalability

**Current Limitations:**
- Single Google account (on the API side)
- Polling-based updates
- No real-time notifications

**Future Improvements:**
- Webhook support for real-time updates
- Configurable update intervals

## Security Considerations

### Authentication

- This integration has no authentication of its own - it just calls the REST
  API's URL, so securing that connection (network placement, HTTPS/reverse
  proxy for remote access) is the REST API's concern, not this repo's.

### Data Privacy

- All data stays local (except the REST API's own calls to Google)
- No third-party services
- User controls all data

## Deployment Options

### Option 1: Manual copy into `custom_components/` (current)
- Copy this repo's `custom_components/google_find_my_device/` into
  Home Assistant's config directory, restart, add via the UI

### Option 2: HACS (planned)
- Not yet published to the Home Assistant Community Store

## Error Handling

- Entity unavailability on errors
- Coordinator retry logic
- User-friendly error messages

## Testing Strategy

- Integration testing in HA dev environment
- Manual testing with real devices
- Log analysis for issues

## Future Enhancements

1. **Actions**: Support for device actions (ring, lock)
2. **History**: Store location history
3. **Geofencing**: Advanced zone detection
4. **MQTT**: Alternative communication protocol
5. **Multi-account**: Support multiple Google accounts (needs matching support
   on the API side)
6. **HACS**: Publish to Home Assistant Community Store

## Maintenance

### Updating This Integration
1. Update version in manifest.json
2. Test with latest Home Assistant
3. Update documentation

## Monitoring

### Health Checks
- Home Assistant: Entity availability
- REST API health: see the API's own `/health` endpoint

### Logging
- Home Assistant: Integration logs in HA

## Troubleshooting

See [README.md](README.md#-troubleshooting)
for integration-specific troubleshooting, or
[google-find-my-device-rest-api](https://github.com/EricFG82/google-find-my-device-rest-api) for
REST API / authentication issues.
