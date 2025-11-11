# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2025-10-30

### Fixed

- **Dockerfile**: Replaced Google Chrome with Chromium for ARM64 compatibility
  - Issue: Google Chrome only provides amd64 packages, causing build failures on Apple Silicon Macs
  - Solution: Use Chromium which supports both amd64 and arm64 architectures
  - Impact: Docker build now works on Apple Silicon (M1/M2/M3) and Intel Macs
  - Added environment variables: `CHROME_BIN` and `CHROMEDRIVER_PATH`

## [1.0.1] - 2025-10-30

### Fixed

- **Dockerfile**: Fixed Google Chrome installation by replacing deprecated `apt-key` with modern GPG keyring method

  - Issue: `apt-key` command is no longer available in newer Debian/Ubuntu versions
  - Solution: Use `gpg --dearmor` and signed-by in sources.list
  - Impact: Docker build now works on all modern systems

- **docker-compose.yml**: Removed obsolete `version` attribute
  - Issue: Docker Compose v2 shows warning about obsolete version attribute
  - Solution: Removed `version: '3.8'` line
  - Impact: No more warnings during build/run

## [1.0.0] - 2025-10-30

### Added

- Initial release of Google Find My Device - Home Assistant Integration
- REST API Service with FastAPI
  - GET /api/v1/devices - List all devices
  - GET /api/v1/devices/{device_id} - Get device details
  - GET /health - Health check endpoint
  - Automatic API documentation (Swagger/ReDoc)
  - 60-second intelligent caching
  - Docker containerization
- Home Assistant Custom Integration
  - Device tracker entities (location on map)
  - Battery level sensors
  - Last seen timestamp sensors
  - UI-based configuration (Config Flow)
  - Coordinator pattern for efficient updates
- Comprehensive Documentation
  - README.md - Main project overview
  - QUICKSTART.md - Step-by-step setup guide
  - ARCHITECTURE.md - Technical architecture
  - PROJECT_SUMMARY.md - Complete project summary
  - Component-specific READMEs
  - Example configurations and automations
- Deployment Files
  - Dockerfile with health checks
  - docker-compose.yml for easy deployment
  - test_api.sh for API testing
  - .env.example for configuration
- License
  - GPL-3.0 license (matching GoogleFindMyTools)

### Technical Details

- Python 3.11+ with FastAPI
- Pydantic for data validation
- Async/await patterns throughout
- Thread pool executor for blocking calls
- Home Assistant coordinator pattern
- Proper error handling and logging

---

## Version History

- **1.0.2** (2025-10-30) - ARM64/Apple Silicon compatibility fix
- **1.0.1** (2025-10-30) - Docker build fixes
- **1.0.0** (2025-10-30) - Initial release
