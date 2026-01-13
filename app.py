import streamlit as st
import random
from gtts import gTTS
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Darija Master Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Amiri:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .arabe-text { font-family: 'Amiri', serif; font-size: 3rem; color: #065F46; direction: rtl; }
    .arabe-btn { font-family: 'Amiri', serif; font-size: 1.2rem; }
    .flashcard {
        background-color: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #10B981; margin-bottom: 20px;
    }
    .stButton>button { border-radius: 10px; height: auto; padding: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES COMPLÈTE (12 THÈMES) ---
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui", "a": "إييه"}, {"d": "Lla", "f": "Non", "a": "لا"},
        {"d": "Afak", "f": "S'il te plaît", "a": "عافاك"}, {"d": "Shokran", "f": "Merci", "a": "شكرا"},
        {"d": "Wakha", "f": "D'accord", "a": "وخا"}, {"d": "Safi", "f": "C'est bon", "a": "صفي"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati", "f": "Je m'appelle", "a": "سميتي"}, {"d": "Msherefin", "f": "Enchanté", "a": "مشرفين"},
        {"d": "Ki dayer?", "f": "Comment vas-tu ?", "a": "كي داير؟"}, {"d": "Labass", "f": "Ça va bien", "a": "لباس"}
    ],
    "🔢 Chiffres": [
        {"d": "Wahed", "f": "Un", "a": "واحد"}, {"d": "Jouj", "f": "Deux", "a": "جوج"},
        {"d": "Tlata", "f": "Trois", "a": "تلاتة"}, {"d": "Ashra", "f": "Dix", "a": "عشرة"}
    ],
    "🏃 Verbes": [
        {"d": "Mshi", "f": "Aller", "a": "مشي"}, {"d": "Koul", "f": "Manger", "a": "كول"},
        {"d": "Shrab", "f": "Boire", "a": "شرب"}, {"d": "N'ass", "f": "Dormir", "a": "نعس"}
    ],
    "🚕 Transport": [
        {"d": "Fin taxi?", "f": "Où est le taxi ?", "a": "فين طاكسي؟"}, {"d": "Hna afak", "f": "Ici svp", "a": "هنا عافاك"}
    ],
    "👕 Shopping": [
        {"d": "Chhal?", "f": "Combien ?", "a": "شحال؟"}, {"d": "Ghalia", "f": "Cher", "a": "غالية"}
    ],
    "🏠 Famille": [
        {"d": "Baba", "f": "Papa", "a": "بابا"}, {"d": "Mama", "f": "Maman", "a": "ماما"}
    ],
    "⏰ Temps": [
        {"d": "L'youm", "f": "Aujourd'hui", "a": "ليوم"}, {"d": "Ghedda", "f": "Demain", "a": "غدا"}
    ],
    "🥗 Nourriture": [
        {"d": "Atay", "f": "Thé", "a": "اتاي"}, {"d": "Bnin", "f": "Délicieux", "a": "بنين"}
    ],
    "🌦️ Météo": [
        {"d": "Skhun", "f": "Chaud", "a": "سخون"}, {"d": "Bard", "f": "Froid", "a": "برد"}
    ],
    "🚑 Santé": [
        {"d": "Tbib", "f": "Docteur", "a": "طبيب"}, {"d": "Ateqni", "f": "Aidez-moi", "a": "عتقني"}
    ],
    "🗣️ Phrases": [
        {"d": "Ma fhemtsh", "f": "Pas compris", "a": "ما فهمتش"}, {"d": "Fiyya l'jou'e", "f": "J'ai faim", "a": "فيا الجوع"}
    ]
}

# --- INITIALISATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'mastery' not in st.session_state: 
    st.session_state.mastery = {m['d']: 0 for t in RAW_DATA for m in RAW_DATA[t]}

def play_audio(text_ar):
    tts = gTTS(text=text_ar, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3', autoplay=True)

def next_question():
    theme = st.session_state.current_theme
    pool = RAW_DATA[theme]
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"])
    
    # Préparation des options
    correct_obj = st.session_state.current_word
    others = [w for w in pool if w['d'] != correct_obj['d']]
    random.shuffle(others)
    st.session_state.options_objects = list(dict.fromkeys([correct_obj] + others[:3]))
    random.shuffle(st.session_state.options_objects)
    st.session_state.answered = False

# --- LOGIN ---
if st.session_state.user is None:
    st.title("🇲🇦 Darija Master")
    name = st.text_input("Pseudo :")
    if st.button("Lancer"):
        if name: st.session_state.user = name; st.rerun()
    st.stop()

# --- SIDEBAR & PROGRESSION ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.subheader("📊 Progression")
    for t in RAW_DATA:
        total = len(RAW_DATA[t])
        done = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        st.write(f"{t} ({done}/{total})")
        st.progress(done / total if total > 0 else 0)

# --- JEU ---
if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

theme_choice = st.selectbox("🎯 Thème :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

word = st.session_state.current_word
st.markdown(f"""<div class="flashcard">
    <div style="color:#6B7280">{"En Français ?" if st.session_state.mode == "D->F" else "En Darija ?"}</div>
    <div class="arabe-text">{word['a'] if st.session_state.mode == "D->F" else ""}</div>
    <div style="font-size:2.5rem; font-weight:600">{word['d'] if st.session_state.mode == "D->F" else word['f']}</div>
</div>""", unsafe_allow_html=True)

# RÉPONSES AVEC AUDIO
cols = st.columns(2)
for i, opt in enumerate(st.session_state.options_objects):
    with cols[i % 2]:
        # Bouton de réponse (Bilingue si Darija)
        label = opt['f'] if st.session_state.mode == "D->F" else f"{opt['d']} / {opt['a']}"
        if st.button(label, key=f"ans_{i}", use_container_width=True):
            if opt['d'] == word['d']:
                if not st.session_state.answered:
                    st.success("Bravo !")
                    st.session_state.mastery[word['d']] += 1
                    st.session_state.answered = True
                    st.balloons()
            else:
                st.error("Raté !")
        
        # Petit bouton audio sous la réponse si mode F->D
        if st.session_state.mode == "F->D":
            if st.button(f"🔈 Écouter", key=f"vol_{i}"):
                play_audio(opt['a'])

if st.session_state.answered:
    if st.button("Suivant ➡️", type="primary"):
        next_question(); st.rerun()

# --- DICTIONNAIRE ---
st.divider()
with st.expander("📚 Dictionnaire du thème"):
    for item in RAW_DATA[st.session_state.current_theme]:
        col_d1, col_d2 = st.columns([3, 1])
        col_d1.write(f"**{item['f']}** = {item['d']} ({item['a']})")
        if col_d2.button("🔈", key=f"dict_{item['d']}"):
            play_audio(item['a'])
