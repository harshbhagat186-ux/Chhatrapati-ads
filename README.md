# Chhatrapati Bullion Ads

Daily advertisement photos and reels for Chhatrapati Bullion (Soni Bazar, Rajkot), and the Android app
that shows them.

- **Daily ads**: `.github/workflows/daily.yml` runs every morning at 7:00 AM India time (backup run 8:15 AM).
  `adgen/daily.py` makes the day's ads in Gujarati and Hindi: 1080x1920 photos plus 8-second animated reels with music.
  The design is `adgen/template.html`, rendered by headless Chromium (`adgen/render.js`).
  On festival days (`adgen/calendar.json`) it makes the festival greeting; otherwise the weekday's regular ad.
  Festivals in the next 2 days are added early so they can be shared in advance.
- Each day is a GitHub Release tagged `YYYY-MM-DD` holding the full-HD files. `index.json` (built by
  `tools/make_index.py`) is what the app reads.
- **App** (`app/`): ads grouped by date, full-screen preview, **Save** (original full HD into the gallery,
  Pictures/Chhatrapati and Movies/Chhatrapati), **Share** (WhatsApp or any app), and a 9:00 AM
  "today's ads are ready" notification. `.github/workflows/build-apk.yml` builds the APK on every change
  under `app/` and publishes it to the release tagged `app`; the app shows a banner when a newer build exists.

A "Good evening" ad is made only on request (Run workflow with "evening" ticked).

Make a specific day by hand: Actions → Daily ads → Run workflow → enter the date (tick "evening" for the evening ad).

Change shop details (phones, address): `adgen/shop.py`.
Add or fix festivals: `adgen/calendar.json` (dates come from published 2026/2027 panchang listings; check
regional dates once a year).

Install the app: open `https://github.com/harshbhagat186-ux/chhatrapati-ads/releases/download/app/ChhatrapatiAds.apk`
on the phone, allow "install unknown apps" for the browser when asked, then tap Install.
