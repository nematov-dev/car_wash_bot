# 🚗 Carwash AI Agent Bot

**Maqsad:**  

Telegram orqali avtomoyka xizmatlarini boshqarish uchun AI agent.
Loyihaning asosiy vazifasi:

User
- Mashinasini ro‘yxatdan o‘tkazish  
- Buyurtmalarini ko'rish (status: washing, done, cancelled)
- Bir mashina bir nechta foydalanuvchi hisobida bo‘lishi mumkin  
- Holat haqida xabarnomalar olish
- Xizmat ko'rsatuvchi haqida ma'lumot

Admin
- Audio orqali buyurtma yaratish.
- Buyurtma holatini inline knopka orqali o‘zgartirish
- Service , Washer , Admin ma’lumotlarini boshqarish (add/update/delete)
- Xabarnomalar yuborish
- Admin uchun statistikani ko‘rsatish (kunlik, haftalik, oylik)  (excel)

---

## ⚡ Texnologiyalar

- **Python 3.11+**  
- **Aiogram 3.x** – Telegram bot framework  
- **SQLAlchemy** – ORM  
- **PostgreSQL** – Database  
- **python-decouple** – sensitive ma’lumotlarni `.env` orqali boshqarish  
- **Psycopg2** – PostgreSQL driver  

---

<table align="center">
  <tr>
    <h2 align="center" >Admin bo'lim</h2>
    <td align="center" valign="bottom">
      <img src="https://github.com/user-attachments/assets/9a20fd65-b6a9-489b-952f-ea3fcf1f86bd" width="200"/><br>
      <sub><b>Audio buyurtma qabul qilish</b></sub>
    </td>
    <td align="center" valign="bottom">
      <img src="https://github.com/user-attachments/assets/031915ff-dc8e-474f-8d58-47c2b1637bda" width="200"/><br>
      <sub><b>Admin panel</b></sub>
    </td>
    <td align="center" valign="bottom">
      <img src="https://github.com/user-attachments/assets/c481114a-483c-4788-91b9-eec46f8506d5" width="230"/><br>
      <sub><b>Hisobot</b></sub>
    </td>
  </tr>
</table>
