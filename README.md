# Multi-Vendor SDN Controller

### Network Automation Platform with NETCONF Protocol Implementation

A production-grade Software-Defined Networking (SDN) controller that automates network device configuration across multi-vendor environments. This project demonstrates modern network automation practices, protocol-level implementation expertise, and full-stack development capabilities.

---

## Overview

This SDN controller eliminates manual CLI-based network configuration by leveraging industry-standard **NETCONF protocol** and **YANG data models**. Built with a three-tier architecture, it provides a RESTful API and web-based UI for managing network devices from multiple vendors through a unified interface.

**Key capabilities:**
- Automates device discovery and capability negotiation across heterogeneous network environments
- Reduces interface configuration time from minutes to seconds through programmatic NETCONF operations
- Provides vendor-agnostic device management using IETF standard YANG models (ietf-interfaces, ietf-ip)
- Enables offline development and testing through custom NETCONF device simulators

---

## Technology Stack

### Backend & Network Protocol Layer

- **Python 3.11** - Core application logic and network orchestration
- **Flask 3.x** - RESTful API server with CORS support
- **ncclient 0.7.0** - NETCONF protocol client library (RFC 6241 compliant)
- **paramiko 4.x** - SSH transport layer for secure NETCONF sessions
- **PyYAML 6.x** - Device inventory and configuration management

### Frontend

- **React 19** - Modern component-based user interface
- **Vite 7** - Fast build tooling and development server
- **Tailwind CSS 4** - Utility-first responsive design system

### DevOps & Infrastructure

- **Docker & Docker Compose** - Multi-container orchestration for development and testing
- **pytest 9.x** - End-to-end integration testing framework
- **Custom NETCONF Simulators** - Protocol-compliant test infrastructure for CI/CD

### Protocols & Standards

- **NETCONF** (Network Configuration Protocol) - RFC 6241
- **YANG Data Models** - ietf-interfaces, ietf-ip modules
- **SSH Subsystem Architecture** - Secure transport for NETCONF messages
- **XML-based RPC** - Remote procedure call messaging between client and devices

---

## Key Features

### Network Device Lifecycle Management

- **Automated Discovery**: Connects to all devices in inventory via NETCONF protocol
- **Capability Negotiation**: Retrieves and parses NETCONF capabilities for each device
- **Multi-Vendor Support**: Vendor-agnostic approach using standard YANG models

### Configuration Management

- **Dynamic Interface Configuration**: Programmatically configure IP addressing and subnet masks
- **Running Configuration Retrieval**: Fetch and parse current device state using NETCONF get-config
- **XML Configuration Templating**: Generate YANG-compliant configuration from user input

### Monitoring & Status

- **Real-Time Device Polling**: On-demand status retrieval for network devices
- **NETCONF Capability Enumeration**: Display supported features and YANG models
- **Interface State Tracking**: Monitor enabled/disabled status and IP assignments
- **Error Detection**: Comprehensive error handling for network failures and timeouts

### Developer Experience

- **RESTful API**: Three well-defined endpoints for device operations
- **Docker-Based Environment**: One-command setup for development and testing
- **Offline Testing**: Custom NETCONF simulators enable development without physical hardware
- **Comprehensive Test Suite**: E2E tests covering discovery, configuration, and error scenarios

---

## Architecture Overview

### Three-Tier Architecture

```
┌──────────────────────┐
│   React Frontend     │  ← User Interface Layer (Port 3000)
│  (Device Dashboard)  │     - Device discovery UI
│                      │     - Configuration management
└──────────┬───────────┘     - Real-time status display
           │
           │ REST API (JSON over HTTP)
           │
┌──────────▼───────────┐
│   Flask Backend      │  ← Application Layer (Port 5000)
│  (SDN Controller)    │     - API endpoints
│                      │     - Business logic
└──────────┬───────────┘     - Device orchestration
           │
           │ NETCONF over SSH
           │
┌──────────▼───────────┐
│  Network Devices     │  ← Device Layer
│  (Routers/Switches)  │     - NETCONF-enabled devices
│   or Simulators      │     - YANG model support
└──────────────────────┘
```

### Backend Components

**NetconfClient** ([netconf_client.py](server/app/netconf_client.py))
- Low-level protocol abstraction for NETCONF operations
- Manages SSH connection lifecycle and session state
- Operations: `connect()`, `get_capabilities()`, `get_config()`, `edit_config()`, `commit()`, `close()`
- Error handling for RPC failures and network timeouts

**SDNController** ([controller.py](server/app/controller.py))
- High-level orchestration logic coordinating device operations
- Device inventory management from YAML configuration
- Key methods:
  - `discover_devices()` - Connects to all inventory devices and retrieves capabilities
  - `get_device_status()` - Fetches running configuration and parses interface data
  - `configure_interface()` - Pushes interface configuration changes via NETCONF
- XML parsing with namespace handling for YANG model data extraction

**API Routes** ([routes.py](server/app/routes.py))
- RESTful endpoint definitions with request validation
- JSON serialization/deserialization for API contracts
- Error handling and HTTP status code management

**Device Inventory** ([devices.yaml](server/inventory/devices.yaml))
- YAML-based configuration for device credentials and metadata
- Environment-specific inventories (local vs. Docker)
- Fields: hostname, IP, port, username, password, vendor, description

### Custom NETCONF Simulator

Built custom NETCONF device simulators ([router.py](server/simulator/router.py), [switch.py](server/simulator/switch.py)) to enable development without physical hardware:

- **Paramiko-based SSH server** implementing NETCONF subsystem
- **NETCONF 1.0 protocol compliance** (RFC 6241) with proper framing (`]]>]]>`)
- **YANG model simulation** for ietf-interfaces and ietf-ip modules
- **RPC message handling** for get-config, edit-config, and commit operations
- **In-memory configuration store** simulating candidate and running datastores
- Enables rapid iteration and CI/CD testing without hardware dependencies

---

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local backend development)
- **Node.js 18+** (for frontend development)

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Multi-Vendor-SDN-Controller

# Start backend API and NETCONF simulators
cd server/docker
docker-compose up -d

# In a separate terminal, start the frontend
cd ../../client
npm install
npm run dev
```

Access the application at `http://localhost:3000`

The API server will be available at `http://localhost:5000`

**Docker Architecture:**
- **sdn-controller** container: Flask API server (port 5000)
- **netconf-simulator** container: Two simulated devices
  - Router simulator on port 8300
  - Switch simulator on port 8400
- **Bridge network**: Enables inter-container communication

### Local Development Setup

**Backend:**
```bash
cd server

# Install dependencies
pip install -r requirements.txt

# Start NETCONF simulators (in separate terminals)
python -m simulator.router
python -m simulator.switch

# Run the Flask API server
python run.py
```

**Frontend:**
```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## API Documentation

Base URL: `http://localhost:5000/api`

### 1. Discover Devices

Discovers and connects to all devices defined in the inventory.

**Endpoint:**
```http
POST /api/discover
```

**Response:**
```json
{
  "status": "success",
  "discovered": 2,
  "devices": [
    {
      "hostname": "router-01",
      "ip": "netconf-simulator",
      "port": 8300,
      "vendor": "generic",
      "description": "Simulated router for testing",
      "status": "connected",
      "capabilities": 6,
      "error": null
    },
    {
      "hostname": "switch-01",
      "ip": "netconf-simulator",
      "port": 8400,
      "vendor": "generic",
      "description": "Simulated switch for testing",
      "status": "connected",
      "capabilities": 6,
      "error": null
    }
  ]
}
```

### 2. Get Device Status

Retrieves detailed configuration and status for a specific device.

**Endpoint:**
```http
GET /api/<device_id>/status
```

**Example:**
```http
GET /api/router-01/status
```

**Response:**
```json
{
  "hostname": "router-01",
  "connection_success": true,
  "capabilities": [
    "urn:ietf:params:netconf:base:1.0",
    "urn:ietf:params:netconf:capability:candidate:1.0",
    "urn:ietf:params:netconf:capability:writable-running:1.0",
    "urn:ietf:params:xml:ns:yang:ietf-interfaces",
    "urn:ietf:params:xml:ns:yang:ietf-ip"
  ],
  "running_config": {
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "type": "ethernetCsmacd",
        "enabled": true,
        "ip": "192.168.1.1",
        "netmask": "255.255.255.0"
      },
      {
        "name": "GigabitEthernet0/1",
        "type": "ethernetCsmacd",
        "enabled": false
      }
    ]
  },
  "device_info": {
    "ip": "netconf-simulator",
    "port": 8300,
    "username": "admin",
    "password": "admin",
    "vendor": "generic",
    "description": "Simulated router for testing"
  }
}
```

### 3. Configure Interface

Configures IP addressing on a network interface via NETCONF edit-config operation.

**Endpoint:**
```http
POST /api/<device_id>/interface
Content-Type: application/json
```

**Request Body:**
```json
{
  "interface_name": "GigabitEthernet0/0",
  "ip_address": "192.168.10.1",
  "subnet_mask": "255.255.255.0"
}
```

**Example:**
```http
POST /api/router-01/interface
Content-Type: application/json

{
  "interface_name": "GigabitEthernet0/0",
  "ip_address": "192.168.10.1",
  "subnet_mask": "255.255.255.0"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Interface GigabitEthernet0/0 configured successfully",
  "hostname": "router-01",
  "configuration": {
    "interface": "GigabitEthernet0/0",
    "ip": "192.168.10.1",
    "netmask": "255.255.255.0"
  }
}
```

**Error Response (404):**
```json
{
  "status": "error",
  "message": "Device 'unknown-device' not found in inventory"
}
```

---

## Testing Approach

### End-to-End Integration Testing

The project includes comprehensive E2E tests that validate the entire workflow from API to NETCONF protocol layer.

**Test Coverage:**
- ✅ Device discovery with multiple devices
- ✅ NETCONF capability negotiation and parsing
- ✅ Configuration retrieval and XML-to-JSON parsing
- ✅ Interface configuration with validation
- ✅ Error handling (device not found, invalid parameters, connection failures)
- ✅ Concurrent device operations

**Test Infrastructure:**
- Tests run against live NETCONF simulators in Docker environment
- Validates API contracts, error handling, and data transformation
- Located in [tests/test_e2e.py](server/tests/test_e2e.py)

**Run Tests:**
```bash
cd server

# Start simulators first
python -m simulator.router &
python -m simulator.switch &

# Run Flask API server
python run.py &

# Execute test suite
pytest tests/ -v

# Stop background processes
pkill -f simulator
pkill -f run.py
```

**Custom Test Infrastructure Benefits:**
- Enables offline development without physical network equipment
- Provides consistent test environments for CI/CD pipelines
- Allows rapid iteration on protocol implementation
- Reduces test execution time and infrastructure costs

---


## Project Structure

```
Multi-Vendor-SDN-Controller/
├── server/                          # Backend application
│   ├── app/                         # Core Flask application
│   │   ├── __init__.py              # Package initialization
│   │   ├── app.py                   # Flask app factory with CORS
│   │   ├── routes.py                # REST API endpoint definitions
│   │   ├── controller.py            # SDN controller orchestration logic
│   │   └── netconf_client.py        # NETCONF protocol client abstraction
│   │
│   ├── simulator/                   # Custom NETCONF device simulators
│   │   ├── router.py                # Router simulator (port 8300)
│   │   └── switch.py                # Switch simulator (port 8400)
│   │
│   ├── inventory/                   # Device configuration files
│   │   ├── devices.yaml             # Local development inventory
│   │   └── devices.docker.yaml      # Docker environment inventory
│   │
│   ├── docker/                      # Container configuration
│   │   ├── Dockerfile.app           # Backend API container
│   │   ├── Dockerfile.simulator     # Simulator container
│   │   └── docker-compose.yml       # Multi-container orchestration
│   │
│   ├── tests/                       # Test suite
│   │   ├── test_e2e.py              # End-to-end integration tests
│   │   └── test_netconf_client.py   # Unit tests for NETCONF client
│   │
│   ├── requirements.txt             # Python dependencies
│   └── run.py                       # Application entry point
│
├── client/                          # Frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── LandingPage.jsx      # Device discovery dashboard
│   │   │   ├── DeviceCard.jsx       # Individual device summary card
│   │   │   └── DevicePage.jsx       # Device configuration modal
│   │   ├── App.jsx                  # Root React component
│   │   └── main.jsx                 # Application entry point
│   │
│   ├── public/                      # Static assets
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite build configuration
│   └── tailwind.config.js           # Tailwind CSS configuration
│
└── README.md                        # Project documentation
```

**Key Design Principles:**
- **Clean Separation**: Backend (server/) and frontend (client/) are completely decoupled
- **Environment Flexibility**: Separate configurations for local development vs. Docker
- **Test Infrastructure**: Custom simulators enable testing without hardware
- **Protocol Abstraction**: netconf_client.py provides clean interface to NETCONF operations
- **Orchestration Layer**: controller.py handles business logic separate from protocol details

---

<!-- ## Future Enhancements

### Scalability

- [ ] **Connection Pooling**: Maintain persistent NETCONF sessions for frequently accessed devices
- [ ] **Async Operation Processing**: Use Celery task queues for long-running configuration operations
- [ ] **Database Persistence**: Store device state history, configuration changes, and audit logs
- [ ] **Horizontal Scaling**: Stateless API design enables load balancing across multiple instances

### Features

- [ ] **Configuration Rollback Mechanism**: Implement NETCONF confirmed-commit for safe configuration changes
- [ ] **Multi-Device Bulk Operations**: Apply configuration templates across multiple devices simultaneously
- [ ] **Network Topology Visualization**: Graph-based visualization of device interconnections
- [ ] **Real-Time Event Streaming**: Implement NETCONF notifications for device state changes
- [ ] **Configuration Templates**: YANG-based templates for common network configurations
- [ ] **Diff Comparison**: Visual comparison between running and candidate configurations

### Security

- [ ] **Authentication and Authorization**: JWT-based API authentication with role-based access control
- [ ] **Encrypted Credential Storage**: Use HashiCorp Vault or similar for device credentials
- [ ] **Audit Logging**: Comprehensive logging of all configuration changes with user attribution
- [ ] **RBAC (Role-Based Access Control)**: Fine-grained permissions for device access and operations
- [ ] **SSH Host Key Verification**: Enable strict host key checking in production environments

### DevOps

- [ ] **Kubernetes Deployment**: Helm charts for cloud-native deployment
- [ ] **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- [ ] **Prometheus Metrics**: Export operational metrics for monitoring and alerting
- [ ] **Grafana Dashboards**: Visualization of device health, API performance, and system metrics
- [ ] **ELK Stack Integration**: Centralized logging for distributed system debugging
- [ ] **Health Check Endpoints**: Kubernetes-ready liveness and readiness probes
 -->
