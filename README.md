# VisionTrack ANPR 🚗⚡

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.3-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

> **Real-Time Vehicle Intelligence & Automatic Number Plate Recognition Platform**  
> Powered by YOLO, EasyOCR, Multi-Object Tracking, FastAPI, Next.js, and an integrated Natural Language AI Query Assistant.

---

## 📌 Overview

**VisionTrack ANPR** is an end-to-end, production-ready computer vision platform built for high-accuracy vehicle tracking and license plate detection. Designed to operate on live RTSP camera streams, pre-recorded video feeds, and uploaded imagery, VisionTrack pairs deep learning inference with an intuitive web operations console and an automated AI analytics assistant.

It specifically includes optimized recognition algorithms and character-correction heuristics for **Indian standard license plates (MORTH)** while remaining fully extensible to global formats.

---

## ✨ Key Features

### 🧠 Computer Vision & Deep Learning Engine
- **Two-Stage Detection:** YOLO vehicle detection + high-resolution plate localization crops.
- **Advanced Preprocessing Pipeline:** Automatic contrast enhancement (CLAHE), adaptive thresholding, bilateral smoothing, and perspective deskewing for difficult lighting (night, glare, rain).
- **OCR Engine with Domain Heuristics:** Multi-candidate OCR with character correction matrices resolving optical ambiguities (e.g., `O` $\leftrightarrow$ `0`, `I` $\leftrightarrow$ `1`, `8` $\leftrightarrow$ `B`, `5` $\leftrightarrow$ `S`).
- **Indian Standard Plate Validation:** Strict validation across all 36 Indian states & union territory codes, commercial vs. private color logic, and series formats.
- **Multi-Object Tracking (MOT):** Kalman filter and IOU-based tracking to maintain consistent vehicle IDs across video frames.
- **Duplicate Suppression:** Temporal spatial windowing prevents multiple records for the same vehicle pausing at gates or lights.

### 🌐 High-Performance Backend (FastAPI)
- **Asynchronous Architecture:** Non-blocking async endpoints with SQLAlchemy 2.0 and connection pooling.
- **Database Flexibility:** Native support for both **PostgreSQL** (production) and **SQLite** (instant zero-config local dev).
- **Real-Time WebSockets:** Event broadcast channels for live detection streams and alert notifications.
- **Role-Based Access Control (RBAC):** Granular permissions for `admin`, `operator`, and `viewer` roles secured via standard bcrypt and JWT tokens.
- **Built-in AI Assistant:** In-memory LLM / heuristic database agent translating plain English questions (e.g. *"Show me all white SUVs detected today"*) into structured analytics queries.

### 💻 Modern Web Operations Console (Next.js 16)
- **Command Dashboard:** Live KPI counters, hourly traffic histograms, and vehicle classification breakdowns.
- **Multi-Camera Wall:** Real-time camera grid with stream status monitoring and configuration.
- **Detection Log & Search:** Full-text plate search, state filtering, confidence sorting, and cropped image views.
- **Smart Alert Management:** Configurable alert triggers for watchlists, suspicious vehicles, or plate matches.
- **Interactive AI Assistant:** Conversational chat interface for natural language querying over ANPR records.
- **System Health Monitor:** Live diagnostics of API latency, database status, Redis cache, and GPU acceleration.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Next.js 16 Frontend (Port 3000)             │
│  Dashboard │ Camera Wall │ Detections │ Analytics │ AI Chat │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST + WebSockets
┌──────────────────────────▼──────────────────────────────────┐
│                 FastAPI Backend (Port 8000)                 │
│  Auth (JWT) │ Cameras │ Detections │ Alerts │ AI Assistant  │
└───┬──────────────────────┬───────────────────────────────┬──┘
    │                      │                               │
    ▼                      ▼                               ▼
PostgreSQL / SQLite      Redis                       ANPR Engine
(Database)             (Cache / PubSub)         ┌───────────────────────┐
                                                │ YOLO Vehicle Detector │
                                                │ Plate Detector Crop   │
                                                │ CLAHE Preprocessing   │
                                                │ EasyOCR + Correction  │
                                                │ Indian State Validator│
                                                │ Multi-Object Tracker  │
                                                └───────────────────────┘
```

---

## 📁 Repository Structure

```
ANPR/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Modular API routes (auth, cameras, detections, ai, uploads)
│   │   ├── core/            # Security (bcrypt, JWT), logging, middleware, exceptions
│   │   ├── database/        # Async SQLAlchemy session and Redis connection handlers
│   │   ├── models/          # Relational DB models (User, Camera, DetectionEvent, etc.)
│   │   ├── schemas/         # Pydantic v2 validation schemas
│   │   ├── services/        # Business logic & AI query assistant service
│   │   ├── vision/          # Computer Vision core (detector, OCR, tracker, validator)
│   │   ├── websocket/       # Real-time WebSocket connection manager
│   │   ├── config.py        # Pydantic environment configuration
│   │   └── main.py          # FastAPI application entry point & demo seeder
│   ├── tests/               # Pytest suite for vision algorithms & validators
│   ├── Dockerfile           # Backend container definition
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── dashboard/       # Dashboard pages (cameras, detections, analytics, assistant)
│   │   ├── login/           # Authentication page
│   │   ├── layout.tsx       # Root Next.js layout & theme
│   │   └── page.tsx         # Modern landing page
│   ├── lib/                 # Typed API client & utilities
│   ├── Dockerfile           # Frontend production container definition
│   └── package.json         # Node.js dependencies (Next.js, Radix, Lucide, Recharts)
├── docker-compose.yml       # Multi-container orchestration (App + Postgres + Redis)
├── ARCHITECTURE.md          # Detailed engineering and architecture specification
├── DEVELOPMENT_PLAN.md      # Milestone implementation guide
├── TODO.md                  # Task tracking and feature checklist
└── README.md                # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** 3.10, 3.11, 3.12, or 3.14
- **Node.js:** 18.x or 20.x+
- **npm** or **pnpm** / **yarn**
- *(Optional)* **Docker & Docker Compose**

---

### Option A: Local Development Setup (Quickest)

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server (starts SQLite & seeds 200 demo detections automatically)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API is now running at **`http://localhost:8000`** (Swagger docs: **`http://localhost:8000/docs`**).

#### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```
The frontend is now available at **`http://localhost:3000`**.

---

### Option B: Docker Compose

To run the complete production stack (Backend + Frontend + PostgreSQL + Redis):

```bash
# From the root directory:
docker compose up -d --build
```

Services will be accessible at:
- **Web Console:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **PostgreSQL:** `localhost:5432`
- **Redis:** `localhost:6379`

---

## 🔑 Default Credentials (Demo Mode)

The system automatically initializes demo users upon first run:

| Role | Username | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Full access, camera configs, user management, alert rules |
| **Operator** | `operator` | `operator123` | View cameras, search detections, manage alert resolutions |

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite covering license plate parsing, regex matching, character correction matrices, image preprocessing, and multi-object tracking:

```bash
cd backend
pytest -v
```

**Test Coverage Summary:**
- Plate structure validation (`XX00XX0000` format)
- Indian state & UT code recognition (DL, MH, KA, TN, UP, GJ, etc.)
- Optical character ambiguity substitution (`O` $\to$ `0`, `I` $\to$ `1`, `8` $\to$ `B`)
- Image preprocessing filters (grayscale, thresholding, morphology)
- Kalman filter tracking & ID preservation across frames
- Temporal duplicate suppression

---

## 📡 API Reference Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Authenticate user & receive JWT tokens |
| `GET` | `/api/v1/cameras` | List all registered cameras & statuses |
| `POST` | `/api/v1/cameras` | Register a new RTSP / webcam stream |
| `GET` | `/api/v1/detections` | Paginated query of vehicle & plate detections |
| `GET` | `/api/v1/analytics/overview` | KPI overview (total vehicles, unique plates, active cameras) |
| `GET` | `/api/v1/analytics/hourly-traffic` | Hourly traffic volume histogram data |
| `GET` | `/api/v1/alerts/events` | List triggered alert events |
| `POST` | `/api/v1/ai/query` | Natural language database query via AI Assistant |
| `POST` | `/api/v1/uploads/image` | Upload image for on-demand ANPR inference |
| `GET` | `/api/v1/system/health` | System health status & diagnostics |
| `WS` | `/ws/detections` | Real-time WebSocket stream for live detections |

*Explore full interactive request/response schemas at `http://localhost:8000/docs`.*

---

## ⚙️ Configuration Reference

Key configuration settings in `backend/.env`:

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./visiontrack.db` | Async database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching & WebSocket pub/sub |
| `JWT_SECRET_KEY` | `dev-secret-key-change-in-production` | Secret key for JWT signing |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifespan |
| `DEMO_MODE` | `true` | Automatically seeds realistic demo data on start |
| `YOLO_DEVICE` | `auto` | Device target: `auto`, `cpu`, or `cuda` |
| `OCR_ENGINE` | `easyocr` | OCR engine: `easyocr` or `paddleocr` |

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request for enhancements, additional plate formats, or performance optimizations.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
