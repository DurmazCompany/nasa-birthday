import streamlit as st
import requests
import os
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import google.generativeai as genai

# .env dosyasından environment değişkenlerini yükle
load_dotenv()

# API keys
API_KEY = os.getenv('API_KEY', 'DEMO_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Gemini yapılandırması
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_apod_data(date, api_key):
    """NASA APOD API'sinden veri çeker."""
    try:
        if hasattr(date, 'strftime'):
            formatted_date = date.strftime('%Y-%m-%d')
        else:
            formatted_date = str(date)
        
        url = "https://api.nasa.gov/planetary/apod"
        params = {'api_key': api_key, 'date': formatted_date}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        st.error(f"⚠️ Hata: {e}")
        return None

def generate_apod_url(date):
    """NASA APOD sayfa URL'sini oluşturur."""
    if hasattr(date, 'strftime'):
        year = date.strftime('%y')
        month = date.strftime('%m')
        day = date.strftime('%d')
    else:
        from datetime import datetime
        dt = datetime.strptime(str(date), '%Y-%m-%d')
        year = dt.strftime('%y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')
    
    return f"https://apod.nasa.gov/apod/ap{year}{month}{day}.html"

def get_astrological_comment(date):
    """Gemini AI ile astrolojik yorum oluşturur."""
    try:
        if not GEMINI_API_KEY:
            return "🔮 Kozmik yorum için Gemini API KEY gerekli. Lütfen .env dosyasına GEMINI_API_KEY ekleyin."
        
        model = genai.GenerativeModel('gemini-pro')
        
        formatted_date = date.strftime('%d %B %Y')
        
        prompt = f"""Sen mistik bir astrologsun. {formatted_date} tarihinde doğan birinin burcunu ve o günkü gökyüzü enerjisini baz alarak 3-4 cümlelik, derin, motive edici ve gizemli bir yorum yap. Türkçe yanıt ver."""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"✨ Kozmik enerji şu an ulaşılamıyor... ({str(e)[:50]})"

def create_memory_card(image_url, date, user_name=None):
    """APOD görselinden hatıra kartı oluşturur."""
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        strip_height = 150
        strip_y = img.height - strip_height
        
        overlay_draw.rectangle(
            [(0, strip_y), (img.width, img.height)],
            fill=(0, 0, 0, 200)
        )
        
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
        
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 50)
            date_font = ImageFont.truetype("arial.ttf", 38)
            name_font = ImageFont.truetype("arial.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            date_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
        
        title_text = "🌌 Doğum Günümde Evren"
        date_text = f"📅 {date.strftime('%d.%m.%Y')}"
        
        text_y = strip_y + 25
        
        draw.text((40, text_y), title_text, fill=(255, 255, 255), font=title_font)
        draw.text((40, text_y + 65), date_text, fill=(106, 17, 203), font=date_font)
        
        if user_name:
            user_text = f"✨ {user_name}"
            text_bbox = draw.textbbox((0, 0), user_text, font=name_font)
            text_width = text_bbox[2] - text_bbox[0]
            x_pos = img.width - text_width - 40
            draw.text((x_pos, text_y + 65), user_text, fill=(255, 255, 255), font=name_font)
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        return output
        
    except Exception as e:
        st.error(f"❌ Hatıra kartı oluşturulamadı: {str(e)[:100]}")
        return None

def display_apod_content(date_obj, col=None, user_name=None):
    """APOD içeriğini gösterir."""
    ctx = col if col else st
    
    with st.spinner("🔭 Evrenin derinliklerinden veri çekiliyor..."):
        apod_data = get_apod_data(date_obj, API_KEY)
        
        if apod_data:
            ctx.success("✨ Veriler yüklendi!")
            
            try:
                translator = GoogleTranslator(source='en', target='tr')
                
                title_en = apod_data.get('title', 'Başlık Yok')
                explanation_en = apod_data.get('explanation', 'Açıklama Yok')
                
                title_tr = translator.translate(title_en)
                explanation_tr = translator.translate(explanation_en)
                
                ctx.subheader(f"🌟 {title_tr}")
                ctx.caption(f"📅 {apod_data.get('date', date_obj)}")
                
                media_type = apod_data.get('media_type', 'image')
                
                if media_type == 'image':
                    image_url = apod_data.get('url', '')
                    if image_url:
                        ctx.image(image_url, use_container_width=True)
                        
                        # Hatıra Kartı
                        ctx.markdown("---")
                        ctx.write("**🎨 Hatıra Kartı**")
                        
                        memory_card = create_memory_card(image_url, date_obj, user_name)
                        if memory_card:
                            filename = f"evren_{date_obj.strftime('%Y%m%d')}.jpg"
                            ctx.download_button(
                                label="📥 Hatıra Kartını İndir",
                                data=memory_card,
                                file_name=filename,
                                mime="image/jpeg",
                                use_container_width=True
                            )
                        
                        hdurl = apod_data.get('hdurl', '')
                        if hdurl:
                            ctx.markdown(f"🔗 [HD Görsel]({hdurl})")
                
                elif media_type == 'video':
                    video_url = apod_data.get('url', '')
                    if video_url:
                        ctx.video(video_url)
                
                # Açıklama
                ctx.markdown("---")
                ctx.write("**📖 Açıklama**")
                ctx.markdown(f"<div style='text-align: justify;'>{explanation_tr}</div>", unsafe_allow_html=True)
                
                # AI Astrolojik Yorum
                ctx.markdown("---")
                ctx.write("**✨ Kozmik Yorum**")
                astrological_comment = get_astrological_comment(date_obj)
                ctx.info(astrological_comment)
                
                # Paylaşım
                ctx.markdown("---")
                ctx.write("**📱 Paylaş**")
                
                apod_page_url = generate_apod_url(date_obj)
                share_text = f"""🌌 Doğduğum gün evrende bu görüntü vardı.
✨ Evren benim için böyle görünüyordu.

🔗 Görmek için:
{apod_page_url}"""
                
                ctx.text_area(
                    "Kopyala:",
                    value=share_text,
                    height=120,
                    key=f"share_{date_obj}",
                    label_visibility="collapsed"
                )
                
            except Exception as e:
                ctx.error(f"❌ Hata: {str(e)[:50]}")

# Sayfa yapılandırması
st.set_page_config(
    page_title="Doğum Gününde Evren",
    page_icon="🌌",
    layout="wide"
)

# YENİ TASARIM CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;700&display=swap');
    
    /* Genel Font Ayarı */
    html, body, [class*="css"] {
        font-family: 'Josefin Sans', sans-serif !important;
    }
    
    * {
        font-family: 'Josefin Sans', sans-serif !important;
    }
    
    /* Arka Plan: Derin Lacivert ve Yıldızlar */
    .stApp {
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        background-image: url("https://www.transparenttextures.com/patterns/stardust.png"), 
                          linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
        background-size: cover;
    }

    /* Buton Stili: Modern ve Parlak */
    .stButton > button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 117, 252, 0.4) !important;
    }

    /* Metin Okunabilirliği */
    h1, h2, h3, p, div, span, label {
        color: #e0e0e0 !important;
        text-shadow: 0px 0px 10px rgba(0,0,0,0.5) !important;
    }
    
    /* Input Alanları */
    div[data-testid="stDateInput"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        padding: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Text Area */
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: #e0e0e0 !important;
        font-family: 'Josefin Sans', monospace !important;
    }
    
    /* Text Input */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: #e0e0e0 !important;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ✨ Kişiselleştir")
    user_name = st.text_input(
        "Adınız (opsiyonel):",
        placeholder="Adınızı girin",
        help="Hatıra kartında görünecek isim"
    )
    
    if user_name:
        st.success(f"👋 Merhaba, {user_name}!")

# LAYOUT: İçeriği ortala
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    # Hero title
    st.markdown("""
    <h1 style="font-size: 2.8rem; text-align: center; margin: 2rem 0 1rem 0; 
                font-family: 'Josefin Sans', sans-serif; font-weight: 700;">
        🌌 Doğum Gününde 
        <span style="background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); 
                     -webkit-background-clip: text; 
                     -webkit-text-fill-color: transparent;">
            Evren
        </span>
    </h1>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.write("NASA'nın APOD arşivinden doğum gününüzdeki evren görüntüsünü keşfedin ve mistik kozmik yorumunuzu alın!")
    
    from datetime import datetime, date
    
    APOD_START_DATE = date(1995, 6, 16)
    TODAY = date.today()
    
    compare_mode = st.checkbox("🔄 Karşılaştırma Modu", help="İki farklı tarihi karşılaştırın")
    
    st.subheader("📅 Tarih Seçin")
    
    if compare_mode:
        col1, col2 = st.columns(2)
        with col1:
            date1 = st.date_input(
                "İlk Tarih:",
                value=None,
                min_value=APOD_START_DATE,
                max_value=TODAY,
                key="date1"
            )
        with col2:
            date2 = st.date_input(
                "İkinci Tarih:",
                value=None,
                min_value=APOD_START_DATE,
                max_value=TODAY,
                key="date2"
            )
        
        if date1 and date2:
            if st.button("🌌 Karşılaştır", type="primary", use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    display_apod_content(date1, st, user_name)
                with col_b:
                    display_apod_content(date2, st, user_name)
    else:
        selected_date = st.date_input(
            "Doğum tarihinizi seçin:",
            value=None,
            min_value=APOD_START_DATE,
            max_value=TODAY
        )
        
        if selected_date:
            if st.button("🌌 Evreni Göster", type="primary", use_container_width=True):
                display_apod_content(selected_date, user_name=user_name)
    
    st.markdown("---")
    st.caption("NASA APOD API & Gemini AI ile oluşturulmuştur.")
