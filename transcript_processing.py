import google.generativeai as genai
import whisper
from utils import split_text
from config import GOOGLE_API_KEY
import streamlit as st
import logging

# Налаштування логування (рекомендовано)
logging.basicConfig(level=logging.INFO)

# Конфігурація Google API
try:
    # Використовуємо GOOGLE_API_KEY з config.py
    genai.configure(api_key=GOOGLE_API_KEY)
    logging.info("Google Generative AI configured successfully.")
except Exception as e:
    st.error(f"Помилка конфігурації Google API: {e}")
    # Можна додати st.stop() якщо конфігурація критична для запуску
    logging.error(f"Failed to configure Google API: {e}")

def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        logging.info(f"Audio transcribed successfully: {audio_path}")
        return result['text']
    except Exception as e:
        st.error(f"Помилка під час транскрипції аудіо: {e}")
        logging.error(f"Error during audio transcription for {audio_path}: {e}")
        return None

def summarize_chunk(chunk, i, model_name="gemini-2.0-flash"):
    prompt = f"""
    Це частина транскрипції лекції. Напиши короткий конспект ключових ідей і понять цієї частини українською мовою. Не переписуй дослівно, а передай суть стисло та зрозуміло.

    Частина {i + 1}:
    {chunk}

    Конспект Частини {i + 1}:
    """
    try:
        # Створення моделі Gemini
        model = genai.GenerativeModel(model_name)

        # Налаштування генерації (опціонально)
        generation_config = genai.types.GenerationConfig(
            temperature=0.5,
            # max_output_tokens=800 # Можна розкоментувати та налаштувати
        )

        # Виклик API Gemini
        response = model.generate_content(prompt, generation_config=generation_config)

        # Перевірка відповіді
        if response.parts:
            logging.info(f"Summary generated successfully for chunk {i+1}.")
            return response.text.strip()
        else:
            block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Невідома причина"
            logging.warning(f"Response for chunk {i+1} was empty or blocked. Reason: {block_reason}")
            st.warning(f"Конспект для частини {i+1} не згенеровано через обмеження безпеки або іншу проблему.")
            return f"[Конспект для частини {i+1} не згенеровано. Причина: {block_reason}]" # Повертаємо інформативне повідомлення

    except Exception as e:
        st.error(f"Помилка Gemini API під час генерації конспекту частини {i + 1}: {e}")
        logging.error(f"Gemini API error for chunk {i+1}: {e}")
        return f"[Помилка генерації конспекту для частини {i+1}: {e}]"


def generate_full_summary(transcript, model_name="gemini-2.0-flash"):
    try:
        chunks = split_text(transcript) # Використовуємо вашу функцію з utils.py
        logging.info(f"Transcript split into {len(chunks)} chunks.")
    except Exception as e:
        st.error(f"Помилка під час розділення тексту на частини: {e}")
        logging.error(f"Error splitting text into chunks: {e}")
        return None

    if not chunks:
        st.warning("Транскрипт порожній або не вдалося розділити на частини.")
        logging.warning("Transcript is empty or could not be split.")
        return ""

    partial_summaries = []
    processed_chunks = 0 # Лічильник успішно оброблених частин

    for i, chunk in enumerate(chunks):
        # Використовуємо Streamlit для відображення прогресу в main.py
        # st.info(f"Генеруємо конспект частини {i + 1} з {len(chunks)}...") # Це краще робити в main.py
        logging.info(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
        summary = summarize_chunk(chunk, i, model_name) # Викликаємо оновлену функцію

        # Додаємо лише якщо конспект валідний і не є повідомленням про помилку
        if summary and not summary.startswith("[Конспект для частини") and not summary.startswith("[Помилка генерації"):
            partial_summaries.append(f"Конспект Частини {i + 1}:\n{summary}")
            processed_chunks += 1
        else:
            # Помилка або блокування вже залоговані та показані в summarize_chunk
            pass # Не додаємо помилкові результати до фінального промпту

    if processed_chunks == 0: # Якщо жодна частина не була успішно оброблена
         st.error("Не вдалося згенерувати жодного часткового конспекту.")
         logging.error("Failed to generate any partial summaries.")
         return "Не вдалося згенерувати конспект через проблеми з обробкою частин."

    logging.info(f"Generated {processed_chunks} partial summaries. Combining...")
    # st.info("Об'єднуємо часткові конспекти в один загальний...") # Краще робити в main.py

    # Формування фінального запиту для Gemini
    final_prompt = f"""
    На основі цих часткових конспектів лекції, створи один єдиний, логічний та структурований загальний конспект українською мовою. Збережи ключові ідеї з кожної частини, але подай їх у зв'язному, читабельному форматі. Ігноруй мета-текст типу "[Конспект для частини...]".

    Часткові конспекти:
    """ + "\n\n".join(partial_summaries) + """

    Загальний структурований конспект лекції:
    """

    try:
        # Створення моделі Gemini
        model = genai.GenerativeModel(model_name)

        # Налаштування генерації (опціонально)
        generation_config = genai.types.GenerationConfig(
            temperature=0.6,
            # max_output_tokens=1500
        )

        # Виклик API Gemini
        response = model.generate_content(final_prompt, generation_config=generation_config)

        # Перевірка відповіді
        if response.parts:
            logging.info("Final summary generated successfully.")
            return response.text.strip()
        else:
            block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Невідома причина"
            st.error(f"Фінальний конспект не згенеровано або заблоковано. Причина: {block_reason}")
            logging.error(f"Final summary generation failed or was blocked. Reason: {block_reason}")
            # Повертаємо часткові конспекти як резервний варіант
            return "Не вдалося створити фінальний конспект. Ось часткові:\n\n" + "\n\n".join(partial_summaries)

    except Exception as e:
        st.error(f"Помилка Gemini API під час генерації фінального конспекту: {e}")
        logging.error(f"Gemini API error during final summary generation: {e}")
        # Повертаємо часткові конспекти як резервний варіант
        return "Помилка при створенні фінального конспекту. Ось часткові:\n\n" + "\n\n".join(partial_summaries)