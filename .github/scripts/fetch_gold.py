"""ดึงราคาทองคำแท่ง 96.5% ตามประกาศสมาคมค้าทองคำ แล้วเขียนลง gold.json

รันโดย .github/workflows/gold-price.yml ทุก 15 นาที
หน้า index.html อ่านไฟล์นี้ตรงๆ จึงไม่ต้องมีเซิร์ฟเวอร์

ถ้าดึงไม่สำเร็จ → ไม่แตะ gold.json (คงราคาเดิมไว้) แล้ว exit 1 ให้ Actions ขึ้นแดง
"""

import json
import os
import sys
import time
import urllib.request

SOURCE = 'https://thaigold.info/RealTimeDataV2/gtdata_.txt'
OUT = 'gold.json'
TIMEOUT = 20


def to_num(v):
    if isinstance(v, (int, float)):
        return float(v) if v > 0 else None
    if isinstance(v, str):
        cleaned = ''.join(c for c in v if c.isdigit() or c == '.')
        try:
            n = float(cleaned)
        except ValueError:
            return None
        return n if n > 0 else None
    return None


def main():
    req = urllib.request.Request(SOURCE, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; TWC9-Landing/1.0; +https://github.com)',
        'Accept': 'application/json, text/plain, */*',
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        rows = json.loads(resp.read().decode('utf-8'))

    if not isinstance(rows, list):
        print('รูปแบบข้อมูลไม่ถูกต้อง: ไม่ใช่ list', file=sys.stderr)
        return 1

    by_name = {str(r.get('name', '')): r for r in rows if isinstance(r, dict)}

    # แถว 'สมาคมฯ' = ทองคำแท่ง 96.5% ประกาศสมาคมค้าทองคำ (bid=รับซื้อคืน, ask=ขายออก)
    # อย่าใช้แถว '96.5%' — นั่นคือราคาคำนวณจาก gold spot ไม่ใช่ประกาศสมาคมฯ
    bar = by_name.get('สมาคมฯ') or {}
    buy = to_num(bar.get('bid'))
    sell = to_num(bar.get('ask'))
    if not buy or not sell:
        print('ไม่พบราคาในแถว "สมาคมฯ"', file=sys.stderr)
        return 1

    data = {
        'status': 'success',
        'source': 'thaigold.info · สมาคมค้าทองคำ',
        'kind': 'gold_bar',
        'buy': buy,
        'sell': sell,
        'diff': bar.get('diff'),
        'updated_at': str((by_name.get('Update') or {}).get('ask') or ''),
        'fetched_at': int(time.time()),
    }

    # เขียนเฉพาะตอนราคาเปลี่ยนจริง — กัน commit เปล่าทุก 15 นาทีจาก fetched_at
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding='utf-8') as f:
                old = json.load(f)
            same = all(old.get(k) == data.get(k)
                       for k in ('buy', 'sell', 'updated_at'))
            if same:
                print(f"ราคาไม่เปลี่ยน ({sell:.0f}/{buy:.0f}) — ข้ามการเขียนไฟล์")
                return 0
        except Exception:
            pass  # ไฟล์เสีย → เขียนทับ

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f"อัปเดต: ขายออก {sell:.0f} / รับซื้อ {buy:.0f} @ {data['updated_at']}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'ดึงราคาไม่สำเร็จ: {e}', file=sys.stderr)
        sys.exit(1)
