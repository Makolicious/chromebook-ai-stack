# Code Execution Server - Deployment Guide

This Node.js backend handles code execution for the Maiko AI application. It can be deployed to various platforms.

## Deployment to Railway (Recommended)

Railway is the simplest platform for deploying this Node.js backend.

### Steps:

1. **Create a Railway Account**
   - Visit https://railway.app
   - Sign up with GitHub

2. **Connect Your Repository**
   - Link your GitHub repository to Railway
   - Railway will auto-detect the Node.js project

3. **Add Environment Variables**
   - In Railway dashboard, go to the project settings
   - Add the following environment variables:
     ```
     PORT=5000
     NODE_ENV=production
     ALLOWED_ORIGINS=https://maiko-eight.vercel.app,http://localhost:8501
     TIMEOUT=5000
     MAX_BUFFER=10485760
     ```

4. **Configure Build & Deploy**
   - Railway will automatically detect package.json
   - Build command: `npm install`
   - Start command: `npm start`

5. **Get Your Deployment URL**
   - Railway provides a unique URL like: `https://maiko-api-production.railway.app`
   - Copy this URL

6. **Update Streamlit App**
   - Set the environment variable in your Streamlit deployment:
     ```
     EXECUTE_API_URL=https://maiko-api-production.railway.app
     ```

## Deployment to Other Platforms

### Render.com
- Similar to Railway, supports Node.js
- Create a new Web Service from GitHub
- Set start command: `npm start`
- Add the same environment variables

### Vercel (with serverless functions)
- Can deploy Node.js as serverless functions
- Create `api/execute.js` file for serverless endpoint
- Less suitable for this use case due to timeout limits

## Local Testing

Before deploying, test locally:

```bash
cd server
npm install
npm start
```

The server will run on http://localhost:5000

Test the health endpoint:
```bash
curl http://localhost:5000/health
```

Test code execution:
```bash
curl -X POST http://localhost:5000/api/execute/run \
  -H "Content-Type: application/json" \
  -d '{"code":"console.log(\"Hello, World!\")","language":"javascript"}'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 5000 | Server port |
| NODE_ENV | development | Environment (development/production) |
| ALLOWED_ORIGINS | http://localhost:3000 | CORS allowed origins (comma-separated) |
| TIMEOUT | 5000 | Code execution timeout in ms |
| MAX_BUFFER | 10485760 | Max output buffer size |

## Security Considerations

- The server validates and sanitizes all code before execution
- CORS is restricted to allowed origins
- Code execution has timeout limits to prevent resource exhaustion
- Dangerous commands are rejected (rm -rf, sudo, etc.)

## Troubleshooting

### Connection Refused
- Check if the backend server is running
- Verify the EXECUTE_API_URL is correct in the Streamlit app
- Check CORS settings in .env

### CORS Errors
- Ensure your Streamlit URL is in ALLOWED_ORIGINS
- Example: `https://maiko-eight.vercel.app`

### Execution Timeouts
- Increase TIMEOUT value in environment variables (max recommended: 30000)
- Check if code is too resource-intensive
