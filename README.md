# ห้างทองทวีชัย ๙ — Landing Page

หน้าเว็บมือถือของร้าน ทองแท้ 96.5% · ซื้อ ขาย จำนำ ออมทอง
เสิร์ฟผ่าน GitHub Pages เป็นไฟล์ static ล้วน ไม่ต้องมีเซิร์ฟเวอร์

## ราคาทองอัปเดตยังไง

`.github/workflows/gold-price.yml` รันทุก ~15 นาที → เรียก `.github/scripts/fetch_gold.py`
→ ดึงราคาทองคำแท่ง 96.5% ประกาศสมาคมค้าทองคำ จาก `thaigold.info`
→ เขียนลง `gold.json` แล้ว commit **เฉพาะตอนราคาเปลี่ยนจริง**

หน้าเว็บอ่าน `gold.json` ตรงๆ ไล่ลำดับแหล่งราคาแบบนี้:

1. `goldApiUrl` (ตั้งเองได้ — ชี้ไปเซิร์ฟเวอร์ในร้าน)
2. `./gold.json` ← ปกติใช้ตัวนี้
3. `/api/gold-price` (ตอนเปิดจาก `serve_lan.py` ในร้าน)
4. `api.chnwt.dev` (สำรอง)

ถ้าดึงไม่ได้ทุกทาง → ขึ้นป้าย OFFLINE + ปุ่มลองใหม่ แล้วแสดงราคาอ้างอิงจาก prop `refGoldPrice`

**กดอัปเดตเองทันที:** แท็บ Actions → "อัปเดตราคาทอง" → Run workflow

## ตั้งค่า GitHub Pages

Settings → Pages → Source: **Deploy from a branch** → Branch `main` / `(root)` → Save

## แก้ราคาอ้างอิงตอน offline

ใน `index.html` ที่ `data-props` → `refGoldPrice`

## ⚠️ ค้างอยู่ — ลิงก์ยังเป็น placeholder

`#line` `#tel` `#map` `#tiktok` `#fb` `#save` `#review` ยังกดไม่ไปไหน
ต้องแทนด้วยลิงก์จริง (LINE OA, `tel:`, Google Maps, TikTok, Facebook)

## ⚠️ ค้างอยู่ — ภาษาพม่าไม่ครบ

ส่วนแคตตาล็อก รีวิว FAQ และ "ทำไมคนแถวนี้ซื้อกับเรา" ยังเป็นไทยล้วน
