# VeriGPT

מערכת AI חכמה לניתוח קוד RTL ב-SystemVerilog עם תמיכה ב-RAG (Retrieval-Augmented Generation).

## 🚀 תכונות עיקריות

- **ניתוח קוד RTL**: זיהוי אוטומטי של מודולים, פורטים וסיגנלים
- **יצירת Assertions**: יצירה חכמה של בדיקות אימות
- **זיהוי Edge Cases**: מציאת תרחישי קצה קריטיים
- **תמיכה ב-RAG**: שימוש ב-LangChain ו-FAISS לניתוח מדויק
- **Docker Support**: פריסה קלה בסביבת production

## 📁 מבנה הפרויקט

```
verigpt/
├── fifo.sv                    # קובץ RTL ראשוני (דוגמת FIFO)
├── verigpt_agent.py          # Agent ראשי מבוסס RAG
├── prompt_bank.py            # ניהול פרומפטים
├── prompts/                  # תבניות פרומפט
│   └── analyze_sv.txt        # פרומפט לניתוח SystemVerilog
├── requirements.txt          # תלותות Python
├── Dockerfile                # קובץ Docker
├── docker-compose.yml        # הגדרות Docker Compose
├── Makefile                  # פקודות Docker נפוצות
└── README.md                 # תיעוד זה
```

## 🐳 הרצה עם Docker

### דרישות מקדימות
- Docker ו-Docker Compose מותקנים
- OpenAI API Key

### הוראות הרצה מהירה

1. **הכנת משתני סביבה:**
   ```bash
   # יצירת קובץ .env (אוטומטי)
   make setup-env
   
   # ערוך את .env והוסף את ה-API Key שלך
   # OPENAI_API_KEY=your-actual-api-key-here
   
   # בדיקה שהכל מוגדר נכון
   make check-env
   
   # בדיקת משתני הסביבה (אופציונלי)
   make test-env
   ```

2. **בנייה והרצה:**
   ```bash
   # בנייה
   make build
   
   # הרצה עם docker-compose (משתמש ב-.env אוטומטית)
   make up
   
   # או הרצה ישירה
   make run
   ```

3. **פקודות נוספות:**
   ```bash
   make logs      # צפייה בלוגים
   make stop      # עצירת הקונטיינר
   make down      # עצירה עם docker-compose
   make clean     # ניקוי
   make shell     # shell אינטראקטיבי
   ```

### הרצה ידנית

```bash
# בנייה
docker build -t verigpt .

# הרצה (חובה עם .env)
docker run -d --name verigpt --env-file .env verigpt

# צפייה בלוגים
docker logs -f verigpt
```

**⚠️  חשוב**: לעולם אל תגדיר משתני סביבה ישירות ב-Dockerfile או תעלה את קובץ .env ל-repository!

## 🔧 התקנה מקומית (ללא Docker)

```bash
# התקנת תלותות
pip install -r requirements.txt

# הגדרת משתני סביבה
export OPENAI_API_KEY="your-key-here"

# הרצה של Agent
python verigpt_agent.py

# הרצה של שירות FastAPI
python main.py
```

## 🚀 הרצה מהירה (Quick Start)

```bash
# 1. Clone הפרויקט
git clone <your-repo-url>
cd verigpt

# 2. הגדר משתני סביבה (בטוח)
make setup-env
# ערוך את .env והוסף את ה-API Key שלך
make check-env

# 3. הרץ עם Docker
make build
make up

# 4. בדוק שהשירות עובד
make test-api
make api-docs

# 5. צפה בלוגים
make logs

## 🚀 הרצה מהירה של שירות FastAPI

```bash
# 1. התקן תלותות
pip install -r requirements.txt

# 2. הגדר משתני סביבה (בטוח)
# ב-PowerShell:
copy env.example .env
# ערוך את .env והוסף את ה-API Key שלך

# 3. הרץ את השירות
python -m app.main

# 4. פתח בדפדפן
# Swagger UI: http://localhost:8000/docs
# Health: http://localhost:8000/health

# 5. בדוק עם Python
python app/test_api.py
```

## 🚨 פתרון בעיות נפוצות:

### **בעיה: "OPENAI_API_KEY not set"**
```bash
# פתרון: צור קובץ .env
make setup-env
# ערוך את .env והוסף את ה-API Key שלך
make check-env
```

### **בעיה: "Could not initialize VeriGPT agent"**
```bash
# פתרון: בדוק שהמשתנים נטענים נכון
# ב-PowerShell:
python -m app.verigpt_agent --test-env

# ב-Linux/Mac:
make test-env
make security-check
```

### **בעיה: שירות לא עונה על localhost:8000**
```bash
# פתרון: בדוק שהשירות רץ
make test-api
make logs
```

## 🔒 אבטחה ומשתני סביבה

- **קובץ .env**: מכיל את ה-API Keys שלך - לעולם אל תעלה אותו ל-repository!
- **Dockerfile**: לא מכיל משתני סביבה רגישים
- **docker-compose.yml**: קורא את .env אוטומטית ומעביר אותו לקונטיינר
- **Makefile**: כולל פקודות לבדיקה והגדרה בטוחה
- **python-dotenv**: המערכת קוראת את .env אוטומטית עם `load_dotenv()`

### 🔒 בדיקות אבטחה:
```bash
# בדיקה שהכל מוגדר נכון
make security-check

# בדיקת משתני הסביבה
make check-env

# הגדרה בטוחה של .env
make setup-env
```

### איך זה עובד:
1. **במקומי**: `load_dotenv()` קורא את .env מהתיקייה הנוכחית
2. **ב-Docker**: docker-compose מעביר את משתני הסביבה אוטומטית
3. **משתני סביבה**: נטענים אוטומטית ונגישים דרך `os.getenv()`
4. **אבטחה**: הקוד בודק שהמשתנים נטענים נכון ומדווח על בעיות

## 🌐 שירות FastAPI

המערכת כוללת שירות FastAPI מלא עם endpoints הבאים:

### **Endpoints זמינים:**
- **`GET /`** - מידע על השירות ובריאות המערכת
- **`GET /health`** - בדיקת בריאות המערכת
- **`POST /analyze/code`** - ניתוח קוד SystemVerilog ישיר
- **`POST /analyze/files`** - ניתוח קבצים ספציפיים
- **`GET /files`** - רשימת כל קבצי SystemVerilog הזמינים
- **`GET /stats`** - סטטיסטיקות על בסיס הקוד
- **`GET /faiss/status`** - מצב ה-FAISS index
- **`POST /agent`** - שאילתות RAG עם ה-FAISS index

### **איך לבדוק:**
```bash
# בדיקת בריאות
curl http://localhost:8000/health

# רשימת קבצים
curl http://localhost:8000/files

# ניתוח קוד
curl -X POST http://localhost:8000/analyze/code \
  -H "Content-Type: application/json" \
  -d '{"code": "module test(); endmodule"}'

# בדיקת מצב FAISS
curl http://localhost:8000/faiss/status

# שאילתת agent
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "How does the FIFO work?", "top_k": 3}'

# או בדיקה עם Python
python app/test_api.py
```

### **ממשק משתמש:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 תלותות

- Python 3.10+
- langchain
- openai
- faiss-cpu
- python-dotenv

## 🚀 שלבים הבאים

- [x] שמירת FAISS לתמיכה ב-Deploy
- [ ] הוספת agent_runner.py לשליטה במצב multi-tool
- [ ] מערכת feedback פשוטה
- [ ] CLI ממשק או Streamlit UI
- [ ] פריסה על Render/Cloud

## 🔍 יצירת FAISS Index

כדי להשתמש ב-agent endpoint, צריך ליצור FAISS index תחילה:

```bash
# הרץ את הסוכן כדי ליצור את ה-index
python -m app.verigpt_agent

# או עם Docker
make build
make up
```

אחרי זה תוכל להשתמש ב-`/agent` endpoint לשאילתות RAG.

## 📞 תמיכה

לשאלות ותמיכה, פנה אל הצוות או פתח issue בפרויקט.
