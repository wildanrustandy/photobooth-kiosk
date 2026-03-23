# PRD — Web Photobooth Kiosk

---

## 1. Overview

**Nama Produk:** Photobooth Web Kiosk  
**Platform:** Web (Kiosk Mode - Touchscreen)

**Target User:**

- Customer walk-in (mall, event, wedding, dll)
- Fokus UX: cepat, fun, tanpa bantuan operator

**Design Theme:**

- Dominan **pink muda (soft pastel)**
- Colorful, playful, aesthetic
- Ramah untuk user wanita & social media oriented

---

## 2. UI / Design System

**Framework UI:** TailwindCSS

### Design Principles

- Touch-friendly (button besar)
- Minimal teks
- Fokus visual (foto > teks)
- Animasi halus
- Kontras warna jelas

### Color System

- Primary: Pink muda
- Secondary: Pink lebih bold
- Background: Soft pastel pink
- Text: Abu gelap (readable)

### Component Guidelines

- Button: besar, rounded, shadow
- Card: soft background + spacing lega
- Icon: simple & universal (kamera, print, download)

---

## 3. User Flow

```text
Landing → Pilih Jumlah Cetak → Payment → QR Payment → Sesi Foto → Preview → Print / Download → Selesai
```

---

## 4. Screen & Functional Requirements

### 4.1 Landing Screen

**Deskripsi:**  
Halaman awal saat user datang ke kiosk.

**Elemen:**

- Background slideshow (foto-foto)
- Tombol utama: **"Mulai"**

**Behavior:**

- Slideshow berjalan otomatis
- Klik "Mulai" → masuk ke step berikutnya

**Backend (future):**

- Slideshow diambil dari master data (CRUD)

---

### 4.2 Screen Pilih Jumlah Cetak

**Deskripsi:**  
User menentukan berapa lembar foto yang ingin dicetak.

**Elemen:**

- Counter jumlah (default: 1)
- Tombol tambah & kurang
- Total harga
- Tombol: **"Lanjutkan"**

**Rules:**

- Minimum: 1
- Maximum: 10
- Tidak boleh 0 / negatif

**Pricing:**

- Harga default: **Rp 35.000** per lembar
- Total = jumlah × harga

**Behavior:**

- Harga update secara realtime

---

### 4.3 Screen Pilih Pembayaran

**Deskripsi:**  
User memilih metode pembayaran dan melihat instruksi.

**Elemen:**

- Header: "Pilih Metode Pembayaran"
- QRIS (single option) dengan logo
- Instruksi singkat: "Scan QR untuk membayar"
- Info harga total
- Tombol: **"Lanjutkan"**

**Behavior:**

- Default langsung QRIS
- Klik lanjut → generate QR

---

### 4.4 Screen QR Payment

**Deskripsi:**  
User melakukan pembayaran via QR.

**Elemen:**

- QR Code (ukuran besar, mudah di-scan)
- Total harga
- Countdown timer (default: 5 menit)
- Instruksi: "Scan QR dengan aplikasi pembayaran Anda"

**Behavior:**

- Timer berjalan
- Jika timeout → kembali ke landing

**Integration:**

- Webhook dari payment gateway:
  - Status: **success**

**Trigger:**

- Jika payment success → lanjut ke sesi foto

---

### 4.5 Screen Sesi Foto

**Deskripsi:**  
User mengambil foto menggunakan webcam.

**Elemen:**

- Live camera preview
- Pilihan timer:
  - 3 detik
  - 5 detik (default)
  - 10 detik
- Button utama:
  - "Mulai Foto"
  - berubah menjadi "Memotret"
- Filter:
  - Normal
  - Lembut
  - Hitam Putih
  - BW2
  - BW3
  - Vintage
  - Bright
- Preview grid:
  - Menampilkan semua 4 foto sebagai thumbnail
- Progress indicator: "Foto 1/4", "Foto 2/4", dst

**Sound Effects:**

- Shutter sound saat foto diambil (`/assets/sounds/shutter.mp3`)
- Countdown beep (optional)

**Behavior:**

**Pengambilan Foto:**

- Total foto: **4**
- Interval berdasarkan timer
- Urutan otomatis
- Countdown visual sebelum tiap foto (3...2...1... 📸)

**Selama Proses:**

- Button berubah menjadi "Memotret"
- Progress indicator update

**Setelah Selesai:**

- Button berubah menjadi **"Berikutnya"**
- Semua 4 foto ditampilkan di preview grid

**Retake:**

- Klik foto individual → muncul popup:
  - "Apakah ingin retake foto ini?"
- Jika Ya: hanya foto tersebut diulang
- Tombol "Retake Semua" → ulang semua foto

**Filter:**

- 1 filter berlaku ke semua foto
- Dipilih sebelum memulai sesi

---

### 4.6 Screen Preview & Output

**Deskripsi:**  
Menampilkan hasil akhir dan opsi output.

**Elemen:**

- 4 foto raw (thumbnail grid)
- 1 foto final (dengan frame) - preview besar
- Tombol:
  - Print
  - Download
  - Selesai

**Frame System:**

- Frame bersifat admin configurable
- Disimpan sebagai PNG dengan transparent area
- Default frame applied otomatis
- Future: user dapat pilih frame

**Print Flow:**

**Definisi:**

- Jumlah print = jumlah yang dipilih pada Step 4.2

**Behavior:**

- 1 sesi menghasilkan 1 layout foto
- Layout tersebut dicetak sebanyak jumlah copy
- Paper size: configurable via admin

**Download Flow:**

- Klik download → tampil QR Code
- QR berisi link download
- Format: ZIP file berisi 4 raw photos + 1 final photo
- Valid: **7 hari** setelah generate
- QR expired → tampilkan pesan "Link expired"

**Selesai:**

- Popup konfirmasi:
  - "Apakah yakin ingin mengakhiri sesi?"
- Jika Ya:
  - Session ditutup
  - Kembali ke landing

---

## 5. Backend Requirements

### Core Modules

- Session management
- Payment integration (QRIS)
- Photo storage & processing
- Frame template management
- Print service
- Download service

### Master Data

- Slideshow images
- Frame templates
- Harga default
- Countdown timer
- Paper size config

### Print Service

- Abstraction layer untuk printer driver
- Support: USB printer (future: network printer)
- Configurable paper size via admin
- Print queue management

### API Endpoints

```text
POST /api/sessions
  - Body: { print_count: number }
  - Response: { session_id, total_price }

POST /api/payments/create
  - Body: { session_id }
  - Response: { payment_id, qr_string, expires_at }

GET /api/payments/:id/status
  - Response: { status: "pending" | "success" | "failed" }

POST /api/photos/upload
  - Body: FormData (session_id, photo, order)
  - Response: { photo_id, url }

POST /api/print
  - Body: { session_id }
  - Response: { status: "queued" | "printing" | "done" }

GET /api/download/:token
  - Response: { download_url, expires_at }

GET /api/frames
  - Response: [{ id, name, preview_url }]

GET /api/slideshows
  - Response: [{ id, image_url, order }]
```

---

## 6. Database Schema

### Sessions

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| created_at | timestamp | Waktu pembuatan |
| status | enum | pending, paid, completed, cancelled |
| print_count | integer | Jumlah cetak (1-10) |
| total_price | decimal | Total harga |
| payment_id | UUID | Foreign key ke payments |
| filter | string | Filter yang dipilih |
| timer | integer | Timer dalam detik |

### Photos

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Foreign key ke sessions |
| file_url | string | URL foto |
| order | integer | Urutan foto (1-4) |
| created_at | timestamp | Waktu upload |

### Payments

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Foreign key ke sessions |
| amount | decimal | Jumlah pembayaran |
| status | enum | pending, success, failed |
| provider | string | Payment provider (QRIS) |
| qr_string | string | QR code string |
| paid_at | timestamp | Waktu pembayaran berhasil |
| expires_at | timestamp | Waktu expired |

### Frames

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | string | Nama frame |
| image_url | string | URL file PNG |
| is_active | boolean | Status aktif |
| is_default | boolean | Frame default |
| created_at | timestamp | Waktu pembuatan |

### Slideshows

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| image_url | string | URL gambar |
| order | integer | Urutan tampil |
| is_active | boolean | Status aktif |
| created_at | timestamp | Waktu pembuatan |

### DownloadTokens

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Foreign key ke sessions |
| token | string | Unique token untuk download |
| expires_at | timestamp | Waktu expired (7 hari) |
| created_at | timestamp | Waktu pembuatan |

---

## 7. State Management (Frontend)

**State utama:**

```text
- session_id: string | null
- print_count: number (1-10)
- total_price: number
- payment_status: "idle" | "pending" | "success" | "failed"
- photos: array [{ id, url, order }]
- selected_filter: string
- timer: number (3 | 5 | 10)
- current_step: string
```

---

## 8. Integrations

- Payment Gateway (QRIS)
- Printer system (USB)
- Storage (foto) - S3/MinIO
- Webhook handler (payment callback)

---

## 9. Edge Cases

| Scenario | Handling |
|----------|----------|
| Payment tidak selesai | Auto cancel setelah 5 menit, kembali ke landing |
| User meninggalkan kiosk | Idle timeout 60 detik → auto reset ke landing |
| Kamera tidak tersedia | Tampilkan error "Kamera tidak terdeteksi" + tombol refresh |
| Upload foto gagal | Retry mechanism (3x) + error message |
| Printer gagal | Tampilkan error + opsi retry atau download |
| Printer out of paper | Error message "Printer sedang maintenance" |
| Internet terputus | Tampilkan error + auto reconnect attempt |
| Storage penuh | Auto cleanup old sessions (30 hari) |
| User cancel di tengah sesi | Void session, kembali ke landing |
| Concurrent user attempt | Reject dengan pesan "Sedang diproses, mohon tunggu" |
| QR download expired | Pesan "Link expired, hubungi admin" |

---

## 10. Kiosk Mode Requirements

**Fullscreen mode**

**Disable:**

- Keyboard shortcuts (Ctrl+Alt+Del, Alt+Tab, dll)
- Right click context menu
- Developer tools access
- Address bar

**Auto Reset:**

- Idle timeout: 60 detik setelah sesi selesai
- Reset ke landing screen

---

## 11. Future Enhancements

- Template frame berbeda (user pilih)
- Sticker & editing tools
- DSLR camera integration (USB)
- Multi booth management
- Dashboard analytics
- Admin panel
- Social media sharing
- GIF/Video mode

---

## 12. Tech Stack

### Frontend

- Vue 3
- Vite
- Pinia
- TailwindCSS

### Backend

- FastAPI (Python)

### Database

- PostgreSQL

### Optional

- Redis (realtime/session)
- Object Storage (S3/MinIO)

---

## 13. File Structure (Frontend)

```text
src/
├── assets/
│   ├── sounds/
│   │   └── shutter.mp3
│   └── images/
│       └── frames/
├── components/
│   ├── CameraPreview.vue
│   ├── PhotoGrid.vue
│   ├── QRDisplay.vue
│   ├── CountdownTimer.vue
│   └── FilterSelector.vue
├── views/
│   ├── LandingView.vue
│   ├── PrintCountView.vue
│   ├── PaymentView.vue
│   ├── PhotoSessionView.vue
│   └── PreviewView.vue
├── stores/
│   └── session.ts
├── composables/
│   ├── useCamera.ts
│   ├── usePayment.ts
│   └── usePrinter.ts
└── router/
    └── index.ts
```
