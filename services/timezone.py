import pytz
from datetime import datetime

UZB_TZ = pytz.timezone('Asia/Tashkent')

def get_uzb_now():
    return datetime.now(UZB_TZ)

def format_uzb_time(utc_dt):
    if not utc_dt:
        return "Noma'lum"
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    
    uzb_dt = utc_dt.astimezone(UZB_TZ)
    return uzb_dt.strftime('%H:%M %d.%m.%Y')