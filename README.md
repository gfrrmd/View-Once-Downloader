# 📥 Downloadinaja

Bot Telegram all-in-one untuk menyimpan media **view once** dan **timer** langsung ke Saved Messages. Cukup deploy sekali dengan satu variabel!

## ✨ Fitur

- Setup session langsung dari chat bot (tanpa coding)
- Download media view once & timer dengan `.dl`
- Session tersimpan otomatis, tidak hilang saat restart
- Support A2F (Two-Factor Authentication)

## 🚀 Deploy ke Railway

1. Fork repo ini
2. Buat project baru di [Railway](https://railway.app)
3. Connect repo ini
4. Tambahkan satu variabel:
   ```
   BOT_TOKEN=token_bot_telegram_kamu
   ```
5. Deploy!

## 📖 Cara Pakai

Setelah deploy, chat bot kamu di Telegram:

1. `/start` — lihat status
2. `/setup` — ikuti langkah setup (API ID → API HASH → No HP → OTP)
3. Selesai! Sekarang balas media view once/timer dengan `.dl`

## 📋 Perintah

| Perintah | Fungsi |
|----------|--------|
| `/start` | Lihat info & status |
| `/setup` | Setup session baru |
| `/status` | Cek status session |
| `/reset` | Hapus session |
| `/cancel` | Batalkan proses setup |

## ⚠️ Catatan

- API ID & API HASH didapat dari https://my.telegram.org
- Jangan bagikan data session kamu ke siapapun
- File `session_data.json` otomatis di-ignore git (tidak terupload)
