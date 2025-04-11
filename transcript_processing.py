import google.generativeai as genai
import whisper
from utils import split_text
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    logging.info("Google Generative AI configured successfully.")
except Exception as e:
    st.error(f"Помилка конфігурації Google API: {e}")
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
        model = genai.GenerativeModel(model_name)

        generation_config = genai.types.GenerationConfig(
            temperature=0.5,
        )

        response = model.generate_content(prompt, generation_config=generation_config)

        if response.parts:
            logging.info(f"Summary generated successfully for chunk {i+1}.")
            return response.text.strip()
        else:
            block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Невідома причина"
            logging.warning(f"Response for chunk {i+1} was empty or blocked. Reason: {block_reason}")
            st.warning(f"Конспект для частини {i+1} не згенеровано через обмеження безпеки або іншу проблему.")
            return f"[Конспект для частини {i+1} не згенеровано. Причина: {block_reason}]" 

    except Exception as e:
        st.error(f"Помилка Gemini API під час генерації конспекту частини {i + 1}: {e}")
        logging.error(f"Gemini API error for chunk {i+1}: {e}")
        return f"[Помилка генерації конспекту для частини {i+1}: {e}]"


def generate_full_summary(transcript, model_name="gemini-2.0-flash"):
    try:
        chunks = split_text(transcript) 
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
    processed_chunks = 0 

    for i, chunk in enumerate(chunks):
        logging.info(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
        summary = summarize_chunk(chunk, i, model_name)

        if summary and not summary.startswith("[Конспект для частини") and not summary.startswith("[Помилка генерації"):
            partial_summaries.append(f"Конспект Частини {i + 1}:\n{summary}")
            processed_chunks += 1
        else:
           
            pass 

    if processed_chunks == 0: 
         st.error("Не вдалося згенерувати жодного часткового конспекту.")
         logging.error("Failed to generate any partial summaries.")
         return "Не вдалося згенерувати конспект через проблеми з обробкою частин."

    logging.info(f"Generated {processed_chunks} partial summaries. Combining...")



    final_prompt = f"""
    На основі цих часткових конспектів лекції, створи один єдиний, логічний та структурований загальний конспект українською мовою. Збережи ключові ідеї з кожної частини, але подай їх у зв'язному, читабельному форматі. Ігноруй мета-текст типу "[Конспект для частини...]".

    Часткові конспекти:
    """ + "\n\n".join(partial_summaries) + """

    Загальний структурований конспект лекції:
    """

    try:
        model = genai.GenerativeModel(model_name)

        generation_config = genai.types.GenerationConfig(
            temperature=0.6,

        )


        response = model.generate_content(final_prompt, generation_config=generation_config)


        if response.parts:
            logging.info("Final summary generated successfully.")
            return response.text.strip()
        else:
            block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Невідома причина"
            st.error(f"Фінальний конспект не згенеровано або заблоковано. Причина: {block_reason}")
            logging.error(f"Final summary generation failed or was blocked. Reason: {block_reason}")
            return "Не вдалося створити фінальний конспект. Ось часткові:\n\n" + "\n\n".join(partial_summaries)

    except Exception as e:
        st.error(f"Помилка Gemini API під час генерації фінального конспекту: {e}")
        logging.error(f"Gemini API error during final summary generation: {e}")
        return "Помилка при створенні фінального конспекту. Ось часткові:\n\n" + "\n\n".join(partial_summaries)
