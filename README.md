# AI Marketing Agent

A comprehensive AI-powered video content repurposing platform that transforms video content into multiple formats for different social media platforms.

## 🚀 Features

- **Multi-Platform Content Generation**: LinkedIn posts, Twitter threads, newsletters, blog posts, and video scripts
- **AI Critique Loop**: Iterative content improvement through AI-powered quality control
- **Cost Tracking**: Monitor API usage and costs across all operations
- **Real-time Processing**: Live progress tracking and status updates
- **Professional Transcription**: High-quality audio/video transcription
- **SEO Optimization**: Built-in keyword analysis and content optimization

## 🏗️ Architecture

### Backend (FastAPI)
- **Video Processing Pipeline**: Complete content transformation workflow
- **AI Agents**: Specialized agents for different content types
- **Cost Tracking**: Real-time API usage monitoring
- **Quality Control**: Multi-stage content validation

### Frontend (Next.js)
- **Modern UI**: Clean, responsive interface
- **Real-time Updates**: Live processing status
- **Settings Management**: Persistent user preferences
- **Results Dashboard**: Comprehensive result visualization

## 📁 Project Structure

```
aimarketingagent/
├── app.py                 # Main application entry point
├── backend/               # FastAPI backend application
│   ├── main.py           # Backend entry point
│   ├── requirements.txt  # Python dependencies
│   ├── core/            # Core processing logic
│   ├── agents/          # AI content agents
│   ├── services/        # Backend services
│   └── integrations/    # External integrations
├── frontend/            # Next.js frontend application
│   ├── app/            # Next.js app pages
│   ├── components/     # React components
│   ├── hooks/          # Custom React hooks
│   └── types/          # TypeScript definitions
├── scripts/            # Utility scripts
│   ├── run_app.py      # Application launcher
│   ├── setup.sh        # Setup script
│   └── monitor_logs.py # Log monitoring
├── tests/              # Test files
├── docs/               # Documentation
├── config/             # Configuration files
└── data/               # Data files
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (for local AI processing)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TheForecastCompany/aimarketingagent.git
   cd aimarketingagent
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Ollama**
   ```bash
   ollama serve
   ```

## 🚀 Running the Application

### Method 1: Using the Launcher Script
```bash
python scripts/run_app.py
```

### Method 2: Manual Startup

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Method 3: Using the Main Entry Point
```bash
python app.py
```

## 📖 Usage

1. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

2. **Configure Settings**
   - Go to Settings page
   - Enable/Disable AI Critique Loop
   - Enable/Disable Cost Tracking
   - Set brand voice preferences

3. **Process Video Content**
   - Enter YouTube URL
   - Configure processing options
   - Monitor real-time progress
   - View generated content

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# API Keys (optional)
OPENAI_API_KEY=your_openai_key
ASSEMBLYAI_KEY=your_assemblyai_key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Application Settings
DEBUG=true
LOG_LEVEL=info
```

### Settings
- **AI Critique Loop**: Enable iterative content improvement
- **Cost Tracking**: Monitor API usage and costs
- **Brand Voice**: Choose content tone (Professional, Casual, etc.)
- **Target Keywords**: SEO keywords for content optimization

## 🧪 Testing

Run tests with:
```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend && npm test
```

## 📊 Features in Detail

### AI Critique Loop
- Multi-stage content refinement
- Quality scoring and threshold checking
- Specialized critique agents (Grammar, Style, Engagement, SEO)
- Iterative improvement until quality standards met

### Cost Tracking
- Real-time API cost monitoring
- Token usage tracking
- Agent-by-agent cost breakdown
- Efficiency metrics and analytics

### Content Generation
- **LinkedIn**: Professional posts with industry insights
- **Twitter**: Engaging threads with hashtags
- **Newsletter**: Email-ready content
- **Blog**: SEO-optimized articles
- **Scripts**: Short-form video content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the configuration examples

## 🔄 Updates

- Regular updates to AI models
- New content platforms added
- Performance improvements
- Bug fixes and security patches

---

Built with ❤️ by The Forecast Company
