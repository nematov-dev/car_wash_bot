import google.generativeai as genai
import os
import json
import time

# API kalitingizni muhit o'zgaruvchisidan olish tavsiya etiladi
genai.configure(api_key="AIzaSyCyStrvMC9Uzb9QfUxWHdIj3Q8tFQ5yofw")

def transcribe_audio_to_order(audio_file_path):
    # 1. To'g'ri model nomini ishlatish
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # 2. Audio faylni yuklash
    sample_file = genai.upload_file(path=audio_file_path)
    
    # 3. Fayl "Active" holatga kelishini kutish (kichik audio bo'lsa ham xavfsizlik uchun)
    while sample_file.state.name == "PROCESSING":
        time.sleep(1)
        sample_file = genai.get_file(sample_file.name)

    prompt = """
    Ushbu audioni diqqat bilan tinglang va avtomobil yuvish shoxobchasi buyurtmasini tahlil qiling.
    Faqatgina quyidagi formatdagi JSON ma'lumotni qaytaring, boshqa hech qanday izoh bermang:
    
    {
        "plate_number": "mashina raqami (masalan 01A777AA) bo'sh joylarsiz, katta harflarda",
        "price": yuvish narxi (faqat raqam tipida),
        "washer_name": "yuvuvchi (moykachi) ismi",
        "services_name": "xizmat nomi (masalan: sedan yuvish, salon va kuzov)"
    }
    
    Agar audioda ma'lumot bo'lmasa, qiymatni null deb ko'rsating.
    """
    
    try:
        # 4. Kontent yaratish
        response = model.generate_content([prompt, sample_file])
        
        # 5. JSONni tozalash va o'qish
        res_text = response.text
        # Markdown belgilarini olib tashlash
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0].strip()
        elif "```" in res_text:
            res_text = res_text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(res_text)
        
        # 6. Lug'at kalitlarini router kodingizga moslashtirish
        # Siz routerda 'plate', 'washer' kabi kalitlarni kutyapsiz
        return {
            "plate": data.get("plate_number"),
            "washer": data.get("washer_name"),
            "price": data.get("price"),
            "service": data.get("services_name")
        }
        
    except Exception as e:
        print(f"Gemini tahlil xatosi: {e}")
        return None
    finally:
        # Serverda joy egallamasligi uchun Gemini cloud'dan faylni o'chirish
        genai.delete_file(sample_file.name)