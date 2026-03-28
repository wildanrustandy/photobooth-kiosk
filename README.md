# Photobooth Web Kiosk

Aplikasi web photobooth untuk kiosk touchscreen di mall, event, wedding, dll. Aplikasi ini sekarang sudah terintegrasi penuh dengan iPaymu Payment Gateway menggunakan backend FastAPI.

## Tech Stack

- **Frontend:** Vue 3 + Vite + Pinia + TailwindCSS
- **Backend:** FastAPI (Python) dengan iPaymu Payment Gateway
- **Database:** PostgreSQL - coming soon

## Quick Start

### Prerequisites

- Node.js 18+
- npm atau bun
- Python 3.9+ (untuk Backend FastAPI)

### 1. Install & Run Backend (FastAPI)

Backend menangani pembuatan QRIS dan pengecekan status transaksi secara aman ke API iPaymu.

```bash
# Masuk ke folder backend
cd backend

# Buat virtual environment (opsional namun direkomendasikan)
python3 -m venv venv

# Aktifkan virtual environment
# Mac/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Jalankan server FastAPI
uvicorn main:app --reload --port 8000
```

Backend API akan berjalan di `http://localhost:8000`.

### 2. Install & Run Frontend (Vue 3)

Buka terminal baru untuk menjalankan frontend.

```bash
# Masuk ke folder frontend
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```

Buka http://localhost:5173 di browser. Kiosk siap digunakan!

### Build for Production (Frontend)

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
Landing → Pilih Jumlah Cetak → QR Payment (iPaymu) → Sesi Foto → Preview → Print/Download → Selesai
```

## Features

- **Payment Gateway:** Integrasi langsung QRIS iPaymu dengan auto-polling status
- **Kiosk UI/UX:** Layout 16:9 responsif (1080p & 720p) yang terkunci di layar (no-scroll)
- **Live Camera:** Preview kamera dengan filter real-time
- **Timer Selection:** Pilihan hitung mundur (3s, 5s, 10s)
- **4 Foto per Sesi:** Pengambilan 4 frame foto berurutan
- **Filter:** Normal, Lembut, Hitam-Putih, BW-2, BW-3, Vintage, Bright
- **Retake:** Fitur retake foto individual atau retake semua foto sekaligus dengan konfirmasi
- **Print & Download:** Cetak fisik dan opsi download QR code
- **Auto-Close:** Layar akhir akan otomatis mereset sesi dalam 3 menit jika tidak ada aktivitas

## Project Structure

```
pb/
├── backend/
│   ├── main.py            # FastAPI server & iPaymu endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── composables/   # usePayment.ts, useCamera.ts, dll
│   │   ├── router/
│   │   ├── stores/
│   │   ├── views/         # Layar-layar kiosk (PaymentView, PhotoSessionView, dll)
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── ipaymu/                # Script referensi iPaymu asli (Python)
├── stitch-assets/
├── PRD.md
└── README.md
```

## Testing Camera

Aplikasi membutuhkan akses kamera. Pastikan:
- Browser mendapat izin akses kamera
- Untuk development lokal, gunakan `http://localhost:5173` (bukan IP address) agar kamera diizinkan oleh kebijakan security browser (WebRTC).

## License

MIT