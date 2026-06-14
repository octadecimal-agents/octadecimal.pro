# octadecimal.pro — marketing site (static)

Static marketing site for [octadecimal.pro](https://octadecimal.pro) and [octadecimal.pro/en/](https://octadecimal.pro/en/).

## Structure

```
website/
├── index.html              # PL homepage
├── en/index.html           # EN homepage
├── typowy-dzien-pracy/     # PL subpage
├── en/typical-workday/     # EN subpage
└── assets/                 # CSS, JS, avatars, logos
```

## Local preview

```bash
cd website
python3 -m http.server 8080
```

- PL homepage: http://127.0.0.1:8080/
- PL workday: http://127.0.0.1:8080/typowy-dzien-pracy/
- EN workday: http://127.0.0.1:8080/en/typical-workday/

## Deploy

Site is served by `octadecimal-pro-web` on pc-ubuntu (bind mount → `/home/octadecimal/www/octadecimal.pro`, port 8080, Cloudflare → public).

Quick sync (no `--delete` — keeps `zespol/`, `projekty/`, legal pages on prod):

```bash
rsync -avz website/ pc-ubuntu:/home/octadecimal/www/octadecimal.pro/
```

## Content source

Subpage **Typowy dzień pracy** / **Typical workday** is derived from Octa OS research:

- Knowledge: `01-Base-Point/pro/projects/octa-os/research/07-typowy-dzien-ceo.md`
- Strategy: `06-strategia-adopcji.md`

## Navigation

Main menu (PL/EN): link **after** „Jak to działa” / „How it works”.
