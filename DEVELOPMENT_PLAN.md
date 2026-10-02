# VisionTrack ANPR — Development Plan

## Phase 1: Project Foundation ✅
- [x] Repository inspection
- [x] ARCHITECTURE.md
- [x] DEVELOPMENT_PLAN.md
- [x] TODO.md
- [x] Project directory structure
- [x] .env.example
- [x] .gitignore

## Phase 2: Backend Foundation
- [ ] FastAPI application skeleton
- [ ] Pydantic settings / configuration
- [ ] Structured logging (structlog)
- [ ] Exception hierarchy + error handling
- [ ] Database session (SQLAlchemy 2.x async)
- [ ] Redis client
- [ ] Health check endpoint
- [ ] CORS middleware
- [ ] Request ID middleware

## Phase 3: Authentication
- [ ] User model + migration
- [ ] Password hashing (bcrypt)
- [ ] JWT access/refresh tokens
- [ ] Login / register / refresh endpoints
- [ ] Role-based access control (ADMIN, OPERATOR, VIEWER)
- [ ] Auth dependencies for FastAPI

## Phase 4: Vision Engine
- [ ] Vehicle detector (YOLO) with protocol
- [ ] Plate detector
- [ ] Preprocessing pipeline (resize, grayscale, CLAHE, threshold, sharpen)
- [ ] OCR engine protocol + EasyOCR/PaddleOCR implementation
- [ ] Indian plate validator
- [ ] Character correction
- [ ] Vehicle classifier (type, color)
- [ ] Multi-object tracker (SORT-based)
- [ ] Duplicate suppression

## Phase 5: ANPR Pipeline
- [ ] Integrated pipeline: frame → detect → track → plate → OCR → validate → event
- [ ] Performance measurement
- [ ] Configurable parameters
- [ ] Demo mode with sample data

## Phase 6: Camera & Processing
- [ ] Camera model + CRUD
- [ ] Camera worker (RTSP, webcam)
- [ ] Video upload processing
- [ ] Image processing endpoint
- [ ] Frame management
- [ ] Camera health monitoring

## Phase 7: Data & Events
- [ ] Detection event model + persistence
- [ ] Redis pub/sub for real-time events
- [ ] WebSocket manager
- [ ] Event aggregation
- [ ] Search + filtering

## Phase 8: Frontend — Core
- [ ] Next.js project setup
- [ ] Tailwind + shadcn/ui
- [ ] Layout (sidebar, header)
- [ ] Auth pages (login/register)
- [ ] API client
- [ ] WebSocket client
- [ ] Theme (dark/light)

## Phase 9: Frontend — Pages
- [ ] Landing page
- [ ] Dashboard
- [ ] Live cameras
- [ ] Detection history + detail
- [ ] Analytics
- [ ] Alerts
- [ ] AI Assistant
- [ ] Settings / System Health

## Phase 10: AI Assistant
- [ ] Tool-based agent architecture
- [ ] search_detections, get_statistics tools
- [ ] Natural language → structured query
- [ ] RAG knowledge base
- [ ] Streaming responses
- [ ] Chat UI

## Phase 11: Alerts & Analytics
- [ ] Alert rules CRUD
- [ ] Alert event generation
- [ ] Analytics aggregation endpoints
- [ ] Time-range filtering

## Phase 12: Testing
- [ ] Backend unit tests
- [ ] Vision pipeline tests
- [ ] API integration tests
- [ ] Auth tests
- [ ] Frontend component tests

## Phase 13: Docker & Deployment
- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile
- [ ] docker-compose.yml
- [ ] docker-compose.dev.yml
- [ ] GPU support configuration

## Phase 14: Polish & Documentation
- [ ] README.md
- [ ] API.md
- [ ] UI visual refinement pass
- [ ] Loading/error/empty states
- [ ] Responsive design pass
- [ ] Final quality audit
