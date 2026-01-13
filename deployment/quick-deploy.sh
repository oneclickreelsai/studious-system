#!/bin/bash

# OneClick Reels AI - Quick Deployment Script
# This script helps you deploy to various platforms

echo "=================================="
echo "OneClick Reels AI - Quick Deploy"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
fi

echo "Select deployment platform:"
echo "1) Railway (Recommended - Easiest)"
echo "2) Render (Good for startups)"
echo "3) Docker (Local/Self-hosted)"
echo "4) AWS EC2 (Production with GPU)"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Deploying to Railway..."
        echo "=================================="
        echo ""
        echo "Steps:"
        echo "1. Push your code to GitHub"
        echo "2. Go to https://railway.app"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select your repository"
        echo "5. Add environment variables in Railway dashboard"
        echo ""
        echo "Required environment variables:"
        echo "- OPENAI_API_KEY"
        echo "- PERPLEXITY_API_KEY"
        echo "- YOUTUBE_CLIENT_ID"
        echo "- YOUTUBE_CLIENT_SECRET"
        echo "- YOUTUBE_REFRESH_TOKEN"
        echo "- FB_PAGE_ID"
        echo "- FB_ACCESS_TOKEN"
        echo "- PEXELS_API_KEY"
        echo "- PIXABAY_API_KEY"
        echo ""
        read -p "Push to GitHub now? (y/n): " push
        if [ "$push" = "y" ]; then
            read -p "Enter GitHub repository URL: " repo_url
            git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url
            git push -u origin main
            echo ""
            echo "Code pushed! Now go to Railway and deploy."
        fi
        ;;
    
    2)
        echo ""
        echo "Deploying to Render..."
        echo "=================================="
        echo ""
        echo "Steps:"
        echo "1. Push your code to GitHub"
        echo "2. Go to https://render.com"
        echo "3. Click 'New +' → 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Configure build and start commands"
        echo "6. Add environment variables"
        echo ""
        echo "See deployment/render-deploy.md for detailed instructions"
        echo ""
        read -p "Push to GitHub now? (y/n): " push
        if [ "$push" = "y" ]; then
            read -p "Enter GitHub repository URL: " repo_url
            git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url
            git push -u origin main
            echo ""
            echo "Code pushed! Now go to Render and deploy."
        fi
        ;;
    
    3)
        echo ""
        echo "Building Docker containers..."
        echo "=================================="
        echo ""
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "Docker is not installed. Please install Docker first."
            echo "Visit: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        # Check if docker-compose is installed
        if ! command -v docker-compose &> /dev/null; then
            echo "docker-compose is not installed. Please install it first."
            echo "Visit: https://docs.docker.com/compose/install/"
            exit 1
        fi
        
        echo "Building and starting containers..."
        docker-compose up -d --build
        
        echo ""
        echo "Deployment complete!"
        echo "Backend: http://localhost:8002"
        echo "Frontend: http://localhost:5173"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;
    
    4)
        echo ""
        echo "AWS EC2 Deployment"
        echo "=================================="
        echo ""
        echo "This requires manual setup. Please follow the guide:"
        echo "deployment/aws-ec2-deploy.md"
        echo ""
        echo "Quick summary:"
        echo "1. Launch EC2 instance (g4dn.xlarge for GPU)"
        echo "2. SSH into instance"
        echo "3. Clone repository"
        echo "4. Run setup script"
        echo "5. Configure Nginx"
        echo "6. Setup SSL"
        echo ""
        ;;
    
    5)
        echo "Exiting..."
        exit 0
        ;;
    
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "Deployment process initiated!"
echo "=================================="
echo ""
echo "For detailed instructions, see:"
echo "- deployment/README.md"
echo "- deployment/railway-deploy.md"
echo "- deployment/render-deploy.md"
echo "- deployment/aws-ec2-deploy.md"
echo ""
