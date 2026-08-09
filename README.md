# plant-doctor-legal-site

Static privacy policy + support page for the Plant Doctor app, meant to be hosted on GitHub Pages for App Store / Play Store submission.

## Deploy (one-time, ~5 minutes)

1. Go to [github.com/new](https://github.com/new) and create a new **public** repository named `plant-doctor-legal-site` (empty — don't add a README/license there).
2. In this folder, run:
   ```bash
   git remote add origin https://github.com/<your-github-username>/plant-doctor-legal-site.git
   git branch -M main
   git push -u origin main
   ```
3. On GitHub, open the repo → **Settings → Pages** → under "Build and deployment", set Source to **Deploy from a branch**, branch **main**, folder **/ (root)** → **Save**.
4. Wait ~1 minute, then your pages are live at:
   - `https://<your-github-username>.github.io/plant-doctor-legal-site/` (support page)
   - `https://<your-github-username>.github.io/plant-doctor-legal-site/privacy.html` (privacy policy)

Use those two URLs in the Play Console / App Store Connect listing fields (see `../plant-doctor/legal/store-listing.md`).

## Updating later

Edit `index.html` / `privacy.html`, then:
```bash
git add -A
git commit -m "Update legal pages"
git push
```
Pages redeploys automatically within a minute.

## Once plantdoctor.app is registered

Swap `mishra.ankit.nit1@gmail.com` for a real `@plantdoctor.app` address in both HTML files, and consider pointing the domain at this GitHub Pages site (Settings → Pages → Custom domain) instead of the `github.io` URL.
