# Monitoring Setup

## Purpose
Periodically ping the `/api/health` endpoint to keep the FastAPI service and MongoDB connection warm, preventing cold‑starts on Render free tier and reducing latency.

## Recommended Services
- **UptimeRobot** (free tier) – configure a HTTP(s) monitor.
- **cron‑job.org** – schedule a curl request.
- Any custom cron job on a server you control.

## Configuration Steps (UptimeRobot example)
1. Sign up at https://uptimerobot.com and log in.
2. Click **Add New Monitor** → **HTTP(s)**.
3. **Monitor Name:** `Pyramyd API Health`
4. **URL:** `https://<your‑domain>/api/health`
5. **Monitoring Interval:** `5 minutes` (default minimum).
6. **Advanced Settings:**
   - Set **HTTP Method** to `GET`.
   - Enable **SSL verification** if using HTTPS.
7. Click **Create Monitor**.

## Configuration Steps (cron‑job.org example)
1. Register at https://cron-job.org.
2. Create a new **Cron Job**.
3. **Command:** `curl -s -o /dev/null -w "%{http_code}" https://<your‑domain>/api/health`
4. **Schedule:** Every `5` minutes.
5. Save the job.

## Verification
- After the first run, check the monitor logs – you should see a `200` response with JSON `{ "status": "healthy", "service": "Pyramyd API", "db": "connected" }`.
- Ensure the scheduler in the FastAPI app (`app/main.py`) logs `Health ping executed` every 5 minutes (you can add a log line inside the `health_check` function if desired).

## Optional: Custom Scheduler Logging
If you want the internal scheduler to log each ping, modify `health_check` in `app/main.py`:
```python
import logging

@app.get("/api/health")
async def health_check():
    logging.info("Health ping executed")
    ...
```

## Summary
Setting up a regular ping keeps the service responsive and avoids the 20‑30 second cold‑start delay caused by Render’s free‑tier sleep behavior.
