# dotday.uz

Dotday ilovasining sayti: landing (13 til), yo'riqnoma (en/uz/ru), maxfiylik siyosati va shartlar.
GitHub Pages `main` / root'dan xizmat qiladi, domen — `CNAME`.

## O'zgartirish

Landing va yo'riqnoma HTML'i qo'lda tahrirlanmaydi — `src/` dan generatsiya qilinadi:

- `src/i18n/<til>.json` — landing matnlari (`en.json` — namuna, kalitlar hamma tilda bir xil bo'lishi shart)
- `src/guide/<til>.json` — yo'riqnoma; yangi til qo'shish uchun fayl qo'shing
- `src/captions.json` — skrinshot sarlavhalari (ilova reposidagi `store/captions.json` dan)
- `assets/style.css`, `assets/site.js` — dizayn va mavzu/til almashtirish

```bash
python3 src/build.py          # HTML, sitemap.xml, robots.txt, assets/langs.js ni qayta yaratadi
python3 -m http.server 8765   # http://localhost:8765
git add -A && git commit -m "..." && git push
```

`privacy*.html` va `terms*.html` qo'lda yoziladi; build ularga faqat canonical/hreflang va mavzu skriptini qo'shadi.

Skrinshotlar: ilova reposidagi `store/raw/<locale>/*.png` → `cwebp -q 78 -resize 600 0` → `assets/shots/<til>/`.
