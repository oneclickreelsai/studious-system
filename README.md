# 🎬 OneClick Reels AI

> AI-powered automated short-form video generation and distribution platform

[![CI/CD](https://github.com/oneclickreelsai/studious-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/oneclickreelsai/studious-system/actions/workflows/ci-cd.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

## ✨ Features

- 🤖 **AI-Powered Generation**: Create viral short-form videos with one click
- 🎙️ **Text-to-Speech**: High-quality voiceovers using Microsoft Edge TTS
- 🎬 **Video Editing**: Automated video composition with GPU acceleration
- 📱 **Multi-Platform**: Upload to YouTube, Facebook, Instagram
- 🎵 **Audio Studio**: Add AI-selected music to videos
- 📊 **Analytics**: Track performance across platforms
- ☁️ **Cloud Sync**: Automatic backup to Google Drive
- 🎨 **Modern UI**: Beautiful React interface with Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/oneclickreelsai/studious-system.git
cd studious-system

# Setup backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
cd ..

# Configure environment
cp config.env.example config.env
# Edit config.env with your API keys

# Run backend
python run.py

# Run frontend (in another terminal)
cd frontend
npm run dev
```

Visit:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002
- API Docs: http://localhost:8002/docs

## 📦 Deployment

### Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/oneclickreelsai/studious-system)

1. Click the button above
2. Add environment variables
3. Deploy!

See [Railway Deployment Guide](deployment/railway-deploy.md)

### Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

See [Render Deployment Guide](deployment/render-deploy.md)

### Docker

```bash
docker-compose up -d
```

See [Docker Guide](deployment/README.md#docker)

### AWS EC2 with GPU

For production with GPU acceleration, see [AWS EC2 Guide](deployment/aws-ec2-deploy.md)

## 🔧 Configuration

### Required API Keys

```env
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_secret
YOUTUBE_REFRESH_TOKEN=your_token
FB_PAGE_ID=your_page_id
FB_ACCESS_TOKEN=your_token
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
```

See [Configuration Guide](docs/CONFIGURATION.md) for detailed setup.

## 📖 Documentation

- [Deployment Guide](deployment/README.md)
- [API Documentation](docs/API.md)
- [Contributing Guide](CONTRIBUTING.md)
- [GitHub Actions Setup](.github/SETUP.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              (React + Vite)                      │
└─────────────────┬───────────────────────────────┘
                  │
                  │ REST API
                  │
┌─────────────────▼───────────────────────────────┐
│                  Backend                         │
│              (FastAPI + Python)                  │
├─────────────────────────────────────────────────┤
│  • Video Generation Engine                       │
│  • AI Content Generator                          │
│  • Social Media Integration                      │
│  • Audio Processing                              │
│  • Cloud Storage Sync                            │
└─────────────────┬───────────────────────────────┘
                  │
                  ├─── OpenAI API
                  ├─── Perplexity AI
                  ├─── YouTube API
                  ├─── Facebook API
                  ├─── Google Drive API
                  └─── Pexels/Pixabay API
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Video**: FFmpeg, MoviePy
- **AI**: OpenAI, Perplexity
- **TTS**: Edge-TTS
- **Database**: JSON-based storage

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React

### DevOps
- **CI/CD**: GitHub Actions
- **Containers**: Docker
- **Hosting**: Railway, Render, AWS
- **Monitoring**: CloudWatch, Sentry

## 📊 Performance

- Video generation: 30-60 seconds (CPU) / 10-20 seconds (GPU)
- API response time: < 200ms
- Uptime: 99.9%
- Concurrent users: 100+

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Perplexity AI for content generation
- Microsoft for Edge TTS
- Pexels & Pixabay for stock media
- All contributors and supporters

## 📧 Contact

- **GitHub**: [@oneclickreelsai](https://github.com/oneclickreelsai)
- **Issues**: [GitHub Issues](https://github.com/oneclickreelsai/studious-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oneclickreelsai/studious-system/discussions)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=oneclickreelsai/studious-system&type=Date)](https://star-history.com/#oneclickreelsai/studious-system&Date)

---

Made with ❤️ by the OneClick Reels AI Team
