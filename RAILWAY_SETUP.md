# Railway Deployment Setup

## Quick Start (3 minutes)

### 1. Create Railway Account
- Go to https://railway.app
- Sign up with GitHub
- Authorize Railway to access your GitHub account

### 2. Create New Project
- Click "New Project" → "Deploy from GitHub repo"
- Search for **Makolicious/Maiko**
- Select the repository

### 3. Configure the Deployment
Railway will auto-detect the project. To deploy specifically the backend:
- Click the project
- Go to **Settings** → **Build & Deploy**
- Set these paths:
  - Root Directory: `server`
  - Build Command: `npm install`
  - Start Command: `npm start`

### 4. Add Environment Variables
In Railway project settings → **Variables**, add:

```
ALLOWED_ORIGINS=https://maiko-eight.vercel.app,http://localhost:8501
NODE_ENV=production
PORT=5000
TIMEOUT=5000
MAX_BUFFER=10485760
```

### 5. Deploy
Click **Deploy** and wait for it to complete (~2 min)

### 6. Get Your URL
Once deployed, Railway shows your public URL:
```
https://maiko-executor-production.railway.app
```

Copy this URL!

### 7. Update Vercel Environment
For your Streamlit app on Vercel:
1. Go to Vercel project settings
2. Environment Variables
3. Add: `EXECUTE_API_URL=https://your-railway-url-here.railway.app`
4. Redeploy Streamlit app

### 8. Test It Works
```bash
# Test health endpoint
curl https://your-railway-url-here.railway.app/health

# Test code execution
curl -X POST https://your-railway-url-here.railway.app/api/execute/run \
  -H "Content-Type: application/json" \
  -d '{"code":"console.log(\"test\")","language":"javascript"}'
```

---

## Automated Deployment (Optional - for future pushes)

To auto-deploy when you push to the branch:

1. Get your Railway API token:
   - Railway dashboard → Account settings → Create API Token
   - Copy the token

2. Add GitHub Secret:
   - Go to repository → Settings → Secrets and variables → Actions
   - Create new secret: `RAILWAY_TOKEN`
   - Paste your Railway token

3. Done! Future pushes to `claude/add-code-execution-layer-FDPrc` will auto-deploy

---

## Testing in Your App

Once deployed, your Maiko app will:
1. ✅ Show the "Code Execution" manual tab (for user code entry)
2. ✅ Allow Claude to autonomously execute code (agentic behavior)
3. ✅ Send code to the Railway backend for execution
4. ✅ Display results in real-time

---

## Troubleshooting

### "Cannot connect to execution server"
- Verify your EXECUTE_API_URL is correct in Vercel
- Check Railway deployment is active (green status)
- Test the health endpoint manually

### CORS Error
- Ensure `https://maiko-eight.vercel.app` is in ALLOWED_ORIGINS
- Railway logs: check for CORS rejection messages

### Code Execution Fails
- Check code doesn't contain dangerous patterns (rm -rf, sudo, etc.)
- Verify timeout is adequate (default 5s, max 30s)
- Check Railway logs for execution errors

---

Need help? Check `/home/user/Maiko/server/DEPLOYMENT.md` for detailed info.
