# Document Q&A AI Agent - Web Application

An enterprise-ready AI-powered web application for intelligent document question-answering with multi-modal PDF processing, built with Flask and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Capabilities
- **🌐 Web-Based Interface** - Clean, modern UI accessible from any browser
- **📤 Drag & Drop PDF Upload** - Easy document upload with visual feedback
- **🤖 AI-Powered Q&A** - Natural language queries with intelligent responses
- **⚡ Real-time Processing** - Instant document processing and query responses
- **📊 Multi-Modal Extraction** - Text, tables, equations, and structure preservation
- **🔍 ArXiv Integration** - Search and reference research papers (bonus feature)

### Query Types Supported
1. **Direct Content Lookup** - "What is the conclusion of this paper?"
2. **Summarization** - "Summarize the methodology section"
3. **Metric Extraction** - "What are the accuracy and F1-scores reported?"
4. **ArXiv Search** - "Find recent papers about transformers"

### Supported LLM Providers
- ✅ **Groq** (Recommended - FREE & Fast)
- ✅ **OpenAI** (GPT-4, GPT-3.5)
- ✅ **Google Gemini**

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8 or higher
- Free API key from [Groq](https://console.groq.com) (Recommended)
- OR OpenAI / Google Gemini API key

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd document-qa-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get FREE API Key (Recommended: Groq)

1. **Visit Groq Console**: https://console.groq.com
2. **Sign up** (completely free, no credit card!)
3. **Create API Key** from dashboard
4. **Copy the key** (starts with `gsk_...`)

### Step 3: Configure Environment

Create a `.env` file in the project root:

```env
# Recommended: Groq (FREE & Fast)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Alternative: OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk_your_key_here
# OPENAI_MODEL=gpt-3.5-turbo

# Alternative: Google Gemini
# LLM_PROVIDER=gemini
# GOOGLE_API_KEY=your_key_here
# GEMINI_MODEL=gemini-1.5-flash
```

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Open Your Browser

Navigate to: **http://localhost:8080**

You should see the Document Q&A interface! 🎉

---

## 📖 How to Use

### 1. Upload a PDF Document

- Click the **"Choose PDF File"** button or drag & drop a PDF
- Supported formats: PDF files only
- The document will be automatically processed
- You'll see a success message when ready

### 2. Ask Questions

Type your question in the chat input and press Enter or click **"Send"**

**Example Questions:**

```
What is this paper about?
Summarize the methodology section
What accuracy scores are reported?
List the key findings
What datasets were used?
Find papers about neural networks on ArXiv
```

### 3. View AI Responses

- Responses appear in real-time
- Scroll through the chat history
- Upload new PDFs to query different documents

---

## 🏗️ Project Structure

```
document-qa-agent/
├── app.py                      # Flask web application
├── static/                     # Frontend assets
│   ├── css/
│   │   └── style.css          # Application styles
│   └── js/
│       └── chat.js            # Chat interface logic
├── templates/
│   └── index.html             # Main web interface
├── src/                       # Backend modules
│   ├── document_processor.py  # PDF processing (450+ lines)
│   ├── llm_interface.py       # LLM abstraction (550+ lines)
│   ├── query_engine.py        # Query orchestration (300+ lines)
│   ├── arxiv_integration.py   # ArXiv API (200+ lines)
│   └── utils.py              # Utilities (280+ lines)
├── data/
│   ├── pdfs/                 # Uploaded PDF files
│   └── processed/            # Processed document cache
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (create this)
└── README.md                # This file
```

---

## 🎨 Web Interface Features

### Modern Chat UI
- **Clean Design** - Minimalist, professional interface
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Instant message display
- **Upload Feedback** - Visual confirmation of uploads
- **Error Handling** - Clear error messages

### User Experience
- **Auto-scroll** - Automatically scrolls to latest message
- **Loading Indicators** - Shows when processing
- **File Validation** - Checks PDF format before upload
- **Session Persistence** - Maintains chat history during session

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider to use | `groq`, `openai`, `gemini` |
| `GROQ_API_KEY` | Groq API key (FREE) | `gsk_...` |
| `GROQ_MODEL` | Groq model name | `llama-3.1-70b-versatile` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | OpenAI model | `gpt-3.5-turbo` |
| `GOOGLE_API_KEY` | Google API key | `AIza...` |
| `GEMINI_MODEL` | Gemini model | `gemini-1.5-flash` |
| `MAX_TOKENS` | Max response length | `2000` |
| `TEMPERATURE` | Creativity (0-1) | `0.7` |

### Application Settings

Edit `app.py` to customize:

```python
# Port number
app.run(port=8080)

# Upload folder
UPLOAD_FOLDER = "data/pdfs"

# LLM Provider (can override .env)
engine = QueryEngine(llm_provider="groq")
```

---

## 🔧 API Endpoints

### GET `/`
- **Description**: Serve the main web interface
- **Returns**: HTML page

### POST `/upload_pdf`
- **Description**: Upload and process a PDF document
- **Content-Type**: `multipart/form-data`
- **Parameters**: 
  - `pdf`: PDF file (form data)
- **Returns**: JSON
  ```json
  {
    "message": "PDF uploaded and processed successfully",
    "filename": "paper.pdf"
  }
  ```

### POST `/ask`
- **Description**: Ask a question about the uploaded document
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "question": "What is the main contribution?"
  }
  ```
- **Returns**: JSON
  ```json
  {
    "answer": "The main contribution is..."
  }
  ```

---

## 🎯 Advanced Usage

### Programmatic API Usage

You can also use the backend directly without the web interface:

```python
from src.query_engine import QueryEngine

# Initialize engine
engine = QueryEngine(llm_provider="groq")

# Process documents
engine.process_documents("data/pdfs")

# Query
answer = engine.query("What is this paper about?")
print(answer)

# Get document summary
summary = engine.get_document_summary("paper_name")
print(summary)
```

### Custom Frontend Integration

The API endpoints can be integrated with any frontend:

```javascript
// Upload PDF
const formData = new FormData();
formData.append('pdf', pdfFile);

fetch('/upload_pdf', {
    method: 'POST',
    body: formData
}).then(res => res.json());

// Ask question
fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: 'Your question here'})
}).then(res => res.json());
```

---

## 🆓 Free LLM Options

### Option 1: Groq (Recommended ⭐)

**Why Choose Groq:**
- ✅ Completely FREE
- ✅ No credit card required
- ✅ SUPER FAST (fastest inference)
- ✅ 30 requests/minute
- ✅ Excellent quality (Llama 3.1)

**Setup:**
1. Go to https://console.groq.com
2. Sign up (free)
3. Create API key
4. Use in `.env`: `GROQ_API_KEY=gsk_...`

**Available Models:**
- `llama-3.1-70b-versatile` - Best overall (recommended)
- `llama-3.1-8b-instant` - Faster, smaller
- `mixtral-8x7b-32768` - Good alternative

### Option 2: OpenAI

- Free: $5 credits (3 months)
- After: ~$0.002-0.03 per query
- Get key: https://platform.openai.com/api-keys

### Option 3: Google Gemini

- Free tier available
- Get key: https://makersuite.google.com/app/apikey

---

## 📝 Example Queries & Responses

### Query 1: Content Lookup
```
Q: What is the main contribution of this paper?

A: The main contribution is a novel beta-elliptical approach 
   for Parkinson's disease detection using online handwriting 
   analysis, combined with a fuzzy perceptual detector that 
   achieves 94.2% accuracy...
```

### Query 2: Methodology Summary
```
Q: Summarize the methodology section

A: The methodology involves three key steps: (1) Data collection 
   from 75 patients using a digital tablet, (2) Feature extraction 
   using beta-elliptical modeling of handwriting dynamics, and 
   (3) Classification using a fuzzy perceptual detector with 
   optimized parameters...
```

### Query 3: Metric Extraction
```
Q: What accuracy scores are reported?

A: **Extracted Metrics:**
   - Overall Accuracy: 94.2%
   - Sensitivity: 92.8%
   - Specificity: 95.6%
   - F1-Score: 0.943
```

### Query 4: ArXiv Search
```
Q: Find recent papers about Parkinson's detection

A: Found 5 papers:
   1. "Deep Learning for Parkinson's Disease Diagnosis..."
   2. "Novel Biomarkers in PD Detection Using AI..."
   [Additional papers with summaries]
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'flask'"
**Solution:**
```bash
pip install flask
```

### Issue: "Address already in use"
**Solution:** Change port in `app.py`:
```python
app.run(port=8081)  # Use different port
```

### Issue: "PDF processing failed"
**Solution:**
- Ensure PDF is not corrupted
- Check if PDF is password-protected
- Try a different PDF file

### Issue: "API key not found"
**Solution:**
```bash
# Check .env file exists
cat .env

# Verify API key is set
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
```

### Issue: "No documents processed"
**Solution:**
1. Upload a PDF using the web interface
2. Wait for "PDF uploaded and processed successfully" message
3. Then ask your question

---

## 🔒 Security Best Practices

### Production Deployment

1. **Disable Debug Mode**
```python
app.run(debug=False)
```

2. **Add Authentication**
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.route("/")
@auth.login_required
def index():
    return render_template("index.html")
```

3. **File Upload Security**
- Limit file size: `app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB`
- Validate file types
- Scan for malware (in production)

4. **Use HTTPS**
```bash
# Use gunicorn with SSL
gunicorn --certfile=cert.pem --keyfile=key.pem app:app
```

5. **Environment Variables**
- Never commit `.env` to version control
- Use secrets management in production
- Rotate API keys regularly

---

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:8080
```

### Production (Gunicorn)
```bash
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8080 app:app

# With workers
gunicorn --workers 4 --bind 0.0.0.0:8080 app:app
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

```bash
# Build and run
docker build -t document-qa .
docker run -p 8080:8080 --env-file .env document-qa
```

### Cloud Platforms

#### Heroku
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### AWS (Elastic Beanstalk)
```bash
eb init -p python-3.9 document-qa
eb create document-qa-env
eb deploy
```

#### Google Cloud Run
```bash
gcloud run deploy document-qa \
  --source . \
  --platform managed \
  --region us-central1
```

---

## 📊 Performance

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Processing | 2-5s | Per document |
| Query Response (Groq) | 1-3s | Fastest |
| Query Response (OpenAI) | 2-5s | Good |
| Query Response (Gemini) | 3-7s | Slower |
| ArXiv Search | 1-3s | Network dependent |

### Optimization Tips

1. **Enable Caching**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def query_with_cache(question):
    return engine.query(question)
```

2. **Process Documents Once**
- Documents stay processed until server restart
- Use persistent storage for production

3. **Use Faster Models**
- Groq: Fastest inference
- GPT-3.5: Cheaper than GPT-4
- Adjust `MAX_TOKENS` for faster responses

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black src/
flake8 src/
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **LLM Providers**: OpenAI, Google, Groq
- **PDF Processing**: PyMuPDF, pdfplumber
- **ArXiv**: Open access research papers
- **Flask**: Web framework

---

## 📞 Support

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: Open a GitHub issue
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)

---

## 🎓 Use Cases

### Academic Research
- Quickly extract information from research papers
- Compare methodologies across papers
- Find related work on ArXiv

### Business Documents
- Extract key metrics from reports
- Summarize long documents
- Find specific information quickly

### Technical Documentation
- Query API documentation
- Extract code examples
- Find specific configurations

---

## 🔄 Changelog

### v2.0.0 - Web Application Release
- ✨ Added Flask web interface
- ✨ Drag & drop PDF upload
- ✨ Real-time chat interface
- ✨ Groq LLM support (FREE)
- 🐛 Fixed PDF processing issues
- 📝 Updated documentation

### v1.0.0 - Initial Release
- ✅ CLI interface
- ✅ Multi-modal PDF processing
- ✅ OpenAI & Gemini support
- ✅ ArXiv integration

---

**Built with ❤️ for enterprise AI applications**

**Get Started Now:** http://localhost:8080 🚀