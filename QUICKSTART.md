# 🚀 Quick Start Guide - Interview Prep AI

Get up and running in 5 minutes!

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.9 or higher
- ✅ MySQL 8.0 or higher installed and running
- ✅ At least one API key (OpenAI, Anthropic, or Ollama installed)

## Step-by-Step Setup

### 1. Install Python Dependencies (2 minutes)

```bash
# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

Copy `.env.example` to `.env` and fill in your details:

```bash
# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

**Minimum required in `.env`:**
```env
# Database (REQUIRED)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=interview_prep_ai
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password

# At least ONE LLM provider (choose one):
OPENAI_API_KEY=sk-...                    # OpenAI
# OR
ANTHROPIC_API_KEY=sk-ant-...             # Claude
# OR
OLLAMA_BASE_URL=http://localhost:11434   # Local (Ollama)

# Optional but recommended for job search:
JSEARCH_API_KEY=your_jsearch_key
```

### 3. Setup Database (1 minute)

```bash
python database/create_db.py
```

You should see:
```
✓ Database 'interview_prep_ai' created/verified
✓ All tables created successfully
✓ Default user created
✅ Database setup completed successfully!
```

### 4. Run the Application (1 minute)

```bash
python main.py
```

The app will open in a new window!

## First Steps in the App

### Configure LLM Provider

1. Click **Settings** in the left sidebar
2. Select your LLM provider (OpenAI, Anthropic, Bedrock, or Ollama)
3. Choose a model
4. Enter your API key (if needed)
5. Click **Test Connection**
6. Click **Save Settings**

### Try Profile Analysis

1. Go to **Profile Analysis**
2. Upload your resume (PDF, DOCX, or TXT)
3. Paste a job description
4. Click **Analyze Compatibility**
5. View your compatibility score and recommendations!

### Search for Jobs

1. Go to **Opportunities**
2. Enter job keywords (e.g., "Python Developer")
3. Optionally add location
4. Click **Search Jobs**
5. View jobs ranked by compatibility!

### Get Career Coaching

1. Go to **Career Coach**
2. Try quick advice buttons or
3. Click **Start New Coaching Session**
4. Chat with your AI career coach!

## Common Issues

### "Database connection failed"
- **Solution**: Make sure MySQL is running
- Check your credentials in `.env`
- Run `python database/create_db.py` again

### "LLM connection failed"
- **Solution**: Verify your API key is correct
- For Ollama: Make sure `ollama serve` is running
- Try **Test Connection** in Settings

### "File upload not working"
- **Solution**: Check file is PDF, DOCX, or TXT
- Make sure file size is reasonable (<10MB)
- Check `data/` directory has write permissions

## Getting API Keys

### OpenAI (Recommended for best quality)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy and paste into `.env`

**Cost**: ~$0.01-0.05 per analysis (GPT-4)

### Anthropic Claude
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Get API key from settings
4. Copy and paste into `.env`

**Cost**: Similar to OpenAI

### Ollama (Free, Local)
1. Install from https://ollama.ai/
2. Run: `ollama pull llama3`
3. Start server: `ollama serve`
4. Use URL: `http://localhost:11434`

**Cost**: Free! Runs on your computer

### JSearch API (Optional - for job search)
1. Sign up at https://rapidapi.com/
2. Subscribe to JSearch API
3. Copy API key to `.env`

**Cost**: Free tier available (100 searches/month)

## What's Working

✅ **Profile Analysis** - Full implementation with LLM
✅ **Job Opportunities** - JSearch integration with compatibility ranking
✅ **Settings** - Complete LLM provider configuration
✅ **Career Coach** - AI-powered career guidance with chat
✅ **Database** - Full MySQL schema with auto-setup
✅ **File Upload** - Resume and JD upload/parsing

## What's Coming Soon

🚧 Questions Generator (placeholder ready)
🚧 Practice Sessions (placeholder ready)
🚧 Document Writer (placeholder ready)
🚧 Application Planner (placeholder ready)

## Need Help?

1. Check the main README.md for detailed documentation
2. Review error messages in the terminal
3. Verify all prerequisites are installed
4. Make sure .env is configured correctly

## Next Steps

After getting started:
1. Upload your resume
2. Try analyzing compatibility with real job postings
3. Search for jobs using JSearch
4. Chat with the career coach for personalized advice
5. Configure your preferred LLM provider in Settings

---

**You're all set! Enjoy using Interview Prep AI! 🎯**

