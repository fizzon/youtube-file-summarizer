🎓 Навчальний Агент / Learning Agent
Простий веб-додаток на Streamlit, який допомагає створювати конспекти та перевіряти знання на основі навчальних матеріалів з YouTube або завантажених файлів.

A simple Streamlit web application that helps create summaries and check knowledge based on learning materials from YouTube or uploaded files.

🇺🇦 Опис українською
Цей інструмент дозволяє користувачам швидко отримати структурований конспект з відеолекції на YouTube або з текстових документів (.txt, .pdf, .pptx). Після створення конспекту, додаток може згенерувати питання з варіантами відповідей для самоперевірки засвоєного матеріалу.

Основні функції:
Конспектування з YouTube: Вставте посилання на відео YouTube, і додаток завантажить аудіо, транскрибує його та створить конспект за допомогою Google Gemini API.

Конспектування з файлів: Завантажте файли у форматах .txt, .pdf або .pptx. Додаток вилучить текст і згенерує конспект.

Перевірка знань: Після генерації конспекту можна створити тест з питаннями та варіантами відповідей для оцінки розуміння ключових моментів.

Технології:
Python

Streamlit (для веб-інтерфейсу)

Google Gemini API (для створення конспектів та питань)

faster-whisper (для транскрипції аудіо)

yt-dlp (для завантаження з YouTube)

PyPDF2, python-pptx (для обробки файлів)

Запуск локально (для розробки):
Клонуйте репозиторій: git clone <URL вашого репозиторію>

Перейдіть у папку проекту: cd <назва папки>

Створіть та активуйте віртуальне середовище (рекомендовано):

python -m venv .venv
source .venv/bin/activate # Linux/macOS
# або
.\.venv\Scripts\activate # Windows

Встановіть залежності: pip install -r requirements.txt

Встановіть ffmpeg: Це системна залежність, потрібна для faster-whisper та yt-dlp. Інструкції зі встановлення залежать від вашої ОС (ffmpeg.org).

Налаштуйте API ключ: Для локального запуску вам потрібно надати GOOGLE_API_KEY. Можна створити файл config.py (і додати його в .gitignore!) або використовувати змінні середовища. При розгортанні на Streamlit Cloud використовуйте st.secrets.

Запустіть додаток: streamlit run main.py

🇬🇧 Description in English
This tool allows users to quickly get a structured summary from a YouTube video lecture or text documents (.txt, .pdf, .pptx). After creating the summary, the application can generate multiple-choice questions for self-assessment of the learned material.

Key Features:
Summarization from YouTube: Paste a YouTube video link, and the app will download the audio, transcribe it, and create a summary using the Google Gemini API.

Summarization from Files: Upload files in .txt, .pdf, or .pptx formats. The app will extract the text and generate a summary.

Knowledge Check: After generating the summary, you can create a quiz with multiple-choice questions to assess understanding of key points.

Technology Stack:
Python

Streamlit (for the web interface)

Google Gemini API (for summarization and question generation)

faster-whisper (for audio transcription)

yt-dlp (for downloading from YouTube)

PyPDF2, python-pptx (for file processing)

Running Locally (for development):
Clone the repository: git clone <your repository URL>

Navigate to the project directory: cd <folder name>

Create and activate a virtual environment (recommended):

python -m venv .venv
source .venv/bin/activate # Linux/macOS
# or
.\.venv\Scripts\activate # Windows

Install dependencies: pip install -r requirements.txt

Install ffmpeg: This is a system dependency required by faster-whisper and yt-dlp. Installation instructions depend on your OS (ffmpeg.org).

Set up API Key: For local execution, you need to provide the GOOGLE_API_KEY. You can create a config.py file (and add it to .gitignore!) or use environment variables. When deploying to Streamlit Cloud, use st.secrets.

Run the application: streamlit run main.py
