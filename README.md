# plant-doctor-site

Marketing website + privacy policy + support page for the Plant Doctor app, hosted on GitHub Pages.

GitHub username: **mishraankit007**

## Deploy (one-time, ~5 minutes)

1. Go to [github.com/new](https://github.com/new) and create a new **private** repository named `plant-doctor-site` (empty — don't add a README/license there).
   - Private is fine: GitHub Pages can publish from a private repo on the free plan — your source stays private, but the built site is public at the URL below (which is what App/Play Store review needs).
2. In this folder, run:
   ```bash
   git remote add origin https://github.com/mishraankit007/plant-doctor-site.git
   git branch -M main
   git push -u origin main
   ```
3. On GitHub, open the repo → **Settings → Pages** → under "Build and deployment", set Source to **Deploy from a branch**, branch **main**, folder **/ (root)** → **Save**.
4. Wait ~1 minute, then your pages are live at:
   - `https://mishraankit007.github.io/plant-doctor-site/` (homepage)
   - `https://mishraankit007.github.io/plant-doctor-site/privacy.html` (privacy policy)

Use those two URLs in the Play Console / App Store Connect listing fields (see `../plant-doctor/legal/store-listing.md`).

## Updating later

Edit the HTML files, then:
```bash
git add -A
git commit -m "Update site"
git push
```
Pages redeploys automatically within a minute.

## Connecting your own domain once you buy one

Say you buy `plantdoctor.app` (or whatever you land on). Two parts: point DNS at GitHub, then tell GitHub about the domain.

**1. In this repo:**
```bash
echo "plantdoctor.app" > CNAME
git add CNAME
git commit -m "Add custom domain"
git push
```
(Or set it via Settings → Pages → Custom domain → GitHub creates the `CNAME` file for you — either works.)

**2. At your domain registrar** (wherever you bought the domain — Namecheap, GoDaddy, Google Domains, etc.), add DNS records:

- If you want the **apex/root domain** (`plantdoctor.app`) to work, add four **A records** for `@`, all pointing at GitHub Pages' IPs:
  ```
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153
  ```
  Plus an **AAAA** set (optional, for IPv6):
  ```
  2606:50c0:8000::153
  2606:50c0:8001::153
  2606:50c0:8002::153
  2606:50c0:8003::153
  ```
- If you want a **subdomain** instead (e.g. `www.plantdoctor.app`), add a **CNAME record**:
  ```
  www  →  mishraankit007.github.io
  ```
  Most people set up both: apex via A records, and a `www` CNAME that redirects to the apex (GitHub Pages handles that redirect automatically once both are configured).

**3. Back on GitHub**: Settings → Pages → Custom domain → enter `plantdoctor.app` → Save. Wait for the DNS check to go green (can take a few minutes to 24 hours depending on DNS propagation), then tick **Enforce HTTPS** once it's available (GitHub auto-provisions a free SSL certificate — this checkbox usually appears within an hour of the domain verifying).

**4. Once live**, update these to use the new domain instead of the `github.io` URL:
- `legal/store-listing.md` and `content.ts` in the main `plant-doctor` app repo (support/privacy URLs)
- The `support@plantdoctor.com` placeholder in `index.html` and `privacy.html` here — swap for a real inbox at whatever domain you actually register, once you've set up email for it (e.g. via Google Workspace, or your registrar's free email forwarding)

Ping me with the domain once you've bought it and I'll do steps 1 and 4 for you — steps 2 and 3 (registrar DNS + GitHub's domain-verification UI) need to happen in accounts only you can access.
