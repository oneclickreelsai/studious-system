# Deploy to AWS EC2 with GPU - Production Setup

## Overview
This guide helps you deploy OneClick Reels AI on AWS EC2 with GPU support for maximum performance.

## Prerequisites
- AWS account
- Basic knowledge of AWS services
- SSH key pair

## Step 1: Launch EC2 Instance

### Instance Configuration
- **Instance Type**: g4dn.xlarge (or g4dn.2xlarge for better performance)
- **AMI**: Deep Learning AMI (Ubuntu 20.04) - has CUDA pre-installed
- **Storage**: 100GB EBS (gp3)
- **Security Group**: 
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
  - Port 8002 (Backend API)

### Cost Estimate
- g4dn.xlarge: ~$0.526/hour (~$380/month)
- g4dn.2xlarge: ~$0.752/hour (~$540/month)

## Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install FFmpeg with NVIDIA support
sudo apt install ffmpeg -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y
```

## Step 4: Clone Repository

```bash
cd /home/ubuntu
git clone YOUR_GITHUB_REPO_URL oneclick-reels
cd oneclick-reels
```

## Step 5: Setup Backend

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create config.env
nano config.env
# Add all your API keys

# Create directories
mkdir -p output logs data cache assets/videos assets/music
```

## Step 6: Setup Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

## Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/oneclick-reels
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /home/ubuntu/oneclick-reels/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Output files
    location /output {
        alias /home/ubuntu/oneclick-reels/output;
        autoindex off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/oneclick-reels /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: Setup Systemd Service

```bash
sudo nano /etc/systemd/system/oneclick-reels.service
```

Add:

```ini
[Unit]
Description=OneClick Reels AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/oneclick-reels
Environment="PATH=/home/ubuntu/oneclick-reels/venv/bin"
ExecStart=/home/ubuntu/oneclick-reels/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oneclick-reels
sudo systemctl start oneclick-reels
sudo systemctl status oneclick-reels
```

## Step 9: Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Step 10: Verify GPU Access

```bash
# Check NVIDIA driver
nvidia-smi

# Test FFmpeg with NVENC
ffmpeg -encoders | grep nvenc
```

## Monitoring

### Setup CloudWatch

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Monitor Logs

```bash
# Backend logs
sudo journalctl -u oneclick-reels -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Backup Strategy

### Automated Backups

```bash
# Create backup script
nano /home/ubuntu/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp /home/ubuntu/oneclick-reels/data/database.json $BACKUP_DIR/database_$DATE.json

# Backup output folder (optional - can be large)
# tar -czf $BACKUP_DIR/output_$DATE.tar.gz /home/ubuntu/oneclick-reels/output

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/database_$DATE.json s3://your-bucket/backups/

# Keep only last 7 days
find $BACKUP_DIR -name "database_*.json" -mtime +7 -delete
```

```bash
chmod +x /home/ubuntu/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh
```

## Security Hardening

```bash
# Setup firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd

# Setup fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

## Performance Optimization

### Enable GPU Monitoring

```bash
# Install nvidia-smi monitoring
watch -n 1 nvidia-smi
```

### Optimize FFmpeg

Edit video generation code to use:
- h264_nvenc for encoding
- CUDA hardware acceleration
- Optimal preset (p7 for quality)

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall if needed
sudo apt install nvidia-driver-525 -y
sudo reboot
```

### Service Won't Start
```bash
# Check logs
sudo journalctl -u oneclick-reels -n 50

# Check permissions
ls -la /home/ubuntu/oneclick-reels

# Test manually
cd /home/ubuntu/oneclick-reels
source venv/bin/activate
python run.py
```

### High Memory Usage
```bash
# Monitor resources
htop

# Restart service
sudo systemctl restart oneclick-reels
```

## Cost Optimization

1. Use Spot Instances (60-90% cheaper)
2. Stop instance when not in use
3. Use Reserved Instances for long-term
4. Monitor with AWS Cost Explorer

## Scaling

For high traffic:
1. Use Application Load Balancer
2. Deploy multiple instances
3. Use Auto Scaling Groups
4. Add Redis for caching
5. Use S3 for video storage

## Support

- AWS docs: https://docs.aws.amazon.com
- NVIDIA docs: https://docs.nvidia.com
- GitHub Issues: [Your repo URL]
