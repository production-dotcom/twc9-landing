"""ดึงราคาทองจาก API กลางของเรา (ทวีชัย ๙) แล้วเขียนลง gold.json

รันโดย .github/workflows/gold-price.yml ทุก 15 นาที
หน้า index.html อ่านไฟล์นี้ตรงๆ จึงไม่ต้องมีเซิร์ฟเวอร์

หลักการ (สเปคราคาทองกลาง): ห้ามยิงต้นทางเอง (thaigold.info / goldtraders / chnwt) จากที่นี่
ยิงมาที่ API เดียวของเรา — เราจัดการ fallback + ธง (stale/manual/estimated/disputed) ให้หมดแล้ว

ถ้าดึงไม่สำเร็จ → ไม่แตะ gold.json (คงราคาเดิมไว้) แล้ว exit 1 ให้ Actions ขึ้นแดง
"""

import json
import os
import sys
import time
import urllib.request

# API กลางของเรา (relay) — จุดเดียวที่หน้าเว็บ/POS/แอปควรเรียก
SOURCE = os.environ.get('GOLD_API') or 'https://admin.twc9sai5.com/api/gold-price'
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
        'User-Agent': 'TWC9-Landing/2.0 (+https://github.com)',
        'Accept': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        g = json.loads(resp.read().decode('utf-8'))

    if not isinstance(g, dict) or not g.get('ok'):
        print('API เราไม่มีราคา: %s' % (g.get('error') if isinstance(g, dict) else 'bad response'), file=sys.stderr)
        return 1

    buy = to_num(g.get('barBuy'))
    sell = to_num(g.get('barSell'))
    if not buy or not sell:
        print('ไม่พบราคาแท่งจาก API', file=sys.stderr)
        return 1

    data = {
        'status': 'success',
        'source': 'API ทวีชัย ๙' + (' (%s)' % g.get('source') if g.get('source') else ''),
        'kind': 'gold_bar',
        'buy': buy,
        'sell': sell,
        # ราคารูปพรรณจริงจากสมาคม (ไม่ใช่แท่ง+550 อีกต่อไป) + ธงสถานะ
        'ornamentBuy': to_num(g.get('ornamentBuy')),
        'ornamentSell': to_num(g.get('ornamentSell')),
        'diff': g.get('diff'),
        'stale': bool(g.get('stale')),
        'manual': bool(g.get('manual')),
        'estimated': bool(g.get('estimated')),
        'disputed': bool(g.get('disputed')),
        'updated_at': str(g.get('updated') or ''),
        'fetched_at': int(time.time()),
    }

    # เขียนเฉพาะตอนราคาเปลี่ยนจริง — กัน commit เปล่าทุก 15 นาทีจาก fetched_at
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding='utf-8') as f:
                old = json.load(f)
            same = all(old.get(k) == data.get(k)
                       for k in ('buy', 'sell', 'ornamentSell', 'updated_at'))
            if same:
                print("ราคาไม่เปลี่ยน (%.0f/%.0f) — ข้ามการเขียนไฟล์" % (sell, buy))
                return 0
        except Exception:
            pass  # ไฟล์เสีย → เขียนทับ

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print("อัปเดต: แท่งขาย %.0f / รับซื้อ %.0f · รูปพรรณขาย %s @ %s"
          % (sell, buy, data.get('ornamentSell'), data['updated_at']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print('ดึงราคาไม่สำเร็จ: %s' % e, file=sys.stderr)
        sys.exit(1)
