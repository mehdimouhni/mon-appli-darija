import streamlit as st
import random
from gtts import gTTS
import io

st.set_page_config(page_title="Darija Master", page_icon="🇲🇦")

# Notre base de données simplifiée pour le test
data = {
    "🌟 Débutant": [
        {"d": "Salam", "f": "Bonjour"},
        {"d": "Labass", "f": "Ça va"},
        {"d": "Shoukran", "f": "Merci"},
        {"d": "Wakha", "f": "D'accord"}
    ],
    "🥙 Nourriture": [
        {"d": "Atay", "f": "Thé"},
        {"d": "Khoubz", "f": "Pain"},
        {"d": "Bghit n'akul", "f": "Je veux manger"}
    ]
}

if 'current_qa' not in st.session_state:
    theme = list(data.keys())[0]
    st.session_state.current_qa = random.choice(data[theme])
    st.session_state.options = []

st.title("🇲🇦 Apprendre le Darija")

# Audio
if st.button("🔈 Écouter la prononciation"):
    tts = gTTS(text=st.session_state.current_qa['d'], lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp, format='audio/mp3', autoplay=True)

st.subheader(f"Comment dit-on : {st.session_state.current_qa['d']} ?")

# Quiz
correct = st.session_state.current_qa['f']
if not st.session_state.options:
    st.session_state.options = [correct] + ["...", "...", "..."] # Temporaire pour le test

for opt in st.session_state.options:
    if st.button(opt):
        if opt == correct:
            st.success("Bravo !")
            if st.button("Suivant"):
                st.session_state.options = []
                st.rerun()
        else:
            st.error("Essaie encore !")
