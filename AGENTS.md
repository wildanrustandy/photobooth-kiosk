# Photobooth Web Kiosk - Codebase Summary

## Project Overview

**Photobooth Web Kiosk** adalah aplikasi photobooth self-service berbasis web untuk venue publik seperti mall, acara, dan pernikahan. Aplikasi ini menyediakan pengalaman end-to-end dimana pelanggan dapat memilih jumlah cetak, membayar via QRIS, mengambil foto, menerapkan filter, dan mencetak hasilnya.

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Vue 3 | ^3.5.30 | UI Framework |
| Vite | ^8.0.1 | Build Tool |
| Pinia | ^3.0.4 | State Management |
| TailwindCSS | ^4.2.2 | CSS Framework |
| TypeScript | ~5.9.3 | Type Safety |
| Vue Router | ^4.6.4 | Navigation |
| QRCode | ^1.5.4 | QR Code Generation |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| Uvicorn | ASGI Server |
| Pydantic | Data Validation |
| Requests | HTTP Client |

---

## Directory Structure

```
pb/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints & iPaymu integration
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   └── tests/                 # Python tests
│
├── frontend/                   # Vue 3 application
│   ├── src/
│   │   ├── main.ts           # Entry point
│   │   ├── App.vue           # Root component
│   │   ├── assets/           # Static assets (sounds, images)
│   │   ├── components/       # Reusable UI components
│   │   │   ├── QRDisplay.vue
│   │   │   ├── FilterSelector.vue
│   │   │   ├── PhotoGrid.vue
│   │   │   ├── CountdownTimer.vue
│   │   │   └── ProgressIndicator.vue
│   │   ├── composables/      # Vue composables
│   │   │   ├── usePayment.ts   # Payment logic
│   │   │   ├── useCamera.ts    # Camera handling
│   │   │   └── usePrinter.ts   # Print functionality
│   │   ├── stores/           # Pinia stores
│   │   │   └── session.ts    # Session state management
│   │   ├── views/            # Page components
│   │   │   ├── LandingView.vue
│   │   │   ├── PrintCountView.vue
│   │   │   ├── PaymentView.vue
│   │   │   ├── PhotoSessionView.vue
│   │   │   └── PreviewView.vue
│   │   └── router/           # Vue Router config
│   ├── public/               # Static public assets
│   ├── index.html            # HTML entry
│   ├── package.json          # Dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── tsconfig.json         # TypeScript config
│   └── tailwind.config.js    # Tailwind config
│
├── ipaymu/                    # iPaymu reference scripts
├── Kiosk-Photobooth/         # Kiosk hardware code
├── stitch-assets/            # Design assets & screenshots
│   ├── html/                 # HTML design mockups
│   └── screenshots/          # UI screenshots
│
├── .opencode/                # OpenCode configuration
│   └── oh-my-opencode-slim.json
├── .pre-commit-config.yaml   # Pre-commit hooks config
├── Description.md             # Project overview
├── PRD.md                    # Product Requirements Document
└── AGENTS.md                 # This file
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI server dengan integrasi pembayaran QRIS iPaymu |
| `frontend/src/stores/session.ts` | State management pusat (payment, photos, session) |
| `frontend/src/router/index.ts` | Definisi route (5 views) |
| `frontend/src/composables/usePayment.ts` | Logic pembuatan & polling pembayaran |
| `frontend/src/composables/useCamera.ts` | Akses kamera WebRTC & capture |
| `frontend/src/assets/styles/main.css` | Tailwind v4 dengan custom Material Design 3 color theme |

---

## Architecture

### User Flow
```
Landing → Print Count → Payment → Photo Session → Preview → Complete
```

### State Management (Pinia Store)
- `sessionId`, `printCount`, `totalPrice`
- `paymentStatus`: idle | pending | success | failed
- `photos`: Array foto yang di-capture dengan blob data
- `selectedFilter`: Filter yang dipilih
- `timer`: Countdown timer (3, 5, atau 10 detik)

### Backend API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/payment/create` | POST | Membuat pembayaran QRIS |
| `/api/payment/status/{id}` | GET | Cek status pembayaran |
| `/api/payment/notify` | GET/POST | Webhook untuk konfirmasi pembayaran |

### Design System
- **Theme**: Soft pink pastel (Material Design 3 inspired)
- **Primary**: `#a7295a` (pink)
- **Background**: `#edf8ff` (light blue)
- **Typography**: Plus Jakarta Sans (headlines), Be Vietnam Pro (body)

---

## Build & Run

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm atau bun

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # atau venv\Scripts\activate di Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API: http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev     # Development: http://localhost:5173
npm run build   # Production build ke dist/
npm run preview # Preview production build
```

### Development Tools
```bash
# Run linting & formatting
npm run lint    # ESLint
npm run format  # Prettier

# Pre-commit hooks (Python)
pre-commit run --all-files
```

---

## Notable Features

1. **Kiosk Mode**: Viewport fixed, no scroll, UI touch-optimized
2. **Real-time Filters**: CSS filter-based (grayscale, sepia, brightness)
3. **Payment Integration**: iPaymu QRIS dengan auto-polling setiap 3 detik
4. **Camera**: WebRTC dengan resolusi ideal 1080p, mirror mode
5. **Photo Countdown**: Visual countdown dengan shutter sound
6. **Auto-reset**: Idle timeout 3 menit kembali ke landing
7. **Retake**: Retake individual atau semua foto dengan confirmation modals

---

## OpenCode Configuration

File konfigurasi utama: `.opencode/oh-my-opencode-slim.json`

```json
{
  "preset": "opencode-go"
}
```

Preset `opencode-go` digunakan untuk konfigurasi default OpenCode di repository ini.
