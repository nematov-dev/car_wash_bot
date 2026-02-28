import google.generativeai as genai
import os
import json

genai.configure(api_key="AIzaSyCyStrvMC9Uzb9QfUxWHdIj3Q8tFQ5yofw")

# Audio to text

def transcribe_audio_to_order(audio_file_path):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    sample_file = genai.upload_file(path=audio_file_path)
    
    prompt = """
    Ushbu audioni tinglang va avtomobil yuvish shoxobchasi uchun buyurtma ma'lumotlarini JSON formatida qaytaring.
    Menga faqat JSON kerak, boshqa matn kerak emas.
    Format quyidagicha bo'lsin:
    {
        "plate_number": "mashina raqami (masalan 01A777AA) bo'sh joylarsiz.",
        "price": "yuvish narxi (faqat raqam)",
        "washer_name": "yuvuvchi ismi",
        "services_name": "yuvish xizmatlari nomlari (maslan moyka)"
    }
    Agar biror ma'lumot audioda bo'lmasa, null deb yozing.
    """
    
    response = model.generate_content([prompt, sample_file])
    
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    print("Raw response from Gemini:", raw_text) 
    return json.loads(raw_text)