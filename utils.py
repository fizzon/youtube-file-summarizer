import textwrap
import streamlit as st 
import logging
import io 


try:
    import PyPDF2
except ImportError:
    st.error("Будь ласка, встановіть бібліотеку pypdf2: pip install pypdf2")
   
try:
    from pptx import Presentation
except ImportError:
    st.error("Будь ласка, встановіть бібліотеку python-pptx: pip install python-pptx")
  


def split_text(text, max_length=3000):
    """Розбиває текст на частини заданої максимальної довжини."""
    if not isinstance(text, str):
        logging.error(f"split_text отримав не текстовий тип: {type(text)}")
        return [] 
  
    text = text.replace('\xa0', ' ')
    return textwrap.wrap(text, width=max_length, break_long_words=False, break_on_hyphens=False)



def extract_text_from_pdf(uploaded_file):
    """Вилучає текст з PDF-файлу."""
    text = ""
    try:
       
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        logging.info(f"Обробка PDF: {uploaded_file.name}, кількість сторінок: {len(pdf_reader.pages)}")
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                 text += page_text + "\n"
            else:
                 logging.warning(f"Не вдалося вилучити текст зі сторінки {i+1} файлу {uploaded_file.name}")
        logging.info(f"Текст з PDF {uploaded_file.name} вилучено успішно.")
        return text.strip() 
    except Exception as e:
        st.error(f"Помилка обробки PDF '{uploaded_file.name}': {e}")
        logging.error(f"Error processing PDF {uploaded_file.name}: {e}")
        return None 

def extract_text_from_pptx(uploaded_file):
    """Вилучає текст з PPTX-файлу."""
    text = ""
    try:
        prs = Presentation(io.BytesIO(uploaded_file.getvalue()))
        logging.info(f"Обробка PPTX: {uploaded_file.name}, кількість слайдів: {len(prs.slides)}")
        for slide_num, slide in enumerate(prs.slides):
            slide_text = ""
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    shape_text = shape.text.strip()
                    if shape_text: 
                         slide_text += shape_text + "\n" 
            if slide_text: 
                 text += f"--- Слайд {slide_num + 1} ---\n{slide_text.strip()}\n\n"
            else:
                 logging.warning(f"Не знайдено тексту на слайді {slide_num + 1} файлу {uploaded_file.name}")

        logging.info(f"Текст з PPTX {uploaded_file.name} вилучено успішно.")
        return text.strip() 
    except Exception as e:
        st.error(f"Помилка обробки PPTX '{uploaded_file.name}': {e}")
        logging.error(f"Error processing PPTX {uploaded_file.name}: {e}")
        return None #

def extract_text_from_txt(uploaded_file):
     """Вилучає текст з TXT-файлу."""
     try:
          text = uploaded_file.getvalue().decode("utf-8")
          logging.info(f"Текст з TXT {uploaded_file.name} вилучено успішно.")
          return text.strip()
     except UnicodeDecodeError:
          st.error(f"Помилка декодування TXT файлу '{uploaded_file.name}'. Спробуйте зберегти файл у кодуванні UTF-8.")
          logging.error(f"UnicodeDecodeError processing TXT {uploaded_file.name}")
          return None
     except Exception as e:
          st.error(f"Помилка обробки TXT '{uploaded_file.name}': {e}")
          logging.error(f"Error processing TXT {uploaded_file.name}: {e}")
          return None #
