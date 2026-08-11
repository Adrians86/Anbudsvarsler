# Deploying to Netlify

The Netlify MCP tools were unavailable at build time. Follow these steps to deploy manually.

## Prerequisites

- Node.js 18+
- A Netlify account at https://app.netlify.com

## Option A — Netlify CLI (recommended)

```bash
# Install CLI globally
npm install -g netlify-cli

# From the repo root
cd /path/to/Anbudsvarsler

# Log in
netlify login

# Create a new Netlify site linked to this repo
netlify sites:create --name anbudsvarsler-web

# Build and deploy (from web/ directory)
cd web
npm run build
netlify deploy --dir .next --prod
```

## Option B — GitHub integration (recommended for CI/CD)

1. Push the branch to GitHub (already done: `claude/anbudsvarsler-mvp-f2v561`).
2. Go to https://app.netlify.com → **Add new site → Import an existing project**.
3. Select the `Adrians86/Anbudsvarsler` GitHub repository.
4. Set the following build settings:
   - **Base directory:** `web`
   - **Build command:** `npm run build`
   - **Publish directory:** `web/.next`
5. Add the `@netlify/plugin-nextjs` plugin (or confirm via `netlify.toml`).
6. Click **Deploy site**.

## Environment Variables

Set these in the Netlify dashboard under **Site settings → Environment variables**:

| Variable | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-api.example.com` | URL of the FastAPI backend |

## netlify.toml (already committed at web/netlify.toml)

```toml
[build]
  base = "web"
  publish = ".next"
  command = "npm run build"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NEXT_PUBLIC_API_URL = "https://your-api.example.com"
```

## Notes

- The Next.js `output: 'standalone'` is set in `next.config.js` for optimal Netlify compatibility.
- Update `NEXT_PUBLIC_API_URL` in Netlify's environment variables to point at your deployed FastAPI backend.
- The FastAPI backend needs to be accessible from the Netlify deployment (ensure CORS is configured on the API).
