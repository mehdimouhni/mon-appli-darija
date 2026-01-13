import streamlit as st
import random
from gtts import gTTS
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Darija Master 🇲🇦", layout="centered")

# --- BASE DE DONNÉES ÉVOLUÉE ---
if 'vocabulaire' not in st.session_state:
    st.session_state.vocabulaire = {
        "👋 Salutations": [
            {"d": "Smiya", "f": "Prénom"},
            {"d": "Msherefin", "f": "Enchanté"},
            {"d": "Ki dayer?", "f": "Comment vas-tu ? (M)"},
            {"d": "Ki dayra?", "f": "Comment vas-tu ? (F)"},
            {"d": "Labass", "f": "Ça va / Pas de mal"},
            {"d": "Sbah l'khir", "f": "Bonjour (matin)"}
        ],
        "🥘 Nourriture & Café": [
            {"d": "Bghit n'shreb", "f": "Je veux boire"},
            {"d": "L'fatura afak", "f": "L'addition svp"},
            {"d": "Chhal hada?", "f": "Combien ça coûte ?"},
            {"d": "Ma fihsh l'har", "f": "Ce n'est pas pimenté"},
            {"d": "Atay", "f": "Thé"},
            {"d": "Khoubz", "f": "Pain"}
        ]
    }

# --- LOGIQUE DE JEU ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_word' not in st.session_state:
    st.session_state.theme = "👋 Salutations"
    st.session_state.answered = False
    
def generate_question():
    theme_words = st.session_state.vocabulaire[st.session_state.theme]
    st.session_state.current_word = random.choice(theme_words)
    correct = st.session_state.current_word['f']
    
    # On prend d'autres mots du même thème pour les faux choix
    others = [w['f'] for w in theme_words if w['f'] != correct]
    # On mélange pour avoir 3 ou 4 options max sans doublons
    random.shuffle(others)
    distracteurs = others[:3] 
    
    opts = list(set([correct] + distracteurs)) # set() évite les doublons
    random.shuffle(opts)
    st.session_state.options = opts
    st.session_state.answered = False

if 'options' not in st.session_state or not st.session_state.options:
    generate_question()

# --- INTERFACE ---
st.title("🇲🇦 Darija Master")
st.write(f"⭐ Score : **{st.session_state.score}**")

# Choix du thème
theme_selection = st.selectbox("Thématique :", list(st.session_state.vocabulaire.keys()))
if theme_selection != st.session_state.theme:
    st.session_state.theme = theme_selection
    generate_question()
    st.rerun()

st.divider()

# Question et Audio
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Comment dit-on :")
    st.info(f"### {st.session_state.current_word['d']}")
with col2:
    if st.button("🔈 Audio"):
        tts = gTTS(text=st.session_state.current_word['d'], lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)

# Boutons de réponse (avec clés uniques pour éviter l'erreur rouge)
st.write("---")
for i, opt in enumerate(st.session_state.options):
    if st.button(opt, key=f"btn_{i}"):
        if opt == st.session_state.current_word['f'] and not st.session_state.answered:
            st.success("🎯 Bravo !")
            st.session_state.score += 1
            st.session_state.answered = True
        elif opt != st.session_state.current_word['f']:
            st.error("Ce n'est pas ça...")

if st.session_state.answered:
    if st.button("Mot suivant ➡️"):
        generate_question()
        st.rerun()
