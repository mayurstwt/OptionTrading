# NETLIFY DEPLOYMENT GUIDE: Complete Step-by-Step

**Purpose**: Deploy Next.js frontend to Netlify in 10 minutes  
**Cost**: Free tier available  
**Time**: 10 minutes setup + 2 minutes per deploy  

---

## PREREQUISITES

You need:
- [ ] GitHub account (for code hosting)
- [ ] Netlify account (free)
- [ ] Next.js frontend code (ready to commit)
- [ ] Backend API running (or will run on VPS)

---

## STEP 1: PREPARE CODE FOR DEPLOYMENT

### 1.1 Update package.json

```json
{
  "name": "options-trading-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "recharts": "^2.10.0",
    "tailwindcss": "^3.3.0",
    "@shadcn/ui": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

### 1.2 Create netlify.toml

```toml
[build]
  # Build command
  command = "npm run build"
  
  # Where to put built files
  publish = ".next/public"
  
  # Functions directory (if using serverless functions)
  functions = "netlify/functions"

# Redirect API routes to serverless functions
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

# Rewrite for SPA routing
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Cache headers
[[headers]]
  for = "/_next/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/api/*"
  [headers.values]
    Cache-Control = "no-cache"
    Access-Control-Allow-Origin = "*"
    Access-Control-Allow-Methods = "GET, POST, PUT, DELETE, OPTIONS"
    Access-Control-Allow-Headers = "Content-Type"
```

### 1.3 Create next.config.ts

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enable static optimization
  reactStrictMode: true,
  
  // Image optimization
  images: {
    unoptimized: process.env.NODE_ENV === 'development',
  },
  
  // Environment variables (accessible to frontend)
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    NEXT_PUBLIC_API_TIMEOUT: '30000',
  },

  // Headers for Netlify
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        {
          key: 'Access-Control-Allow-Origin',
          value: '*',
        },
      ],
    },
  ],
};

export default nextConfig;
```

### 1.4 Create .gitignore

```
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/
dist/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## STEP 2: CREATE GITHUB REPOSITORY

### 2.1 Initialize Git (if not already done)

```bash
cd frontend/
git init
git add .
git commit -m "Initial commit: Next.js trading dashboard"
```

### 2.2 Create GitHub Repository

```bash
# Option A: Using GitHub CLI
gh repo create trading-engine-frontend --public --source=. --remote=origin --push

# Option B: Manual
# 1. Go to https://github.com/new
# 2. Create repo: "trading-engine-frontend"
# 3. Run:
git remote add origin https://github.com/YOUR_USERNAME/trading-engine-frontend.git
git branch -M main
git push -u origin main
```

### 2.3 Verify on GitHub

```
https://github.com/YOUR_USERNAME/trading-engine-frontend
```

---

## STEP 3: CONNECT TO NETLIFY

### 3.1 Sign Up / Log In

```
1. Go to https://netlify.com
2. Click "Sign up"
3. Choose "GitHub" authentication
4. Authorize Netlify to access your GitHub
```

### 3.2 Create New Site

```
1. In Netlify dashboard, click "New site from Git"
2. Select GitHub
3. Search for "trading-engine-frontend" repo
4. Click "Install and authorize"
```

### 3.3 Configure Build Settings

```
Build settings screen:

Branch to deploy: main

Build command: npm run build

Publish directory: .next/public

(These should auto-fill based on next.config.ts, 
 but you may need to adjust)
```

### 3.4 Deploy

```
1. Review settings
2. Click "Deploy site"
3. Wait for build to complete (usually 1-2 minutes)
4. You'll get a URL: https://[random-name].netlify.app
```

---

## STEP 4: CONFIGURE ENVIRONMENT VARIABLES

### 4.1 In Netlify Dashboard

```
1. Go to Site settings
2. Click "Build & deploy" → "Environment"
3. Add environment variables:

Key:   NEXT_PUBLIC_BACKEND_URL
Value: https://your-backend-vps-ip:port/
(or http://localhost:8000 for local testing)

Key:   NEXT_PUBLIC_API_TIMEOUT
Value: 30000

Key:   NEXT_PUBLIC_POLLING_INTERVAL
Value: 5000
```

### 4.2 Re-deploy with Environment Variables

```
1. Go to Deploys
2. Click on latest deploy
3. Click "Retry deploy"
4. Wait for new build (with env vars)
```

---

## STEP 5: SETUP CUSTOM DOMAIN (OPTIONAL)

### 5.1 Connect Custom Domain

```
1. Go to Site settings → Domain management
2. Add custom domain
3. Follow DNS setup instructions for your registrar

Example:
  Domain: trading-dashboard.com
  DNS Records:
    Type: ALIAS
    Name: @
    Value: [your-netlify-dns]
```

### 5.2 Enable HTTPS

```
Netlify auto-enables HTTPS with Let's Encrypt
(usually within 1 hour of DNS setup)
```

---

## STEP 6: CONFIGURE CORS FOR BACKEND

### 6.1 Backend CORS Setup

Your backend needs to allow requests from Netlify:

```python
# In backend (main.py or FastAPI app)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local dev
        "https://your-netlify-domain.netlify.app",  # Production
        "https://your-custom-domain.com"  # If custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.2 Or use Netlify Edge Functions as Proxy

If backend CORS is problematic:

```typescript
// netlify/functions/api.ts
export default async (request) => {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  const response = await fetch(`${backendUrl}${request.url}`);
  return response;
};
```

---

## STEP 7: SET UP AUTO-DEPLOYS

### 7.1 GitHub Integration (Automatic)

```
Every push to 'main' branch automatically:
1. Triggers Netlify build
2. Runs: npm run build
3. Deploys to https://[your-site].netlify.app
4. Takes ~2-3 minutes

You can watch progress in Netlify dashboard:
Deploys section → Build logs
```

### 7.2 Disable Auto-Deploy (Optional)

```
1. Site settings → Build & deploy → Deploy contexts
2. Set "main" → "Deploy only" (not auto-deploy)
3. Manual deploy with: netlify deploy
```

---

## STEP 8: VERIFY DEPLOYMENT

### 8.1 Check Frontend

```
1. Go to https://[your-site].netlify.app
2. Should see dashboard loading
3. Check browser console (F12) for errors
```

### 8.2 Check API Connectivity

```
Browser console:
  fetch('/api/market-data')
    .then(r => r.json())
    .then(d => console.log(d))

Should return market data from backend
If error: check NEXT_PUBLIC_BACKEND_URL in env vars
```

### 8.3 Check Build Logs

```
Netlify dashboard → Deploys → Latest deploy → Build logs

Look for:
  ✓ Dependencies installed
  ✓ Next.js build successful
  ✓ Deploy complete
  
If errors: check error messages
```

---

## STEP 9: SETUP MONITORING

### 9.1 Enable Analytics

```
In Netlify:
1. Site settings → Analytics
2. Enable Site Analytics
3. View traffic, errors, performance
```

### 9.2 Setup Alerts

```
1. Netlify dashboard → Site settings → Notifications
2. Add notification:
   - Event: Deploy failed
   - Channel: Email
   - Address: your-email@example.com
```

### 9.3 Monitor Backend Connectivity

```
Add health check to frontend:

// lib/health.ts
export async function checkBackendHealth() {
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/health`,
      { timeout: 5000 }
    );
    return res.ok;
  } catch {
    return false;
  }
}

// Use in Dashboard
function Dashboard() {
  const [healthy, setHealthy] = useState(true);
  
  useEffect(() => {
    checkBackendHealth().then(setHealthy);
  }, []);
  
  return (
    <div>
      {!healthy && (
        <Alert type="error">
          Backend unreachable
        </Alert>
      )}
    </div>
  );
}
```

---

## STEP 10: UPDATE README WITH DEPLOYMENT INFO

```markdown
# Trading Dashboard Frontend

## Deployment

Deployed on Netlify: https://[your-site].netlify.app

### Environment Variables

Required in Netlify dashboard:
- NEXT_PUBLIC_BACKEND_URL: Backend API URL
- NEXT_PUBLIC_API_TIMEOUT: Timeout in ms (default 30000)
- NEXT_PUBLIC_POLLING_INTERVAL: Poll interval in ms (default 5000)

### Deploy from GitHub

1. Push to main branch
2. Netlify auto-builds and deploys
3. View status in Netlify dashboard

### Manual Deploy

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

### Custom Domain

To use custom domain:
1. Add domain in Site settings → Domain management
2. Follow DNS instructions for your registrar
3. Wait for HTTPS certificate (usually 1 hour)
```

---

## TROUBLESHOOTING

### Problem: Build fails

```
Check:
1. package.json has all dependencies
2. next.config.ts is valid
3. All imports are correct
4. TypeScript errors: npm run build locally

Solution:
1. Fix errors locally
2. Push to GitHub
3. Netlify will rebuild automatically
```

### Problem: API requests fail

```
Check:
1. NEXT_PUBLIC_BACKEND_URL is correct
2. Backend is running
3. Backend CORS allows Netlify origin
4. Network tab in DevTools (F12)

Solution:
Add console logging:
  const url = process.env.NEXT_PUBLIC_BACKEND_URL;
  console.log('API URL:', url);
  fetch(url + '/api/health')
```

### Problem: Pages show 404

```
Check:
1. All page.tsx files are in correct directories
2. Routes match expected paths
3. Netlify redirects are configured

Solution:
```

---

## PERFORMANCE TIPS

### 1. Enable Image Optimization

```typescript
import Image from 'next/image';

// Auto-optimized
<Image src="/logo.png" width={100} height={100} />
```

### 2. Code Splitting

```typescript
import dynamic from 'next/dynamic';

const Analytics = dynamic(() => import('./analytics'), {
  loading: () => <Spinner />
});
```

### 3. Caching

```
Static pages:
- Built once, served globally
- ISR (Incremental Static Regeneration) for updates

Dynamic pages:
- Server-side render
- Consider SWR for client-side caching
```

### 4. Monitoring

```
Netlify Analytics shows:
- Page load times
- Slow endpoint identification
- Traffic patterns
- Error tracking
```

---

## NEXT STEPS

1. ✅ Deploy frontend to Netlify
2. ✅ Verify API connectivity
3. ✅ Setup custom domain (optional)
4. ✅ Configure monitoring
5. → Start backend trading engine
6. → Monitor in real-time from dashboard

---

## QUICK REFERENCE

```bash
# Local development
npm run dev
# Visit: http://localhost:3000

# Build for production
npm run build

# Serve production build locally
npm start

# Deploy to Netlify (CLI)
npm i -g netlify-cli
netlify deploy --prod

# View logs
netlify logs
```

---

## SUPPORT

**Issues?**

1. Check Netlify documentation: https://docs.netlify.com
2. Check Next.js documentation: https://nextjs.org/docs
3. Check build logs in Netlify dashboard
4. Check browser console (F12) for errors

**Common URLs:**

- Frontend: https://[your-site].netlify.app
- Backend API: https://[your-vps]:8000
- Netlify dashboard: https://app.netlify.com
- GitHub repo: https://github.com/[username]/trading-engine-frontend

---

**Version**: 1.0.0  
**Last Updated**: May 6, 2024  
**Status**: ✅ Ready to Deploy

