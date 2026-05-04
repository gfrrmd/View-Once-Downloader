# 📥 Downloadinaja

Bot Telegram all-in-one untuk menyimpan media **view once** dan **timer** langsung ke Saved Messages. Multi-user — setiap orang bisa setup akun mereka sendiri!

## ✨ Fitur

- Multi-user: setiap user punya session & client sendiri
- Setup session langsung dari chat bot (tanpa coding)
- Download media view once & timer dengan `.dl`
- Session tersimpan otomatis per user, tidak hilang saat restart
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

Setelah deploy, siapapun bisa chat bot dan setup akun mereka sendiri:

1. `/start` — lihat status
2. `/setup` — ikuti langkah setup (API ID → API HASH → No HP → OTP)
3. Selesai! Balas media view once/timer dengan `.dl`
4. Media tersimpan ke **Saved Messages** masing-masing user

## 📋 Perintah

| Perintah | Fungsi |
|----------|--------|
| `/start` | Lihat info & status |
| `/setup` | Setup session baru |
| `/status` | Cek status session kamu |
| `/reset` | Hapus session kamu |
| `/cancel` | Batalkan proses setup |

## ⚠️ Catatan

- API ID & API HASH didapat dari https://my.telegram.org
- Setiap user menyimpan session masing-masing secara terpisah
- Jangan bagikan data session kamu ke siapapun
- File `session_data.json` otomatis di-ignore git (tidak terupload)
