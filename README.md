# Photobooth Web Kiosk

Aplikasi web photobooth untuk kiosk touchscreen di mall, event, wedding, dll.

## Tech Stack

- **Frontend:** Vue 3 + Vite + Pinia + TailwindCSS
- **Backend:** FastAPI (Python) - coming soon
- **Database:** PostgreSQL - coming soon

## Quick Start

### Prerequisites

- Node.js 18+
- npm atau bun

### Install & Run

```bash
# Masuk ke folder frontend
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```

Buka http://localhost:5173 di browser.

### Build for Production

```bash
cd frontend
npm run build
```

Output ada di `frontend/dist/`

### Preview Production Build

```bash
cd frontend
npm run preview
```

## User Flow

```
Landing → Pilih Jumlah Cetak → Payment → QR Payment → Sesi Foto → Preview → Print/Download → Selesai
```

## Features

- Live camera preview dengan filter
- Timer selection (3s, 5s, 10s)
- 4 foto per sesi
- Filter: Normal, Lembut, Hitam-Putih, BW-2, BW-3, Vintage, Bright
- Retake foto individual atau semua
- Print & Download hasil foto

## Project Structure

```
pb/
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── stitch-assets/
│   ├── html/
│   └── screenshots/
├── PRD.md
└── README.md
```

## Testing Camera

Aplikasi membutuhkan akses kamera. Pastikan:
- Browser mendapat izin akses kamera
- Untuk development lokal, gunakan `localhost` (bukan IP address) agar kamera bisa diakses

## License

MIT
