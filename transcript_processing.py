import google.generativeai as genai
import whisper
from utils import split_text
import streamlit as st
import logging
from typing import Literal, TypedDict

logging.basicConfig(level=logging.INFO)

SummaryMode = Literal["short", "detailed"]
SummaryLength = Literal["short", "medium", "long"]


class SummaryResult(TypedDict):
    """Result object returned by the transcript summarization pipeline."""

    summary: str
    compression_ratio: float
    language: Literal["uk", "en"]
    mode: SummaryMode
    length: SummaryLength


LENGTH_TO_MAX_TOKENS: dict[SummaryLength, int] = {
    "short": 256,
    "medium": 512,
    "long": 1024,
}


def detect_transcript_language(text: str) -> Literal["uk", "en"]:
    """Detect transcript language using a lightweight character-based heuristic."""
    normalized_text = (text or "").lower()
    ukrainian_specific_chars = sum(normalized_text.count(char) for char in "іїєґ")
    cyrillic_chars = sum(1 for char in normalized_text if "а" <= char <= "я" or char in "іїєґ")

    if ukrainian_specific_chars > 0:
        return "uk"
    if cyrillic_chars > max(20, len(normalized_text) // 15):
        return "uk"
    return "en"


def _build_chunk_prompt(chunk: str, chunk_index: int, mode: SummaryMode, language: Literal["uk", "en"]) -> str:
    """Build chunk-level prompt according to selected mode and language."""
    if language == "uk":
        style_instruction = (
            "Напиши дуже стислий конспект (3-5 речень) ключових ідей." if mode == "short"
            else "Напиши деталізований конспект (8-12 речень) з ключовими ідеями, аргументами та прикладами."
        )
        return f"""
        Це частина транскрипції лекції українською мовою. {style_instruction}
        Не переписуй дослівно, а передай суть структуровано.

        Частина {chunk_index + 1}:
        {chunk}

        Конспект Частини {chunk_index + 1}:
        """

    style_instruction = (
        "Write a concise summary (3-5 sentences) with only the core ideas." if mode == "short"
        else "Write a detailed summary (8-12 sentences) with key arguments, concepts, and examples."
    )
    return f"""
    This is a part of a lecture transcript in English. {style_instruction}
    Do not copy text verbatim; capture the meaning clearly.

    Part {chunk_index + 1}:
    {chunk}

    Summary of Part {chunk_index + 1}:
    """


def _build_final_prompt(partial_summaries: list[str], mode: SummaryMode, language: Literal["uk", "en"]) -> str:
    """Build final aggregation prompt according to selected mode and language."""
    if language == "uk":
        depth_instruction = (
            "створи короткий фінальний конспект (1-2 абзаци)." if mode == "short"
            else "створи деталізований фінальний конспект з підзаголовками та логічною структурою."
        )
        return f"""
        На основі цих часткових конспектів лекції {depth_instruction}
        Збережи ключові ідеї з кожної частини та ігноруй мета-текст типу "[Конспект для частини...]".

        Часткові конспекти:
        """ + "\n\n".join(partial_summaries) + """

        Загальний структурований конспект лекції:
        """

    depth_instruction = (
        "create a short final summary (1-2 paragraphs)." if mode == "short"
        else "create a detailed final summary with logical sections and clear structure."
    )
    return f"""
    Based on these partial summaries, {depth_instruction}
    Keep important ideas from all parts and ignore metadata like "[Summary for part ...]".

    Partial summaries:
    """ + "\n\n".join(partial_summaries) + """

    Final structured lecture summary:
    """

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    logging.info("Google Generative AI configured successfully.")
except Exception as e:
    st.error(f"Помилка конфігурації Google API: {e}")
    logging.error(f"Failed to configure Google API: {e}")

def transcribe_audio(audio_path):
    """Transcribe audio file into text using Whisper."""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        logging.info(f"Audio transcribed successfully: {audio_path}")
        return result['text']
    except Exception as e:
        st.error(f"Помилка під час транскрипції аудіо: {e}")
        logging.error(f"Error during audio transcription for {audio_path}: {e}")
        return None

def summarize_chunk(
    chunk: str,
    i: int,
    mode: SummaryMode = "short",
    summary_length: SummaryLength = "medium",
    max_tokens: int | None = None,
    language: Literal["uk", "en"] = "en",
    model_name: str = "gemini-2.0-flash",
) -> str:
    """Summarize one transcript chunk with configurable depth and output length."""
    prompt = _build_chunk_prompt(chunk=chunk, chunk_index=i, mode=mode, language=language)
    try:
        model = genai.GenerativeModel(model_name)
        resolved_max_tokens = max_tokens if max_tokens is not None else LENGTH_TO_MAX_TOKENS[summary_length]

        generation_config = genai.types.GenerationConfig(
            temperature=0.5,
            max_output_tokens=resolved_max_tokens,
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


def summarize_transcript_pipeline(
    transcript: str,
    mode: SummaryMode = "short",
    summary_length: SummaryLength = "medium",
    max_tokens: int | None = None,
    model_name: str = "gemini-2.0-flash",
) -> SummaryResult:
    """Run full summarization pipeline: chunking → summarization → metrics → output."""
    try:
        chunks = split_text(transcript)
        logging.info(f"Transcript split into {len(chunks)} chunks.")
    except Exception as e:
        st.error(f"Помилка під час розділення тексту на частини: {e}")
        logging.error(f"Error splitting text into chunks: {e}")
        return {
            "summary": "",
            "compression_ratio": 0.0,
            "language": "en",
            "mode": mode,
            "length": summary_length,
        }

    if not chunks:
        st.warning("Транскрипт порожній або не вдалося розділити на частини.")
        logging.warning("Transcript is empty or could not be split.")
        return {
            "summary": "",
            "compression_ratio": 0.0,
            "language": "en",
            "mode": mode,
            "length": summary_length,
        }

    language = detect_transcript_language(transcript)
    logging.info("Detected transcript language: %s", language)

    partial_summaries = []
    processed_chunks = 0

    for i, chunk in enumerate(chunks):
        logging.info(f"Generating summary for chunk {i + 1}/{len(chunks)}...")
        summary = summarize_chunk(
            chunk,
            i,
            mode=mode,
            summary_length=summary_length,
            max_tokens=max_tokens,
            language=language,
            model_name=model_name,
        )

        if summary and not summary.startswith("[Конспект для частини") and not summary.startswith("[Помилка генерації"):
            partial_summaries.append(f"Конспект Частини {i + 1}:\n{summary}")
            processed_chunks += 1
        else:
           
            pass 

    if processed_chunks == 0:
        st.error("Не вдалося згенерувати жодного часткового конспекту.")
        logging.error("Failed to generate any partial summaries.")
        empty_message = "Не вдалося згенерувати конспект через проблеми з обробкою частин."
        return {
            "summary": empty_message,
            "compression_ratio": len(empty_message) / max(len(transcript), 1),
            "language": language,
            "mode": mode,
            "length": summary_length,
        }

    logging.info(f"Generated {processed_chunks} partial summaries. Combining...")

    final_prompt = _build_final_prompt(partial_summaries, mode=mode, language=language)

    try:
        model = genai.GenerativeModel(model_name)
        resolved_max_tokens = max_tokens if max_tokens is not None else LENGTH_TO_MAX_TOKENS[summary_length]

        generation_config = genai.types.GenerationConfig(
            temperature=0.6,
            max_output_tokens=resolved_max_tokens,

        )


        response = model.generate_content(final_prompt, generation_config=generation_config)


        if response.parts:
            logging.info("Final summary generated successfully.")
            final_summary = response.text.strip()
        else:
            block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Невідома причина"
            st.error(f"Фінальний конспект не згенеровано або заблоковано. Причина: {block_reason}")
            logging.error(f"Final summary generation failed or was blocked. Reason: {block_reason}")
            final_summary = "Не вдалося створити фінальний конспект. Ось часткові:\n\n" + "\n\n".join(partial_summaries)

    except Exception as e:
        st.error(f"Помилка Gemini API під час генерації фінального конспекту: {e}")
        logging.error(f"Gemini API error during final summary generation: {e}")
        final_summary = "Помилка при створенні фінального конспекту. Ось часткові:\n\n" + "\n\n".join(partial_summaries)

    compression_ratio = len(final_summary) / max(len(transcript), 1)
    logging.info("Compression ratio: %.4f", compression_ratio)

    return {
        "summary": final_summary,
        "compression_ratio": compression_ratio,
        "language": language,
        "mode": mode,
        "length": summary_length,
    }


def generate_full_summary(
    transcript: str,
    model_name: str = "gemini-2.0-flash",
    mode: SummaryMode = "short",
    summary_length: SummaryLength = "medium",
    max_tokens: int | None = None,
) -> str:
    """Backward-compatible wrapper that returns only final summary text."""
    result = summarize_transcript_pipeline(
        transcript=transcript,
        mode=mode,
        summary_length=summary_length,
        max_tokens=max_tokens,
        model_name=model_name,
    )
    return result["summary"]
