# KrishiVani - Deployment Guide

This guide covers deploying KrishiVani to production on various platforms.

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] `.env` file is in `.gitignore` (not committed)
- [ ] Error handling tested
- [ ] Logging configured
- [ ] API rate limits understood
- [ ] Monitoring setup planned

## Local Production Testing

Before deploying, test locally with production settings:

```bash
# Set to production
export FLASK_ENV=production  # Linux/macOS
set FLASK_ENV=production     # Windows

# Run without debug mode
python twilio_app.py
python telegram_app.py
```

## Deployment Platforms

### Option 1: Render (Recommended for Beginners)

**Telegram Bot:**
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Create new Web Service
4. Set environment variables in Render dashboard
5. Deploy

**WhatsApp Server:**
1. Same as above
2. Get public URL from Render
3. Use as `NGROK_URL` in `.env`

### Option 2: Railway.app

**Setup:**
```bash
# Install railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Configure:**
1. Add environment variables in Railway dashboard
2. Get public URL
3. Configure Twilio webhook

### Option 3: Heroku (Free tier deprecated, but still available)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set GROQ_API_KEY=your_key

# Deploy
git push heroku main
```

### Option 4: VPS (DigitalOcean, Linode, AWS EC2)

**Initial Setup:**
```bash
# SSH into your VPS
ssh root@your_vps_ip

# Update system
apt update && apt upgrade -y

# Install Python & Git
apt install python3 python3-pip git -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/KrishiVani.git
cd KrishiVani

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env  # Add your credentials
```

**Run with Systemd (Permanent Service):**

Create `/etc/systemd/system/krishivani-telegram.service`:
```ini
[Unit]
Description=KrishiVani Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/KrishiVani
ExecStart=/root/KrishiVani/.venv/bin/python telegram_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/krishivani-whatsapp.service`:
```ini
[Unit]
Description=KrishiVani WhatsApp Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/KrishiVani
ExecStart=/root/KrishiVani/.venv/bin/python twilio_app.py
Restart=always
RestartSec=10
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
```

**Enable services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable krishivani-telegram.service
sudo systemctl enable krishivani-whatsapp.service
sudo systemctl start krishivani-telegram.service
sudo systemctl start krishivani-whatsapp.service

# Check status
sudo systemctl status krishivani-telegram.service
sudo systemctl status krishivani-whatsapp.service

# View logs
sudo journalctl -u krishivani-telegram.service -f
```

## Environment Variables for Production

```env
# Required
TELEGRAM_BOT_TOKEN=your_token_here
GROQ_API_KEY=your_key_here

# For WhatsApp
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
NGROK_URL=https://your-public-url.com

# Production Settings
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=INFO
```

## Using Reverse Proxy (Nginx)

For VPS deployments, use Nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /webhook {
        proxy_pass http://127.0.0.1:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup

Using Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

Update Nginx config to use SSL:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring

### Application Logs

Enable rotating logs in `twilio_app.py`:
```python
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler('app.log', maxBytes=10485760, backupCount=10)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
```

### Health Check Endpoint

Add to `twilio_app.py`:
```python
@app.route("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

Setup monitoring (e.g., UptimeRobot):
- Check `https://your-domain.com/health` every 5 minutes
- Alert if down for more than 5 minutes

### Database Backup

For SQLite (if used):
```bash
# Daily backup cron job
0 2 * * * cp /path/to/database.db /backup/database-$(date +\%Y\%m\%d).db
```

## Performance Tips

1. **Use Gunicorn for production:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 twilio_app:app
   ```

2. **Enable caching:**
   - Cache model predictions
   - Cache language detection results

3. **Rate limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: "global")
   
   @app.route("/webhook", methods=["POST"])
   @limiter.limit("100/hour")
   def webhook():
       # ...
   ```

4. **Database optimization:**
   - Use connection pooling
   - Index frequently queried fields

## Troubleshooting

### Bot not responding
- Check API credentials
- Verify internet connection
- Check logs for errors
- Ensure service is running: `systemctl status krishivani-telegram`

### WhatsApp webhook not receiving messages
- Verify Twilio webhook URL is correct
- Check webhook URL is publicly accessible
- Verify HTTPS/SSL certificate
- Check Twilio logs in dashboard

### High CPU usage
- Check model prediction performance
- Review API rate limits
- Consider caching results
- Check for infinite loops in logs

### Memory issues
- Limit concurrent requests
- Clear temporary files regularly
- Monitor with `free -m` (Linux)
- Use memory profiler: `pip install memory-profiler`

## Scaling Strategies

For high traffic:

1. **Load Balancing:**
   - Deploy multiple instances
   - Use load balancer (Nginx, HAProxy)
   - Share session state (Redis)

2. **Caching:**
   - Redis for model predictions
   - Database query caching

3. **Job Queues:**
   - Celery for async processing
   - Separate worker processes

4. **Database:**
   - Move from SQLite to PostgreSQL
   - Add read replicas
   - Implement partitioning

## Cost Optimization

- **Groq API:** Monitor usage, set limits
- **Twilio:** Use trial credits wisely
- **Hosting:** Choose appropriate tier
- **Bandwidth:** Compress audio/images

## Security Best Practices

1. Never commit `.env` file
2. Use strong, unique API keys
3. Rotate credentials periodically
4. Monitor for suspicious activity
5. Keep dependencies updated: `pip install --upgrade -r requirements.txt`
6. Use HTTPS/SSL everywhere
7. Implement input validation
8. Log security events

## Recovery Plan

1. **Backups:**
   - Auto-backup database daily
   - Store in separate location

2. **Disaster Recovery:**
   - Document deployment process
   - Keep recovery playbook updated
   - Test recovery procedure monthly

3. **Rollback Procedure:**
   ```bash
   git log --oneline
   git revert <commit-hash>
   git push
   # Redeploy
   ```

---

For additional help, check platform-specific documentation or open an issue on GitHub.
