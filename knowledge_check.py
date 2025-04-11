import json
import random
import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY
import logging

def generate_questions(summary_text, num_questions=5, q_type='multiple_choice', model_name="models/gemini-2.0-flash-lite"): # Можливо, Pro краще для цього
    """Генерує питання на основі конспекту за допомогою Gemini."""
    if q_type == 'multiple_choice':
        prompt = f"""
        На основі наданого нижче конспекту, згенеруй {num_questions} запитань з чотирма варіантами відповіді (A, B, C, D) для перевірки розуміння матеріалу. Чітко вкажи правильний варіант відповіді. Переконайся, що питання та варіанти стосуються ВИКЛЮЧНО наданого тексту конспекту. Надай результат у форматі JSON списку об'єктів. Кожен об'єкт повинен мати такі ключі: "question" (текст питання), "options" (словник з ключами "A", "B", "C", "D" та текстами варіантів) та "correct_answer" (літера правильного варіанту, наприклад "C").

        Конспект:
        ---
        {summary_text}
        ---

        JSON відповідь:
        """
    elif q_type == 'flashcards':
         prompt = f"""
        На основі наданого нижче конспекту, згенеруй {num_questions} флеш-карток (термін/питання - визначення/відповідь) для самоперевірки. Створи картки, що покривають ключові поняття з конспекту. Надай результат у форматі JSON списку об'єктів. Кожен об'єкт повинен мати ключі "front" (лицьова сторона картки: термін або коротке питання) та "back" (зворотна сторона картки: визначення або відповідь).

        Конспект:
        ---
        {summary_text}
        ---

        JSON відповідь:
        """
    else: 
        st.error("Непідтримуваний тип питань.")
        return None

    try:

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()

        questions_data = json.loads(cleaned_response_text)
        random.shuffle(questions_data)
        return questions_data

    except json.JSONDecodeError as json_err:
        st.error(f"Помилка обробки відповіді від Gemini (неправильний JSON): {json_err}")
        logging.error(f"JSON Decode Error: {json_err}\nRaw Response:\n{response.text}")
        return None
    except Exception as e:
        st.error(f"Помилка під час генерації питань: {e}")
        logging.error(f"Error generating questions: {e}")
        return None
