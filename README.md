# 🎓 Навчальний Агент / Learning Agent

Простий веб-додаток на **Streamlit**, який допомагає створювати конспекти та перевіряти знання на основі навчальних матеріалів з **YouTube** або завантажених файлів.

*A simple Streamlit web application that helps create summaries and check knowledge based on learning materials from YouTube or uploaded files.*

---

## 🇺🇦 Опис українською

Цей інструмент дозволяє користувачам швидко отримати структурований конспект з відеолекції на YouTube або з текстових документів (.txt, .pdf, .pptx).  
Після створення конспекту додаток може згенерувати тестові питання для самоперевірки.

### 🔑 Основні функції

- **Конспектування з YouTube**  
  Вставте посилання на відео, і додаток:
  - Завантажить аудіо (`yt-dlp`)
  - Зробить транскрипцію (`whisper`)
  - Створить конспект через **Google Gemini API**

- **Конспектування з файлів**  
  Завантажте файл у форматі `.txt`, `.pdf`, або `.pptx`.  
  Додаток витягне текст і сформує конспект.

- **Перевірка знань**  
  На основі конспекту можна згенерувати тест з варіантами відповідей.

---

## 🇬🇧 Description in English

This tool allows users to quickly get a structured summary from a **YouTube video lecture** or text documents (`.txt`, `.pdf`, `.pptx`).  
After generating the summary, the app can create **multiple-choice questions** for self-assessment.

### 🔑 Key Features

- **Summarization from YouTube**  
  Paste a video link – the app will:
  - Download audio (`yt-dlp`)
  - Transcribe it (`whisper`)
  - Summarize using **Google Gemini API**

- **Summarization from Files**  
  Upload `.txt`, `.pdf`, or `.pptx` files and get a summary.

- **Knowledge Check**  
  Automatically generate quiz questions to check understanding.

---

## ⚙️ Technology Stack

- **Python**
- **Streamlit** – UI
- **Google Gemini API** – Summarization & quiz generation
- **whisper** – Audio transcription
- **yt-dlp** – YouTube audio download
- **PyPDF2**, **python-pptx** – File parsing

---

## 🚀 Запуск локально / Run Locally

1. **Клонуйте репозиторій / Clone the repository**
   ```bash
   git clone <URL вашого репозиторію>
   cd <назва папки>
   ```

2. **Створіть та активуйте віртуальне середовище / Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # або / or
   .venv\Scripts\activate     # Windows
   ```

3. **Встановіть залежності / Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Встановіть `ffmpeg`**
   - Необхідно для `-whisper` та `yt-dlp`.
   - Інструкції: [ffmpeg.org](https://ffmpeg.org/download.html)

5. **Налаштуйте API ключ / Set up API Key**
   - Створіть `config.py` (і додайте в `.gitignore`) або
   - Використовуйте змінні середовища
   - Для Streamlit Cloud використовуйте `st.secrets`

6. **Запуск додатку / Run the app**
   ```bash
   streamlit run main.py
   ```



---

## 📄 Ліцензія / License

MIT License
