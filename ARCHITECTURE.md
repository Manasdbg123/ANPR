# VisionTrack ANPR — Architecture

## Overview

VisionTrack ANPR is a production-grade AI-powered Automatic Number Plate Recognition platform. It processes live camera streams, uploaded videos, and images to detect vehicles, recognize license plates, track objects, and provide real-time intelligence through a modern dashboard.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│  Dashboard │ Live View │ Detections │ Analytics │ AI Agent  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST + WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend                          │
│  Auth │ Cameras │ Detections │ Analytics │ Alerts │ AI      │
└───┬──────────┬──────────────┬───────────────────────────────┘
    │          │              │
    ▼          ▼              ▼
PostgreSQL   Redis      ANPR Engine
                        ┌─────────────────────┐
                        │  Vehicle Detector    │
                        │  Plate Detector      │
                        │  Preprocessor        │
                        │  OCR Engine          │
                        │  Validator           │
                        │  Tracker             │
                        │  Classifier          │
                        │  Event Processor     │
                        └─────────────────────┘
```

## Component Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                  # Application entry point
│   ├── config.py                # Pydantic settings
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # API router aggregation
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── cameras.py       # Camera CRUD + management
│   │       ├── detections.py    # Detection CRUD + search
│   │       ├── analytics.py     # Analytics endpoints
│   │       ├── alerts.py        # Alert rules + events
│   │       ├── system.py        # Health + system status
│   │       ├── ai.py            # AI assistant endpoints
│   │       └── uploads.py       # File upload handling
│   ├── core/
│   │   ├── security.py          # JWT, password hashing
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── exceptions.py        # Exception hierarchy
│   │   ├── middleware.py        # Logging, CORS, rate limiting
│   │   └── logging.py          # Structured logging setup
│   ├── models/
│   │   ├── base.py              # SQLAlchemy base
│   │   ├── user.py
│   │   ├── camera.py
│   │   ├── detection.py
│   │   ├── alert.py
│   │   └── system.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── camera.py
│   │   ├── detection.py
│   │   ├── analytics.py
│   │   ├── alert.py
│   │   └── common.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── camera_service.py
│   │   ├── detection_service.py
│   │   ├── analytics_service.py
│   │   ├── alert_service.py
│   │   └── ai_service.py
│   ├── vision/
│   │   ├── detection/
│   │   │   ├── base.py          # Detector protocol
│   │   │   └── yolo_detector.py # YOLO implementation
│   │   ├── plate/
│   │   │   ├── detector.py      # Plate detection
│   │   │   └── validator.py     # Indian plate validation
│   │   ├── ocr/
│   │   │   ├── base.py          # OCR protocol
│   │   │   ├── paddleocr_engine.py
│   │   │   └── easyocr_engine.py
│   │   ├── preprocessing/
│   │   │   └── pipeline.py      # Image preprocessing
│   │   ├── tracking/
│   │   │   └── tracker.py       # Multi-object tracking
│   │   ├── classification/
│   │   │   └── classifier.py    # Vehicle classification
│   │   └── pipeline/
│   │       ├── anpr_pipeline.py # Full ANPR pipeline
│   │       └── event_processor.py
│   ├── workers/
│   │   ├── camera_worker.py     # Camera stream processing
│   │   └── video_worker.py      # Video file processing
│   ├── websocket/
│   │   └── manager.py           # WebSocket connection manager
│   └── database/
│       ├── session.py           # Database session
│       └── redis.py             # Redis client
├── alembic/
├── tests/
├── requirements.txt
└── Dockerfile
```

### Frontend (Next.js)

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 # Landing page
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   └── (dashboard)/
│       ├── layout.tsx           # Dashboard layout with sidebar
│       ├── dashboard/
│       ├── cameras/
│       ├── detections/
│       ├── analytics/
│       ├── alerts/
│       ├── ai-assistant/
│       └── settings/
├── components/
│   ├── ui/                      # shadcn/ui components
│   ├── layout/                  # Sidebar, Header, etc.
│   ├── dashboard/               # Dashboard widgets
│   ├── cameras/                 # Camera components
│   ├── detections/              # Detection table/detail
│   ├── charts/                  # Chart components
│   └── common/                  # Shared components
├── lib/
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Auth utilities
│   ├── websocket.ts             # WebSocket client
│   └── utils.ts
├── hooks/
├── types/
├── public/
└── Dockerfile
```

## Data Flow

### Real-Time Processing Pipeline

```
Camera/Video Source
       │
       ▼
Frame Capture (OpenCV)
       │
       ▼
Frame Queue (asyncio / Redis)
       │
       ▼
Vehicle Detection (YOLOv8)
       │
       ▼
Multi-Object Tracking (SORT/ByteTrack)
       │
       ▼
Plate Detection (YOLO plate model)
       │
       ▼
Plate Preprocessing (OpenCV pipeline)
       │
       ▼
OCR (PaddleOCR / EasyOCR)
       │
       ▼
Plate Validation + Normalization
       │
       ▼
Duplicate Suppression (Redis TTL)
       │
       ▼
Event Processor → PostgreSQL
       │
       ▼
Redis Pub/Sub → WebSocket → Frontend
```

### Authentication Flow

```
Client → POST /api/v1/auth/login
       → JWT access token (short-lived, 30min)
       → Refresh token (long-lived, 7 days)
       → RBAC middleware on protected routes
```

## Database Schema (Core Entities)

| Entity | Purpose |
|--------|---------|
| User | Authentication, roles |
| Camera | Camera configuration |
| DetectionEvent | Vehicle detection records |
| PlateRecognition | OCR results linked to detections |
| AlertRule | User-defined alert conditions |
| AlertEvent | Triggered alerts |
| ProcessingJob | Video upload processing |

## Key Design Decisions

1. **Vision engine is decoupled from FastAPI** — can run independently for testing/batch processing
2. **Redis for ephemeral state** — duplicate suppression, camera status, pub/sub; PostgreSQL for durable storage
3. **Protocol-based abstractions** — detector, OCR, classifier use Python protocols for swappability
4. **Event-driven architecture** — detections flow through pub/sub to WebSocket clients
5. **Configurable preprocessing** — multiple strategies evaluated when OCR confidence is low
6. **Indian plate validation** — configurable regex patterns for state codes, district codes, plate formats
7. **Demo mode** — clearly separated from production, uses synthetic data when no cameras available

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, Pydantic v2 |
| Database | PostgreSQL 16, SQLAlchemy 2.x, Alembic |
| Cache | Redis 7 |
| CV | OpenCV, PyTorch, Ultralytics YOLOv8 |
| OCR | PaddleOCR / EasyOCR |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Charts | Recharts |
| Animation | Framer Motion |
| Icons | Lucide React |
| Auth | JWT (PyJWT), bcrypt |
| Logging | structlog |
| Container | Docker, Docker Compose |

## Security Architecture

- JWT with short access token + refresh token rotation
- bcrypt password hashing (12 rounds)
- Role-based access: ADMIN, OPERATOR, VIEWER
- CORS whitelist
- Rate limiting on auth endpoints
- Input validation via Pydantic
- Parameterized SQL queries (SQLAlchemy ORM)
- File upload validation (MIME, size, extension)
- No secrets in code or Docker files
