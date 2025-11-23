# Interview Prep AI 🎯

An AI-powered desktop/web application for comprehensive interview preparation, built with **Flet** UI framework and **MySQL** database.

## ✨ Features

### 📄 Profile Analysis
- Upload resume (PDF, DOCX, TXT)
- Paste or upload job descriptions
- AI-powered compatibility analysis (0-100% score)
- Matched and missing skills identification
- Improvement suggestions

### 💼 Job Opportunities (JSearch Integration)
- Real-time job search from multiple sources
- Automatic compatibility ranking with your resume
- Remote job filtering
- Save jobs for later
- View detailed job descriptions

### 🎯 Settings & LLM Configuration
- Support for multiple LLM providers:
  - **OpenAI** (GPT-4, GPT-3.5)
  - **Anthropic** (Claude 3 Opus, Sonnet, Haiku)
  - **AWS Bedrock** (Claude, Titan, etc.)
  - **Ollama** (Local LLMs: Llama 3, Mistral, Phi-3)
- Configurable temperature and max tokens
- API key encryption
- Test connection functionality

### 🚧 Coming Soon
- Interview Questions Generator
- Practice Sessions (Written/Audio/Video)
- Document Writer (Resume, Cover Letter, Cold Email)
- Application Planner & Tracker
- AI Career Coach (Agentic System)

## 🚀 Installation

### Prerequisites
- **Python 3.9+**
- **MySQL 8.0+** (running locally or remotely)
- API keys for your chosen LLM provider (optional for Ollama)

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd interview_prep_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file in the project root (copy from `.env.example`):

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=interview_prep_ai
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password

# API Keys (at least one required)
JSEARCH_API_KEY=your_jsearch_rapidapi_key  # For job search
OPENAI_API_KEY=your_openai_api_key         # For OpenAI
ANTHROPIC_API_KEY=your_anthropic_api_key   # For Claude
AWS_ACCESS_KEY_ID=your_aws_key             # For Bedrock
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

# Ollama (if using local LLMs)
OLLAMA_BASE_URL=http://localhost:11434

# App Configuration
APP_SECRET_KEY=your_random_secret_key_here
DEBUG_MODE=True
DEFAULT_USER_ID=1
```

### Step 3: Initialize Database

```bash
# Create database and tables automatically
python database/create_db.py
```

You should see output like:
```
🚀 Starting database setup...
✓ Database 'interview_prep_ai' created/verified
✓ All tables created successfully
✓ Indexes created successfully
✓ Default user created
✅ Database setup completed successfully!
```

### Step 4: Run the Application

```bash
# Start the Flet application
python main.py
```

The application will open in a new window (desktop app mode) or your browser (web mode).

## 📁 Project Structure

```
interview_prep_ai/
├── main.py                          # Flet app entry point
├── requirements.txt                 # Python dependencies
├── .env                            # Environment configuration
├── .env.example                    # Example environment file
│
├── config/
│   ├── settings.py                 # App settings
│   └── prompts.py                  # LLM prompts library
│
├── database/
│   ├── connection.py               # Database connection pool
│   ├── create_db.py                # Auto database setup script
│   └── migrations/
│       ├── 001_initial_schema.sql  # Database schema
│       └── 002_add_indexes.sql     # Performance indexes
│
├── core/
│   ├── document_parser.py          # PDF/DOCX/TXT parsing
│   ├── text_extractor.py           # Text extraction utilities
│   ├── encryption.py               # API key encryption
│   ├── auth.py                     # Authentication (simple)
│   └── validators.py               # Input validation
│
├── ai/
│   └── providers/
│       ├── base_provider.py        # Abstract LLM provider
│       ├── openai_provider.py      # OpenAI implementation
│       ├── anthropic_provider.py   # Anthropic implementation
│       ├── bedrock_provider.py     # AWS Bedrock implementation
│       └── ollama_provider.py      # Ollama implementation
│
├── services/
│   ├── llm_service.py              # LLM provider management
│   ├── resume_service.py           # Resume operations
│   ├── jd_service.py               # Job description operations
│   ├── compatibility_service.py    # Compatibility analysis
│   ├── question_service.py         # Question generation
│   ├── practice_service.py         # Practice sessions
│   ├── jsearch_service.py          # JSearch API integration
│   ├── document_service.py         # Document generation
│   └── application_service.py      # Application tracking
│
├── ui/
│   ├── components/
│   │   ├── navigation.py           # Navigation rail
│   │   ├── file_uploader.py        # File upload component
│   │   ├── score_card.py           # Score display
│   │   └── job_card.py             # Job listing card
│   ├── views/
│   │   ├── home_view.py            # Dashboard
│   │   ├── profile_analysis_view.py # Resume analysis
│   │   ├── opportunities_view.py    # Job search
│   │   ├── settings_view.py        # Settings
│   │   └── placeholder_view.py     # Coming soon views
│   └── styles/
│       ├── theme.py                # Color schemes
│       └── constants.py            # UI constants
│
└── data/                           # File storage
    ├── resumes/
    ├── job_descriptions/
    ├── documents/
    ├── recordings/
    └── logs/
```

## 🔧 Configuration

### LLM Providers Setup

**OpenAI:**
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-...`
3. Configure in Settings UI

**Anthropic (Claude):**
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
3. Configure in Settings UI

**AWS Bedrock:**
1. Configure AWS credentials
2. Enable Bedrock models in AWS Console
3. Configure in Settings UI

**Ollama (Local):**
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama3`
3. Start Ollama: `ollama serve`
4. Configure in Settings UI

### JSearch API Setup

1. Sign up at RapidAPI: https://rapidapi.com/
2. Subscribe to JSearch API: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
3. Add API key to `.env`: `JSEARCH_API_KEY=your_key`

## 🎮 Usage

### 1. Profile Analysis
1. Go to **Profile Analysis**
2. Upload your resume
3. Paste or upload job description
4. Click **Analyze Compatibility**
5. View compatibility score, matched/missing skills, and suggestions

### 2. Job Search
1. Go to **Opportunities**
2. Enter search keywords (e.g., "Python Developer")
3. Optionally add location
4. Check "Remote only" if desired
5. Click **Search Jobs**
6. View jobs ranked by compatibility
7. Save interesting jobs or apply directly

### 3. LLM Configuration
1. Go to **Settings**
2. Select LLM Provider
3. Choose model
4. Enter API key (if required)
5. Adjust temperature and max tokens
6. Click **Test Connection**
7. Save settings

## 🛠️ Development

### Database Management

**Reset database:**
```bash
# Drop and recreate
python database/create_db.py
```

**Verify database:**
```python
from database import DatabaseManager
DatabaseManager.test_connection()
```

### Adding New Features

1. Create service in `services/`
2. Create UI view in `ui/views/`
3. Add route in `main.py`
4. Add navigation item in `ui/components/navigation.py`

## 📊 Database Schema

The application uses MySQL with the following main tables:
- `users` & `user_profiles` - User information
- `resumes` - Uploaded resumes
- `job_descriptions` - Job descriptions
- `compatibility_analyses` - Analysis results
- `question_sets` & `questions` - Interview questions
- `practice_sessions` - Practice history
- `applications` & `reminders` - Application tracking
- `jsearch_jobs` - Cached job listings
- `llm_settings` - User LLM configuration

## ⚠️ Troubleshooting

**Database connection failed:**
- Verify MySQL is running
- Check credentials in `.env`
- Run `python database/create_db.py`

**LLM connection failed:**
- Verify API key is correct
- Check network connection
- For Ollama: ensure `ollama serve` is running

**File upload not working:**
- Check file permissions on `data/` directory
- Verify file size is reasonable (<10MB)

**JSearch API errors:**
- Verify API key is valid
- Check RapidAPI subscription status
- Review rate limits

## 📝 License

MIT License

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs!

## 📧 Support

For issues or questions, please check the troubleshooting section above or review the code comments.

---

**Built with ❤️ using Flet, MySQL, and AI**

