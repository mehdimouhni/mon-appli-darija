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
    .arabe-text { font-family: 'Amiri', serif; font-size: 3.5rem; color: #065F46; direction: rtl; }
    .flashcard {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #10B981; margin-bottom: 20px;
    }
    .big-text { font-size: 2.5rem; font-weight: 600; color: #1F2937; margin: 5px 0; }
    .sub-text { color: #6B7280; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES AVEC ÉCRITURE ARABE ---
# d = darija phonétique, f = français, a = arabe (pour le robot)
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui", "a": "إييه"},
        {"d": "Lla", "f": "Non", "a": "لا"},
        {"d": "Afak", "f": "S'il te plaît", "a": "عافاك"},
        {"d": "Shokran", "f": "Merci", "a": "شكرا"},
        {"d": "Wakha", "f": "D'accord", "a": "وخا"},
        {"d": "Safi", "f": "C'est bon / Ok", "a": "صفي"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati...", "f": "Je m'appelle...", "a": "سميتي"},
        {"d": "Mnin nta?", "f": "D'où viens-tu ?", "a": "منين نتا؟"},
        {"d": "Msherefin", "f": "Enchanté", "a": "مشرفين"},
        {"d": "Ki dayer?", "f": "Comment vas-tu ?", "a": "كي داير؟"}
    ],
    "🏃 Verbes de Base": [
        {"d": "Mshi", "f": "Aller", "a": "مشي"},
        {"d": "Koul", "f": "Manger", "a": "كول"},
        {"d": "Shrab", "f": "Boire", "a": "شرب"},
        {"d": "Dir", "f": "Faire", "a": "دير"}
    ]
    # Note: On pourra compléter les autres thèmes de la même manière
}

# --- LOGIQUE SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'mastery' not in st.session_state: 
    st.session_state.mastery = {m['d']: 0 for t in RAW_DATA for m in RAW_DATA[t]}

def next_question():
    theme = st.session_state.current_theme
    pool = RAW_DATA[theme]
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"])
    
    correct = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']
    others = [(w['f'] if st.session_state.mode == "D->F" else w['d']) for w in pool if w['d'] != st.session_state.current_word['d']]
    
    random.shuffle(others)
    st.session_state.options = list(dict.fromkeys([correct] + others[:3]))
    random.shuffle(st.session_state.options)
    st.session_state.answered = False

# --- INTERFACE ---
if st.session_state.user is None:
    st.title("🇲🇦 Darija Master")
    name = st.text_input("Pseudo :")
    if st.button("Commencer"):
        if name:
            st.session_state.user = name
            st.rerun()
    st.stop()

with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.write("---")
    for t in RAW_DATA:
        mastered = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        st.write(f"**{t}** ({mastered}/{len(RAW_DATA[t])})")
        st.progress(mastered / len(RAW_DATA[t]))

if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

theme_choice = st.selectbox("🎯 Thème :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

# --- AFFICHAGE DE LA CARTE ---
word = st.session_state.current_word
instruction = "Traduisez en Français" if st.session_state.mode == "D->F" else "Traduisez en Darija"

st.markdown(f"""
    <div class="flashcard">
        <div class="sub-text">{instruction}</div>
        <div class="arabe-text">{word['a'] if st.session_state.mode == "D->F" else ""}</div>
        <div class="big-text">{word['d'] if st.session_state.mode == "D->F" else word['f']}</div>
    </div>
""", unsafe_allow_html=True)

# AUDIO (Utilise maintenant la version arabe 'a')
col1, col2 = st.columns(2)
with col1:
    if st.button("🔈 Écouter la vraie voix"):
        # ON ENVOIE LE TEXTE ARABE AU ROBOT (mieux compris)
        tts = gTTS(text=word['a'], lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)

# RÉPONSES
st.write("---")
correct_ans = word['f'] if st.session_state.mode == "D->F" else word['d']
cols = st.columns(2)
for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        if st.button(opt, key=f"btn_{i}", use_container_width=True):
            if opt == correct_ans:
                if not st.session_state.answered:
                    st.balloons()
                    st.session_state.mastery[word['d']] += 1
                    st.session_state.answered = True
            else:
                st.error(f"Faux ! C'était : {correct_ans}")
                st.session_state.answered = True

if st.session_state.answered:
    if st.button("Suivant ➡️", type="primary"):
        next_question()
        st.rerun()
