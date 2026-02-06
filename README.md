# NextConvert (Universal File Converter)
NextConvert is a modern multi-format file conversion web app designed to make file processing fast, simple, and reliable. Users can upload a file, choose a target format, convert it, and download the output. Future updates may add AI-powered automation to make file handling even smarter.

## Features
- Drag & drop file upload
- Convert files to multiple formats ( DOCX to PDF, PDF to JPEG, PNG to PDF etc.)
- Conversion job status tracking (queued/running/done/failed)
- Download converted output
- Support / Contact Developer section
- Upcoming Features roadmap section (UI)

## 🧰 Tech Stack

**Frontend**
- Vue 3 + Vite
- TypeScript
- Vuetify (UI)
- Pinia (state management)
- Axios (API calls)

**Backend**
- FastAPI (Python)
- Uvicorn
- File conversion utilities (e.g., `pdf2docx` depending on formats)

## 🚀 Getting Started (Local)
> **Inside frontend folder**
```text
npm install
npm run dev
```

> **Inside backend folder**
```text
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

source .venv/bin/activate
uvicorn app.main:app --reload --port 8000   
```

> **.env setup**
```text
VITE_API_BASE_URL=http://localhost:8000
```

## 📬 Contact

**Pearl Viralkumar Patel**  
🎓 M.S. in Computer Engineering, University of South Florida  
💼 Aspiring Software Engineer | Data & AI Enthusiast  

📧 Email: pearl31patelus@gmail.com  
🔗 LinkedIn: https://www.linkedin.com/in/pearl-patel-6464bb1ab

Feel free to reach out for collaboration, feedback, or opportunities related to this project.


