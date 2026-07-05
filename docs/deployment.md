# Deployment Guide

NeuroFlow is designed for multi-container deployments. We recommend Railway for its ease of managing databases and docker deployments.

## Prerequisites
- Railway CLI (`npm install -g @railway/cli`)
- A Railway account

## Steps to Deploy
1. **Initialize Project**
   ```bash
   railway login
   railway init
   ```
2. **Add Database**
   Provision a new PostgreSQL database from the Railway dashboard. Ensure pgvector extension is added.
3. **Add Redis**
   Provision a new Redis instance from the Railway dashboard.
4. **Deploy Backend API**
   - Choose to deploy from GitHub repo or local folder.
   - Point Railway to the `backend/` directory for the API build.
5. **Deploy Background Worker**
   - Same as above but override the start command to `uvicorn worker:app`.
6. **Set Environment Variables**
   Reference `.env.example` to inject all necessary variables into each Railway service.

## Rollback Procedure
If a deployment fails, use Railway's built-in rollback tool:
1. Navigate to the Service -> Deployments tab.
2. Find the previously successful deployment.
3. Click "Rollback".
4. Monitor logs to verify health.

## Live Verification
- [x] GET `https://your-app.railway.app/health` returns OK.
- [x] Pipeline processes queries correctly.
- [x] Stream `GET /query/{run_id}/stream` streams tokens.
- [x] Load tests confirm 10 concurrent users run optimally.
