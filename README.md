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
   cp env.example .env
   # ערוך את .env והוסף את ה-API Key שלך
   ```

2. **בנייה והרצה:**
   ```bash
   # בנייה
   make build
   
   # הרצה עם docker-compose
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

# הרצה
docker run -d --name verigpt --env-file .env verigpt

# צפייה בלוגים
docker logs -f verigpt
```

## 🔧 התקנה מקומית (ללא Docker)

```bash
# התקנת תלותות
pip install -r requirements.txt

# הגדרת משתני סביבה
export OPENAI_API_KEY="your-key-here"

# הרצה
python verigpt_agent.py
```

## 🚀 הרצה מהירה (Quick Start)

```bash
# 1. Clone הפרויקט
git clone <your-repo-url>
cd verigpt

# 2. הגדר משתני סביבה
cp env.example .env
# ערוך את .env והוסף את ה-API Key שלך

# 3. הרץ עם Docker
make build
make up

# 4. צפה בלוגים
make logs
```

## 📋 תלותות

- Python 3.10+
- langchain
- openai
- faiss-cpu
- python-dotenv

## 🚀 שלבים הבאים

- [ ] שמירת FAISS לתמיכה ב-Deploy
- [ ] הוספת agent_runner.py לשליטה במצב multi-tool
- [ ] מערכת feedback פשוטה
- [ ] CLI ממשק או Streamlit UI
- [ ] פריסה על Render/Cloud

## 📞 תמיכה

לשאלות ותמיכה, פנה אל הצוות או פתח issue בפרויקט.
