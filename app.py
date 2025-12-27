import streamlit as st
import requests
import os
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import random
from datetime import date as date_class

# .env dosyasından API key yükle
load_dotenv()
API_KEY = os.getenv('API_KEY', 'DEMO_KEY')

# ===== ÇOK DİLLİ METINLER =====
TEXTS = {
    'TR': {
        'page_title': 'Doğum Gününde Evren',
        'main_title': '🌌 Doğum Gününde Evren',
        'subtitle': "NASA'nın APOD arşivinden doğum gününüzdeki evren görüntüsünü keşfedin!",
        'select_date': '📅 Tarih Seçin',
        'birth_date': 'Doğum tarihinizi seçin:',
        'show_button': '🌌 Evreni Göster',
        'loading': '🔭 Evrenin derinliklerinden veri çekiliyor...',
        'success': '✨ Veriler yüklendi!',
        'description': '📖 Açıklama',
        'cosmic_analysis': '✨ Günlük Kozmik Analiz & Kehanet',
        'share': '📱 Paylaş',
        'share_text_template': '🌌 Doğduğum gün evrende bu görüntü vardı.\n✨ Evren benim için böyle görünüyordu.\n\n🔗 Görmek için:\n{url}',
        'download_hd': '📥 HD Resmi İndir',
        'footer': 'NASA APOD API kullanılarak oluşturulmuştur.',
        'disclaimer': 'Bu yorum, doğum haritanız ve bugünün gökyüzü konumları baz alınarak anlık hesaplanmıştır.'
    },
    'EN': {
        'page_title': 'Universe on Your Birthday',
        'main_title': '🌌 Universe on Your Birthday',
        'subtitle': "Discover the cosmic view from NASA's APOD archive on your birthday!",
        'select_date': '📅 Select Date',
        'birth_date': 'Select your birth date:',
        'show_button': '🌌 Show Universe',
        'loading': '🔭 Fetching data from the depths of universe...',
        'success': '✨ Data loaded!',
        'description': '📖 Description',
        'cosmic_analysis': '✨ Daily Cosmic Analysis & Prophecy',
        'share': '📱 Share',
        'share_text_template': '🌌 This was the universe on my birthday.\n✨ The cosmos looked like this for me.\n\n🔗 See it here:\n{url}',
        'download_hd': '📥 Download HD Image',
        'footer': 'Powered by NASA APOD API.',
        'disclaimer': 'This reading is calculated based on your birth chart and today\'s celestial positions.'
    }
}

# ===== PROSEDÜREL ASTROLOJİ İÇERİK HAVUZLARI =====
ASTRO_CONTENT = {
    'TR': {
        'energy': [
            "Bugün gökyüzündeki hizalanma, ruhsal frekansında beklenmedik bir kırılma yaratıyor.",
            "Kozmik rüzgarlar, geçmişten gelen bir döngüyü kapatman için seni zorluyor.",
            "Evrensel enerji, içindeki gizli potansiyeli ortaya çıkarmak için kapılarını aralıyor.",
            "Şu an gezegensel titreşimler, kaderin sana fısıldadığı mesajları güçlendiriyor.",
            "Bugün astral düzlemdeki dalgalanmalar, yeni bir başlangıcın habercisi.",
            "Kozmik akıştaki bu ani değişim, ruhunun derinliklerinde yankılanıyor.",
            "Evrenin senin için hazırladığı sürprizler, bugün kendini göstermeye başlıyor.",
            "Bugünkü gökyüzü haritası, içsel gücünü iki katına çıkarıyor.",
            "Astral enerjinin yoğunluğu, sezgilerinin doruğa ulaşmasını sağlıyor.",
            "Kozmik saatin şu anki konumu, hayatında kritik bir dönüm noktasına işaret ediyor.",
            "Bugün evrensel bilinç, seninle daha önce hiç olmadığı kadar uyumlu.",
            "Gökyüzündeki nadir görülen bu konfigürasyon, ruhsal kapasiteni genişletiyor.",
            "Bugünkü kozmik frekans, geçmiş yaşam deneyimlerini hatırlatıyor.",
            "Evrensel matris, bugün senin için özel bir şifre gönderiyor.",
            "Astral alan, bugün senin içindeki yaratıcı gücü tetikliyor."
        ],
        'planetary': [
            "Satürn'ün kısıtlayıcı etkisi, retrograd enerjisiyle birleşerek sabrını sınıyor.",
            "Venüs ve Mars arasındaki gerilimli açı, tutkularını yeniden gözden geçirmeni istiyor.",
            "Jüpiter'in genişletici enerjisi, umutlarını ve hayallerini büyütüyor.",
            "Merkür'ün geri hareketindeki yankılar, zihinsel netliğini test ediyor.",
            "Ay'ın bugünkü evresi, duygusal dengenin anahtarını elinde tutuyor.",
            "Neptün'ün mistik sisi, gerçekle hayal arasındaki çizgiyi bulanıklaştırıyor.",
            "Uranüs'ün şok dalgaları, beklenmedik değişimlere hazır olmanı gerektiriyor.",
            "Plüto'nun dönüştürücü gücü, eski kalıplarını kırmanı emrediyor.",
            "Mars'ın agresif enerjisi, cesaret gösterme zamanının geldiğini söylüyor.",
            "Venüs'ün harmonik titreşimi, ilişkilerinde denge aramanı öneriyor.",
            "Satürn-Plüto konjonksiyonu, köklü değişimler için zemin hazırlıyor.",
            "Merkür-Jüpiter açısı, öğrenme arzunu zirveye taşıyor.",
            "Ay'ın düğüm noktalarıyla teması, kadersel bir buluşmaya işaret ediyor.",
            "Güneş-Uranüs karşıtlığı, özgünlüğünü ifade etme cesareti veriyor.",
            "Chiron'un iyileştirici enerjisi, eski yaralarına merhem oluyor."
        ],
        'advice': [
            "Bugün karşına çıkan mavi rengine dikkat et, bir işaret olabilir.",
            "Rüyalarındaki sembolleri not al, evren sana fısıldıyor.",
            "Saat 11:11'i görürsen, bir dilek tut - bugün güçlü bir portal açık.",
            "Rastgele açılan kitap sayfalarına bak, mesaj orada saklı.",
            "Bugün kendiliğinden aklına gelen ilk düşünceye güven, sezgin haklı.",
            "Bir yabancının sana söyleyeceği rastgele söz, kaderinle ilintili.",
            "Bugün doğada yalnız zaman geçir, ruhun huzur bulacak.",
            "Aynaya bakarken gözlerinin derinliklerine bak, içindeki gücü gör.",
            "Bugün tekrarlayan sayı dizilerine dikkat et, evrensel şifre gizli.",
            "Sessizlikte otur ve nefes al, kozmik mesajlar gelecek.",
            "Rastlantı diye bir şey yok - bugün her detay anlamlı.",
            "Bir mum yak ve niyetini netleştir, manifestasyon enerjisi güçlü.",
            "Kristallerin enerjisine sarıl, bugün onların titreşimi seninkiyle uyumlu.",
            "Geçmişten gelen bir hatırayı serbest bırak, bugün bağışlama zamanı.",
            "Suyun akışını izle, hayatın yönünü gösterecek."
        ],
        'prediction': [
            "Yakında 3 rakamını sık görmeye başlayacaksın - yeni bir döngünün başlangıcı.",
            "Eski bir dosttan beklenmedik bir haber var, 7 gün içinde.",
            "Yeşil bir nesne, sana önemli bir fırsat getirecek - reddetme.",
            "Ay dolunayda, gizli bir gerçek açığa çıkacak.",
            "İçinden gelip bir şey satın almak isteyeceksin - al, zamanı gelmiş.",
            "Bir çocuk sana önemli bir ders verecek, küçümseme.",
            "Yolda bulacağın bir tüy, melek işareti - yolundasın.",
            "13. günde önemli bir karar vereceksin, korkma.",
            "Rüyanda su görürsen, duygusal temizlenme zamanı.",
            "Sarı renk bugünlerde etrafında toplanacak - bolluk geliyor.",
            "Bir ayna kırılırsa, eski bir dönemin sonu - üzülme.",
            "Kuş sürüsü göreceksin, özgürlük seni çağırıyor.",
            "Eski bir fotoğraf elindeyken duygusallaşacaksın - geçmişi bırak.",
            "Üçlü bir tesadüf yaşayacaksın - evren seninle konuşuyor.",
            "Karanlıkta bir ışık göreceksin - umudunu kaybetme."
        ]
    },
    'EN': {
        'energy': [
            "Today's celestial alignment creates an unexpected shift in your spiritual frequency.",
            "Cosmic winds are pushing you to close a cycle from your past.",
            "Universal energy opens its doors to reveal your hidden potential.",
            "Current planetary vibrations amplify the messages fate whispers to you.",
            "Today's astral fluctuations herald a new beginning for you.",
            "This sudden change in cosmic flow resonates in the depths of your soul.",
            "The surprises the universe prepared for you begin revealing themselves today.",
            "Today's sky map doubles your inner power.",
            "The intensity of astral energy brings your intuition to its peak.",
            "The current position of the cosmic clock points to a critical turning point in your life.",
            "Today, universal consciousness is more aligned with you than ever before.",
            "This rare configuration in the sky expands your spiritual capacity.",
            "Today's cosmic frequency reminds you of past life experiences.",
            "The universal matrix sends you a special code today.",
            "The astral field triggers the creative power within you today."
        ],
        'planetary': [
            "Saturn's restrictive effect tests your patience by combining with retrograde energy.",
            "The tense angle between Venus and Mars asks you to reconsider your passions.",
            "Jupiter's expansive energy magnifies your hopes and dreams.",
            "Mercury's retrograde echoes test your mental clarity.",
            "The Moon's current phase holds the key to your emotional balance.",
            "Neptune's mystical mist blurs the line between reality and fantasy.",
            "Uranus's shock waves require you to be ready for unexpected changes.",
            "Pluto's transformative power commands you to break your old patterns.",
            "Mars's aggressive energy says it's time to show courage.",
            "Venus's harmonic vibration suggests you seek balance in relationships.",
            "The Saturn-Pluto conjunction prepares ground for radical changes.",
            "The Mercury-Jupiter aspect brings your learning desire to its peak.",
            "The Moon's contact with the nodes points to a karmic meeting.",
            "The Sun-Uranus opposition gives you courage to express your authenticity.",
            "Chiron's healing energy soothes your old wounds."
        ],
        'advice': [
            "Notice the blue color you encounter today, it may be a sign.",
            "Note the symbols in your dreams, the universe is whispering to you.",
            "If you see 11:11, make a wish - a powerful portal is open today.",
            "Look at randomly opened book pages, the message is hidden there.",
            "Trust the first thought that comes to mind today, your intuition is right.",
            "A stranger's random words to you are linked to your destiny.",
            "Spend time alone in nature today, your soul will find peace.",
            "Look deep into your eyes in the mirror, see the power within.",
            "Notice repeating number sequences today, the universal code is hidden.",
            "Sit in silence and breathe, cosmic messages will come.",
            "There's no such thing as coincidence - every detail is meaningful today.",
            "Light a candle and clarify your intention, manifestation energy is strong.",
            "Embrace the energy of crystals, their vibration aligns with yours today.",
            "Release a memory from the past, today is time for forgiveness.",
            "Watch the flow of water, it will show life's direction."
        ],
        'prediction': [
            "Soon you'll start seeing the number 3 frequently - beginning of a new cycle.",
            "Unexpected news from an old friend awaits, within 7 days.",
            "A green object will bring you an important opportunity - don't refuse.",
            "At full moon, a hidden truth will be revealed.",
            "You'll feel like buying something impulsively - buy it, its time has come.",
            "A child will teach you an important lesson, don't underestimate.",
            "A feather you'll find on the road is an angel sign - you're on track.",
            "On the 13th day you'll make an important decision, don't fear.",
            "If you see water in your dream, it's time for emotional cleansing.",
            "Yellow color will gather around you these days - abundance is coming.",
            "If a mirror breaks, it's the end of an old era - don't grieve.",
            "You'll see a flock of birds, freedom is calling you.",
            "You'll get emotional holding an old photo - let go of the past.",
            "You'll experience a triple coincidence - the universe is talking to you.",
            "You'll see a light in the darkness - don't lose hope."
        ]
    }
}

# ===== BURÇ HESAPLAMA =====
ZODIAC_SIGNS = {
    'TR': ["Oğlak", "Kova", "Balık", "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay"],
    'EN': ["Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius"]
}

ZODIAC_RANGES = [
    (12, 22, 1, 19, 0),  # Oğlak/Capricorn
    (1, 20, 2, 18, 1),   # Kova/Aquarius
    (2, 19, 3, 20, 2),   # Balık/Pisces
    (3, 21, 4, 19, 3),   # Koç/Aries
    (4, 20, 5, 20, 4),   # Boğa/Taurus
    (5, 21, 6, 20, 5),   # İkizler/Gemini
    (6, 21, 7, 22, 6),   # Yengeç/Cancer
    (7, 23, 8, 22, 7),   # Aslan/Leo
    (8, 23, 9, 22, 8),   # Başak/Virgo
    (9, 23, 10, 22, 9),  # Terazi/Libra
    (10, 23, 11, 21, 10), # Akrep/Scorpio
    (11, 22, 12, 21, 11)  # Yay/Sagittarius
]

def get_zodiac_sign(day, month, lang='TR'):
    """Burç hesaplama"""
    for start_month, start_day, end_month, end_day, idx in ZODIAC_RANGES:
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return ZODIAC_SIGNS[lang][idx]
    return ZODIAC_SIGNS[lang][0]

def generate_dynamic_horoscope(birth_date, lang='TR'):
    """Deterministik prosedürel burç yorumu"""
    day = birth_date.day
    month = birth_date.month
    year = birth_date.year
    today = date_class.today()
    
    # Seed değeri
    seed_value = day + month * 100 + year + today.year * 10000 + today.month * 100 + today.day
    random.seed(seed_value)
    
    # Burcu hesapla
    zodiac = get_zodiac_sign(day, month, lang)
    
    # Her kategoriden rastgele seç
    content = ASTRO_CONTENT[lang]
    energy = random.choice(content['energy'])
    planetary = random.choice(content['planetary'])
    advice = random.choice(content['advice'])
    prediction = random.choice(content['prediction'])
    
    # Greeting
    if lang == 'TR':
        greeting = f"**Sevgili {zodiac},**"
        disclaimer = f"\n\n*{TEXTS['TR']['disclaimer']}*"
    else:
        greeting = f"**Dear {zodiac},**"
        disclaimer = f"\n\n*{TEXTS['EN']['disclaimer']}*"
    
    # Birleştir
    horoscope = f"{greeting}\n\n{energy} {planetary}\n\n{advice}\n\n🔮 {prediction}{disclaimer}"
    
    return horoscope

# ===== NASA APOD FONKSİYONU =====
def get_apod_data(date, api_key):
    """NASA APOD API'sinden veri çeker"""
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
        st.error(f"⚠️ Error: {e}")
        return None

def generate_apod_url(date):
    """NASA APOD sayfa URL'sini oluşturur"""
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

# ===== STREAMLIT SAYFA KONFIGÜRASYONU =====
st.set_page_config(
    page_title="Universe on Your Birthday",
    page_icon="🌌",
    layout="wide"
)

# ===== JOSEFIN SANS FONT & LAC İVERT TASARIM =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;700&display=swap');
    
    html, body, [class*="css"], * {
        font-family: 'Josefin Sans', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        background-image: url("https://www.transparenttextures.com/patterns/stardust.png"), 
                          linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        background-attachment: fixed;
        background-size: cover;
    }

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

    h1, h2, h3, p, div, span, label {
        color: #e0e0e0 !important;
        text-shadow: 0px 0px 10px rgba(0,0,0,0.5) !important;
    }
    
    div[data-testid="stDateInput"], .stRadio {
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        padding: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: #e0e0e0 !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== ANA UYGULAMA =====

# Dil Seçimi (Sağ Üstte)
col_title, col_lang = st.columns([4, 1])
with col_lang:
    language = st.radio("🌐", options=["TR", "EN"], horizontal=True, label_visibility="collapsed")

# Başlık
st.markdown(f"""
<h1 style="font-size: 2.8rem; text-align: center; margin: 1rem 0; 
            font-family: 'Josefin Sans', sans-serif; font-weight: 700;">
    {TEXTS[language]['main_title'].split('🌌')[0]}🌌 
    <span style="background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); 
                 -webkit-background-clip: text; 
                 -webkit-text-fill-color: transparent;">
        {TEXTS[language]['main_title'].split('🌌')[1]}
    </span>
</h1>
""", unsafe_allow_html=True)

st.markdown("---")
st.write(TEXTS[language]['subtitle'])

# Merkezi Alan
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    st.subheader(TEXTS[language]['select_date'])
    
    from datetime import datetime, date
    APOD_START_DATE = date(1995, 6, 16)
    TODAY = date.today()
    
    selected_date = st.date_input(
        TEXTS[language]['birth_date'],
        value=None,
        min_value=APOD_START_DATE,
        max_value=TODAY
    )
    
    if selected_date:
        if st.button(TEXTS[language]['show_button'], type="primary", use_container_width=True):
            with st.spinner(TEXTS[language]['loading']):
                apod_data = get_apod_data(selected_date, API_KEY)
                
                if apod_data:
                    st.success(TEXTS[language]['success'])
                    
                    try:
                        # Çeviri
                        translator = GoogleTranslator(source='en', target=language.lower())
                        title_en = apod_data.get('title', 'No Title')
                        explanation_en = apod_data.get('explanation', 'No description')
                        
                        title_tr = translator.translate(title_en) if language == 'TR' else title_en
                        explanation_tr = translator.translate(explanation_en) if language == 'TR' else explanation_en
                        
                        st.subheader(f"🌟 {title_tr}")
                        st.caption(f"📅 {apod_data.get('date', selected_date)}")
                        
                        # Görsel veya Video
                        media_type = apod_data.get('media_type', 'image')
                        
                        if media_type == 'image':
                            image_url = apod_data.get('url', '')
                            if image_url:
                                st.image(image_url, width='stretch')
                                
                                # HD İndirme Butonu
                                st.markdown("---")
                                try:
                                    hd_url = apod_data.get('hdurl', image_url)
                                    response = requests.get(hd_url, timeout=15)
                                    st.download_button(
                                        label=TEXTS[language]['download_hd'],
                                        data=response.content,
                                        file_name=f"nasa_apod_{selected_date.strftime('%Y%m%d')}.jpg",
                                        mime="image/jpeg",
                                        use_container_width=True
                                    )
                                except:
                                    st.info("HD image not available")
                        
                        elif media_type == 'video':
                            video_url = apod_data.get('url', '')
                            if video_url:
                                st.video(video_url)
                        
                        # Açıklama
                        st.markdown("---")
                        st.write(f"**{TEXTS[language]['description']}**")
                        st.markdown(f"<div style='text-align: justify;'>{explanation_tr}</div>", unsafe_allow_html=True)
                        
                        # Kozmik Analiz
                        st.markdown("---")
                        st.write(f"**{TEXTS[language]['cosmic_analysis']}**")
                        
                        horoscope_text = generate_dynamic_horoscope(selected_date, language)
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, rgba(10, 5, 40, 0.8), rgba(30, 10, 60, 0.8)); 
                                    padding: 20px; 
                                    border-radius: 15px; 
                                    border: 1px solid rgba(106, 17, 203, 0.3);
                                    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
                                    font-style: italic;
                                    line-height: 1.8;
                                    color: #e0d4f7;'>
                            {horoscope_text}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Paylaşım
                        st.markdown("---")
                        st.write(f"**{TEXTS[language]['share']}**")
                        
                        apod_page_url = generate_apod_url(selected_date)
                        share_text = TEXTS[language]['share_text_template'].format(url=apod_page_url)
                        
                        st.text_area(
                            "Share:",
                            value=share_text,
                            height=120,
                            label_visibility="collapsed"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)[:100]}")
    
    st.markdown("---")
    st.caption(TEXTS[language]['footer'])
