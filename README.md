# Data Intelligence Suite - Complete Hackathon Project

## 📦 Project Structure

```
test/
├── data-intelligence-suite.html      ← Frontend (READY)
├── main.py                            ← FastAPI backend
├── requirements.txt                   ← Python dependencies
├── Dockerfile                         ← Docker image
├── docker-compose.yml                 ← Full stack deployment
├── setup.bat                          ← Windows setup script
├── setup.sh                           ← Mac/Linux setup script
└── SETUP.md                           ← Detailed setup guide
```

---

## 🚀 Quick Start (Windows)

### Step 1: Run Setup Script
```bash
cd C:\Users\Siddharth Gupta\Desktop\test
setup.bat
```

This will:
- ✅ Create Python virtual environment
- ✅ Activate venv
- ✅ Install all dependencies (FastAPI, SQLAlchemy, MiniLM v6, etc.)

### Step 2: Verify Installation
```bash
python --version  # Should be 3.11+
pip list          # Should show fastapi, sqlalchemy, sentence-transformers
```

### Step 3: Start Backend
```bash
python main.py
```

Server will start on `http://localhost:8000`

### Step 4: Open Frontend
```bash
# In another terminal:
start data-intelligence-suite.html
```

---

## 🐳 Docker Deployment (Production)

### One Command:
```bash
docker-compose up --build
```

This starts:
- **Backend:** `http://localhost:8000` (FastAPI)
- **Frontend:** `http://localhost:3000` (Nginx)
- **PostgreSQL:** `localhost:5432`
- **MySQL:** `localhost:3306`

---

## 🔧 What You Have

### Frontend (`data-intelligence-suite.html`)
- ✅ Excel-like professional UI
- ✅ MiniLM v6 semantic matching
- ✅ Dark mode support
- ✅ CSV/JSON upload support
- ✅ No external dependencies

### Backend (`main.py`)
- ✅ FastAPI with CORS enabled
- ✅ PostgreSQL & MySQL support
- ✅ MiniLM v6 semantic similarity
- ✅ SQL generation pipeline
- ✅ Schema introspection
- ✅ Query execution with limits
- ✅ Fallback pattern matching

### Deployment
- ✅ Docker + Docker Compose
- ✅ PostgreSQL + MySQL
- ✅ Nginx frontend serving
- ✅ Health checks
- ✅ Auto-restart on failure

---

## 📊 API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Connect Database
```bash
curl -X POST http://localhost:8000/api/connect \
  -H "Content-Type: application/json" \
  -d '{
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "username": "postgres",
    "password": "postgres",
    "database": "data_intelligence"
  }'
```

### Natural Language Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me top 10 employees by salary",
    "limit": 100
  }'
```

Response:
```json
{
  "generated_sql": "SELECT * FROM employees ORDER BY salary DESC LIMIT 10",
  "results": [...],
  "rows_affected": 10,
  "execution_time": 0.25,
  "confidence": 0.95
}
```

### Get Schema
```bash
curl http://localhost:8000/api/schema
```

---

## 🧠 MiniLM v6 Integration

**Automatic semantic matching** in SQL generation:

```python
# First run: downloads model (~450MB)
python main.py

# Model cached locally after first run
# Used for:
# - Table name matching
# - Column name inference
# - Query intent detection
# - Confidence scoring
```

**Fallback to token-based matching** if MiniLM not installed.

---

## 🎯 For Hackathon Presentation

**What to show judges:**

1. **Frontend Demo**
   - Upload CSV file
   - Ask natural language questions
   - See SQL generated
   - View results with visualizations

2. **Backend Capabilities**
   - Real database connection
   - Semantic NL understanding
   - SQL generation pipeline
   - Production-ready code

3. **Complete Stack**
   - Docker deployment
   - Scalable architecture
   - Both PostgreSQL & MySQL support

---

## 📝 Troubleshooting

**ImportError: No module named 'fastapi'**
```bash
pip install -r requirements.txt
```

**Connection refused (database)**
- With Docker: `docker-compose up` starts databases
- Local: Install PostgreSQL/MySQL manually

**MiniLM model slow**
- Normal on first run (downloads ~450MB)
- Cached after first execution
- Use local token matching as fallback

**CORS errors**
- CORS already enabled in backend
- Check frontend/backend URLs match

---

## 📁 Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `data-intelligence-suite.html` | Frontend UI | ✅ Ready |
| `main.py` | FastAPI backend | ✅ Ready |
| `requirements.txt` | Python dependencies | ✅ Ready |
| `Dockerfile` | Container image | ✅ Ready |
| `docker-compose.yml` | Full stack orchestration | ✅ Ready |
| `setup.bat` | Windows setup | ✅ Ready |
| `setup.sh` | Mac/Linux setup | ✅ Ready |
| `SETUP.md` | Detailed guide | ✅ Ready |

---

## ✨ Key Features

✅ **Professional UI** - Excel-like Fluent Design  
✅ **MiniLM v6** - Semantic NL understanding  
✅ **SQL Generation** - Template-based with ML enhancement  
✅ **PostgreSQL & MySQL** - Multi-database support  
✅ **Docker Ready** - One-command deployment  
✅ **CORS Enabled** - Production CORS setup  
✅ **Health Checks** - Monitoring built-in  
✅ **Type Safe** - Pydantic models  
✅ **Scalable** - Connection pooling ready  

---

## 🎬 Next Steps

1. **Run setup.bat** to install dependencies
2. **Start backend**: `python main.py`
3. **Open frontend**: `data-intelligence-suite.html`
4. **Test queries**: "Top 10 by salary", "Count by department"
5. **For production**: Use `docker-compose up`

---

**You're ready for the hackathon! 🚀**
