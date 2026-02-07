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
- **🔍 ArXiv Integration** - Search and reference research papers

### Query Types Supported
1. **Direct Content Lookup** - "What is the conclusion of this paper?"
2. **Summarization** - "Summarize the methodology section"
3. **Metric Extraction** - "What are the accuracy and F1-scores reported?"
4. **ArXiv Search** - "Find recent papers about transformers"

### Supported LLM Providers
- ✅ **OpenAI** (GPT-4, GPT-3.5)
- ✅ **Google Gemini**

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8 or higher
- API key from OpenAI / Google Gemini

### Step 1: Clone & Setup

```bash
# Clone the repository
git clone https://github.com/akshat-2600/document-qa-agent.git
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

### Step 2: Get FREE API Key

1. **Visit Google AI Studio**: https://aistudio.google.com/
2. **Sign up** (completely free, no credit card!)
3. **Create API Key** from dashboard
4. **Copy the key**

### Step 3: Configure Environment

Create a `.env` file in the project root:

```env
# Recommended: Google Gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash

# Alternative: OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk_your_key_here
# OPENAI_MODEL=gpt-3.5-turbo
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
│   ├── __init__.py
│   ├── document_processor.py  # PDF processing 
│   ├── llm_interface.py       # LLM abstraction 
│   ├── query_engine.py        # Query orchestration 
│   ├── arxiv_integration.py   # ArXiv API 
│   └── utils.py              # Utilities 
├── data/
│   ├── pdfs/                 # Uploaded PDF files
│   └── processed/            # Processed document cache
├── main.py
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
| `LLM_PROVIDER` | AI provider to use | `openai`, `gemini` |
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
engine = QueryEngine(llm_provider="gemini-2.5-flash")
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

## 🆓 Free LLM Options

### Option 1: Google Gemini (Recommended ⭐)

- Free tier available
- Get key: https://makersuite.google.com/app/apikey


### Option 2: OpenAI

- Free: $5 credits (3 months)
- After: ~$0.002-0.03 per query
- Get key: https://platform.openai.com/api-keys

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
LLM_PROVIDER=gemini
GOOGLE_API_KEY=_your_key_here
```

### Issue: "No documents processed"
**Solution:**
1. Upload a PDF using the web interface
2. Wait for "PDF uploaded and processed successfully" message
3. Then ask your question

---

## 🙏 Acknowledgments

- **LLM Providers**: OpenAI, Google
- **PDF Processing**: PyMuPDF, pdfplumber
- **ArXiv**: Open access research papers
- **Flask**: Web framework

---

**Built with ❤️ for enterprise AI applications**

**Get Started Now:** http://localhost:8080 🚀