import streamlit as st
from youtube_processing import download_audio
from transcript_processing import transcribe_audio, summarize_transcript_pipeline
from utils import extract_text_from_pdf, extract_text_from_pptx, extract_text_from_txt
from knowledge_check import generate_questions
import os
import logging

logging.basicConfig(level=logging.INFO)

if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'audio_file_path' not in st.session_state:
     st.session_state.audio_file_path = None
if 'source_text' not in st.session_state:
     st.session_state.source_text = None
if 'summary_metadata' not in st.session_state:
     st.session_state.summary_metadata = None



st.title("🎓 Навчальний агент")

summary_mode = st.selectbox(
    "Режим конспекту:",
    options=["short", "detailed"],
    index=0,
    help="short — короткий конспект, detailed — детальний конспект.",
)

summary_length = st.selectbox(
    "Розмір конспекту:",
    options=["short", "medium", "long"],
    index=1,
    help="Керує орієнтовною довжиною відповіді моделі.",
)

max_tokens = st.number_input(
    "Максимум токенів (0 = авто):",
    min_value=0,
    max_value=4096,
    value=0,
    step=32,
)

input_option = st.radio(
    "Виберіть джерело контенту:",
    ('Посилання на YouTube', 'Завантажити файл'),
    key="input_option_selector",
    horizontal=True
)


process_button_pressed = False 

if input_option == 'Посилання на YouTube':
    youtube_url = st.text_input("🔗 Встав лінк на відео з YouTube:", key="youtube_url_input")
    if st.button("Обробляти відео 🎥", key="process_youtube_button"):
        process_button_pressed = True
        st.session_state.summary = None
        st.session_state.questions = None
        st.session_state.show_results = False
        st.session_state.source_text = None
        st.session_state.audio_file_path = None 
        st.session_state.summary_metadata = None

        if youtube_url:
            transcript = None
            audio_file = None
            try:
                with st.spinner("📥 Завантажуємо аудіо..."):
                    audio_file = download_audio(youtube_url)
                    st.session_state.audio_file_path = audio_file
                with st.spinner("🧠 Розпізнаємо мову..."):
                    transcript = transcribe_audio(audio_file) 
                    st.session_state.source_text = transcript 

                if not transcript:
                    st.error("Не вдалося отримати транскрипцію.")

            except Exception as e:
                st.error(f"Сталася помилка під час обробки відео: {e}")
                logging.error(f"Error during YouTube processing: {e}")
                st.session_state.source_text = None 
                if audio_file and os.path.exists(audio_file):
                     try: os.remove(audio_file)
                     except Exception as remove_err: logging.warning(f"Could not remove temp audio file: {remove_err}")
                st.session_state.audio_file_path = None
        else:
            st.warning("⚠️ Будь ласка, встав лінк на відео.")
            process_button_pressed = False 

elif input_option == 'Завантажити файл':
    uploaded_file = st.file_uploader(
        "📂 Завантажте файл (txt, pdf, pptx):",
        type=['txt', 'pdf', 'pptx'],
        key="file_uploader_widget"
    )
    if uploaded_file is not None:
        if st.button("Обробляти файл 📄", key="process_file_button"):
            process_button_pressed = True
            st.session_state.summary = None
            st.session_state.questions = None
            st.session_state.show_results = False
            st.session_state.source_text = None
            st.session_state.audio_file_path = None # Файлу не буде
            st.session_state.summary_metadata = None

            file_type = uploaded_file.type
            extracted_text = None
            with st.spinner(f"Обробляємо файл {uploaded_file.name}..."):
                try:
                    if file_type == "application/pdf":
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                        extracted_text = extract_text_from_pptx(uploaded_file)
                    elif file_type == "text/plain":
                        extracted_text = extract_text_from_txt(uploaded_file)
                    else:
                        st.error("Непідтримуваний тип файлу.")

                    st.session_state.source_text = extracted_text # Зберігаємо вилучений текст

                    if not extracted_text:
                         st.error(f"Не вдалося вилучити текст з файлу '{uploaded_file.name}'.")

                except Exception as e:
                    st.error(f"Сталася помилка під час обробки файлу: {e}")
                    logging.error(f"Error processing uploaded file {uploaded_file.name}: {e}")
                    st.session_state.source_text = None # Очищаємо стан


if st.session_state.source_text:
    if process_button_pressed: 
        st.success("📝 Текст отримано:")
        st.text_area(
            "Початковий текст (фрагмент):",
            st.session_state.source_text[:2000] + ("..." if len(st.session_state.source_text) > 2000 else ""),
            height=150,
            disabled=True, 
            key="source_text_display"
        )

    if not st.session_state.summary:
        with st.spinner("✍️ Генеруємо конспект..."):
            summary_result = summarize_transcript_pipeline(
                transcript=st.session_state.source_text,
                mode=summary_mode,
                summary_length=summary_length,
                max_tokens=max_tokens if max_tokens > 0 else None,
            )
            st.session_state.summary = summary_result["summary"]
            st.session_state.summary_metadata = summary_result

            if not summary_result["summary"]:
                 st.error("Не вдалося створити конспект.")


if st.session_state.summary:
    st.success("📚 Конспект:")
    st.markdown(st.session_state.summary)
    if st.session_state.summary_metadata:
        metadata = st.session_state.summary_metadata
        st.caption(
            f"Мова: {metadata['language']} · Режим: {metadata['mode']} · "
            f"Розмір: {metadata['length']} · Compression ratio: {metadata['compression_ratio']:.3f}"
        )
    st.markdown("---")

    if not st.session_state.questions and not st.session_state.show_results: 
        if st.button("🤔 Перевірити знання (згенерувати питання)"):
            with st.spinner("Генеруємо питання..."):
                questions = generate_questions(st.session_state.summary, num_questions=5, q_type='multiple_choice')

            if questions:
                st.session_state.questions = questions
                st.session_state.current_question_index = 0
                st.session_state.user_answers = {}
                st.session_state.show_results = False
                st.rerun()
            else:
                st.warning("Не вдалося згенерувати питання.")
                st.session_state.questions = None



if st.session_state.questions and not st.session_state.show_results:
    q_index = st.session_state.current_question_index
    if 0 <= q_index < len(st.session_state.questions):
        q_data = st.session_state.questions[q_index]
        st.subheader(f"Питання {q_index + 1} з {len(st.session_state.questions)}")
        st.write(q_data.get('question', 'Текст питання відсутній'))
        options = q_data.get('options', {})
        options_list = list(options.items())
        radio_options = [f"{key}: {value}" for key, value in options_list]
        selected_index = None
        previous_answer = st.session_state.user_answers.get(q_index)
        if previous_answer:
            try:
                selected_index = [opt.split(":")[0] for opt in radio_options].index(previous_answer)
            except ValueError: selected_index = None
        user_choice = st.radio("Виберіть відповідь:", radio_options, key=f"q_{q_index}", index=selected_index)
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("⬅️ Попереднє", disabled=(q_index == 0)):
                if user_choice: st.session_state.user_answers[q_index] = user_choice.split(":")[0]
                st.session_state.current_question_index -= 1
                st.rerun()
        with col2:
            if q_index < len(st.session_state.questions) - 1:
                if st.button("Наступне ➡️"):
                    if user_choice: st.session_state.user_answers[q_index] = user_choice.split(":")[0]
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                if st.button("✅ Завершити тест"):
                    if user_choice: st.session_state.user_answers[q_index] = user_choice.split(":")[0]
                    st.session_state.show_results = True
                    st.rerun()
    else:
        st.error("Виникла помилка з індексом питання.")
        st.session_state.questions = None
        st.session_state.show_results = False



if st.session_state.show_results:
    st.subheader("Результати тестування:")
    score = 0
    if st.session_state.questions: 
        for i, q_data in enumerate(st.session_state.questions):
            user_ans = st.session_state.user_answers.get(i)
            correct_ans = q_data.get('correct_answer', 'N/A')
            question_text = q_data.get('question', f'Питання {i+1}') 
            options_display = q_data.get('options', {})

            st.markdown(f"**{question_text}**")
            for key, value in options_display.items():
                 st.write(f"  {key}: {value}") 

            st.write(f"Ваша відповідь: `{user_ans if user_ans else 'Немає'}`")
            st.write(f"Правильна відповідь: `{correct_ans}`")

            if user_ans == correct_ans:
                st.success("✔️ Правильно!")
                score += 1
            else:
                st.error("❌ Неправильно.")
            st.markdown("---")

        st.markdown(f"### **Ваш результат: {score} з {len(st.session_state.questions)}**")

        if st.button("🔄 Пройти ще раз / Згенерувати нові питання"):
            st.session_state.questions = None
            st.session_state.current_question_index = 0
            st.session_state.user_answers = {}
            st.session_state.show_results = False
            st.rerun() 

    else:
        st.warning("Немає даних про питання для відображення результатів.")


