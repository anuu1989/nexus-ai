# 🚀 NexusAI Production Scripts Guide

## 📋 Complete Production Toolkit

Your NexusAI application now has a comprehensive set of production management scripts!

### 🎛️ **Master Control Script**
```bash
./manage-production.sh
```
**Interactive menu with all production operations:**
- 🚀 Start Production (Simple/Full/Docker)
- 🛑 Stop Production
- 📊 Check Status
- 📋 View Logs
- 🔄 Restart
- 🧹 Clean Up
- ⚙️ Configuration Help

---

## 🔧 Individual Scripts

### **1. Simple Production Start**
```bash
./run-prod-simple.sh
```
**What it does:**
- ✅ Quick production deployment
- ✅ Gunicorn WSGI server with 4 workers
- ✅ Production logging to `logs/` directory
- ✅ Environment validation
- ✅ Optimized for immediate deployment

**Best for:** Quick testing, development, small deployments

### **2. Full Production Setup**
```bash
./run-production.sh
```
**What it does:**
- ✅ Complete production environment setup
- ✅ Dependency management with production packages
- ✅ Security configuration
- ✅ Multiple deployment options (Gunicorn/Systemd/Docker)
- ✅ Nginx configuration generation
- ✅ SSL/TLS setup assistance
- ✅ Monitoring and logging setup

**Best for:** Production servers, enterprise deployments

### **3. Production Stop**
```bash
./stop-production.sh
```
**What it does:**
- ✅ Gracefully stops all NexusAI processes
- ✅ Handles multiple deployment methods
- ✅ Cleans up PID files and stale processes
- ✅ Comprehensive process detection
- ✅ Safe shutdown procedures

### **4. Status Check**
```bash
./status-production.sh
```
**What it does:**
- ✅ Shows all running NexusAI processes
- ✅ Checks application health
- ✅ Network port status
- ✅ Log file information
- ✅ System resource usage
- ✅ Quick troubleshooting info

---

## 🐳 Docker Production

### **Basic Docker Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **Full Stack with Nginx**
```bash
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### **Complete with Monitoring**
```bash
docker-compose -f docker-compose.prod.yml --profile with-nginx --profile with-monitoring up -d
```

---

## ⚙️ Configuration Files

### **Environment Configuration**
- **`.env.production`** - Production environment template
- **`.env`** - Your actual configuration (copy from template)

### **Docker Configuration**
- **`docker-compose.prod.yml`** - Production Docker setup
- **`nexusai.service`** - Systemd service file (auto-generated)
- **`nexusai-nginx.conf`** - Nginx configuration (auto-generated)

---

## 🚀 Quick Start Guide

### **1. First Time Setup**
```bash
# Copy environment template
cp .env.production .env

# Edit with your values (required!)
nano .env  # or your preferred editor

# Set your API keys:
# GROQ_API_KEY=<your-actual-api-key>
# SECRET_KEY=<your-secure-secret-key>
```

### **2. Choose Your Deployment Method**

#### **🏃‍♂️ Quick & Simple (Recommended)**
```bash
./run-prod-simple.sh
```

#### **🎛️ Interactive Management**
```bash
./manage-production.sh
```

#### **🏭 Full Production Setup**
```bash
./run-production.sh
```

#### **🐳 Docker Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoring & Management

### **Check Status**
```bash
./status-production.sh
# or
./manage-production.sh  # Choose option 5
```

### **View Logs**
```bash
# Real-time logs
tail -f logs/access.log logs/error.log

# Recent logs
./manage-production.sh  # Choose option 6
```

### **Stop Server**
```bash
./stop-production.sh
# or
./manage-production.sh  # Choose option 4
```

### **Restart Server**
```bash
./manage-production.sh  # Choose option 7
# or manually:
./stop-production.sh && ./run-prod-simple.sh
```

---

## 🛡️ Security Checklist

### **Before Production Deployment:**
- [ ] **Set secure SECRET_KEY** in `.env`
- [ ] **Configure GROQ_API_KEY** in `.env`
- [ ] **Set up HTTPS/SSL** certificates
- [ ] **Configure firewall** (allow only 80, 443, 22)
- [ ] **Update CORS_ORIGINS** with your domain
- [ ] **Enable rate limiting** (RATE_LIMIT_ENABLED=True)
- [ ] **Secure session cookies** (SESSION_COOKIE_SECURE=True)

### **After Deployment:**
- [ ] **Test application** at http://localhost:5000
- [ ] **Check logs** for errors
- [ ] **Monitor resource usage**
- [ ] **Set up automated backups**
- [ ] **Configure monitoring alerts**

---

## 🚨 Troubleshooting

### **Application Won't Start**
```bash
# Check configuration
./status-production.sh

# Check logs
tail -f logs/error.log

# Validate environment
python backend/app.py
```

### **Port Already in Use**
```bash
# Find what's using port 5000
netstat -tlnp | grep :5000
# or
ss -tlnp | grep :5000

# Stop conflicting process
./stop-production.sh
```

### **Permission Errors**
```bash
# Fix script permissions
chmod +x *.sh

# Fix log directory permissions
mkdir -p logs
chmod 755 logs
```

### **Environment Issues**
```bash
# Check if .env exists
ls -la .env

# Validate required variables
grep -E "GROQ_API_KEY|SECRET_KEY" .env
```

---

## 📈 Performance Optimization

### **Adjust Workers**
Edit `.env`:
```env
WORKERS=4  # Adjust based on CPU cores
GUNICORN_WORKERS=4
```

### **Database Optimization**
For production, consider PostgreSQL:
```env
DATABASE_URL=<your-database-connection-string>
```

### **Caching**
Enable Redis caching:
```env
REDIS_URL=<your-redis-connection-string>
```

### **Static Files**
Use Nginx for static file serving (auto-configured in full setup).

---

## 🎉 Success!

Your NexusAI application is now production-ready with:

- ✅ **Multiple deployment options** for different needs
- ✅ **Comprehensive management scripts** for easy operation
- ✅ **Production-grade security** configuration
- ✅ **Monitoring and logging** capabilities
- ✅ **Docker containerization** support
- ✅ **Automated setup and teardown**
- ✅ **Interactive management interface**

**🌟 Access your production NexusAI at: http://localhost:5000**

---

## 📞 Need Help?

1. **Check the logs:** `tail -f logs/error.log`
2. **Run status check:** `./status-production.sh`
3. **Use interactive manager:** `./manage-production.sh`
4. **Read full guide:** `PRODUCTION_DEPLOYMENT.md`

**Happy deploying! 🚀✨**