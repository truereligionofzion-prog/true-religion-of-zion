# True Religion Of Zion — Netlify-Ready Source

This is the full source (Vite + React) of your site. You do NOT need PowerShell to deploy.

## Deploy without any CLI (GitHub + Netlify)

1. Create a **new GitHub repo** on github.com (empty).
2. Click **Add file → Upload files**, then **drag the *contents* of this folder** into the repo (include `package.json`, `index.html`, `netlify.toml`, `public/`, `src/`).
3. In Netlify: **Add new site → Import an existing project** → choose your GitHub repo.
4. Build command: `npm run build` | Publish directory: `dist` (already set in `netlify.toml`).
5. Deploy.

Routing is handled by both `netlify.toml` and `public/_redirects`.

## Local dev (optional)
```bash
npm install
npm run dev
```
