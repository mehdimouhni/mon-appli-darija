import streamlit as st
import random
from gtts import gTTS
import io
import pandas as pd

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Darija Pro 🇲🇦", layout="wide")
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #2ecc71; }
    .stButton>button { border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_stdio=True)

# --- BASE DE DONNÉES ÉLARGIE (Inspirée de Speak Moroccan) ---
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui"}, {"d": "Lla", "f": "Non"}, {"d": "Afak", "f": "S'il te plaît"},
        {"d": "Shokran", "f": "Merci"}, {"d": "Wakha", "f": "D'accord"}, {"d": "Daba", "f": "Maintenant"},
        {"d": "Mashi moshkil", "f": "Pas de problème"}, {"d": "Safi", "f": "Ça suffit / Ok"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati...", "f": "Je m'appelle..."}, {"d": "Mnin nta?", "f": "D'où viens-tu ?"},
        {"d": "Msherefin", "f": "Enchanté"}, {"d": "Fin kheddam?", "f": "Où travailles-tu ?"},
        {"d": "Ma fhemtsh", "f": "Je n'ai pas compris"}
    ],
    "🛒 Marché & Prix": [
        {"d": "Chhal?", "f": "Combien ?"}, {"d": "Ghalia bzaf", "f": "C'est trop cher"},
        {"d": "Atini...", "f": "Donne-moi..."}, {"d": "Bghit hada", "f": "Je veux celui-là"}
    ]
}

# --- INITIALISATION DE LA MÉMOIRE ---
if 'mastery' not in st.session_state:
    # On initialise le score de maîtrise à 0 pour chaque mot
    st.session_state.mastery = {}
    for t in RAW_DATA:
        for m in RAW_DATA[t]:
            st.session_state.mastery[m['d']] = 0

if 'score' not in st.session_state: st.session_state.score = 0

# --- FONCTIONS LOGIQUES ---
def get_audio(text):
    # 'ar' avec un accent plus lent pour mieux décomposer
    tts = gTTS(text=text, lang='ar', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

def next_question():
    theme = st.session_state.current_theme
    # On pioche en priorité les mots non maîtrisés (score < 5)
    pool = [m for m in RAW_DATA[theme] if st.session_state.mastery[m['d']] < 5]
    if not pool: pool = RAW_DATA[theme] # Si tout est fini, on reset le thème
    
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"]) # Alternance automatique
    
    # Génération des options
    correct = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']
    others = [ (w['f'] if st.session_state.mode == "D->F" else w['d']) for w in RAW_DATA[theme] if w['d'] != st.session_state.current_word['d']]
    
    opts = random.sample(others, min(len(others), 3)) + [correct]
    random.shuffle(opts)
    st.session_state.options = opts
    st.session_state.answered = False

# --- INTERFACE ---
st.title("🇲🇦 Darija Master Pro")

# Barre latérale : Progression par thématique
with st.sidebar:
    st.header("📊 Tes Progrès")
    for t in RAW_DATA:
        total = len(RAW_DATA[t])
        # Un mot est "acquis" si son score de maîtrise est >= 5
        acquis = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        st.write(f"**{t}** ({acquis}/{total})")
        st.progress(acquis / total)
    
    st.divider()
    if st.button("Réinitialiser ma mémoire"):
        st.session_state.mastery = {k: 0 for k in st.session_state.mastery}
        st.rerun()

# Initialisation du jeu si vide
if 'current_word' not in st.session_state:
    st.session_state.current_theme = list(RAW_DATA.keys())[0]
    next_question()

# Zone de jeu
col_t, col_s = st.columns([2,1])
with col_t:
    theme_choice = st.selectbox("Choisir une thématique :", list(RAW_DATA.keys()), index=list(RAW_DATA.keys()).index(st.session_state.current_theme))
    if theme_choice != st.session_state.current_theme:
        st.session_state.current_theme = theme_choice
        next_question()
        st.rerun()

# Affichage de la question
st.write("---")
mode_label = "Traduisez vers le Français :" if st.session_state.mode == "D->F" else "Traduisez vers le Darija :"
st.write(f"### {mode_label}")

q_text = st.session_state.current_word['d'] if st.session_state.mode == "D->F" else st.session_state.current_word['f']
st.info(f"## {q_text}")

# Bouton Audio (uniquement si le mot affiché ou à deviner est en Darija)
if st.button("🔈 Prononciation"):
    audio = get_audio(st.session_state.current_word['d'])
    st.audio(audio, format='audio/mp3', autoplay=True)

# Réponses
correct_ans = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']

cols = st.columns(2)
for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        if st.button(opt, key=f"btn_{i}", use_container_width=True):
            if opt == correct_ans:
                if not st.session_state.answered:
                    st.success("🎯 Correct !")
                    st.session_state.mastery[st.session_state.current_word['d']] += 1
                    st.session_state.score += 1
                    st.session_state.answered = True
            else:
                st.error("Faux, réessaie !")
                st.session_state.mastery[st.session_state.current_word['d']] = max(0, st.session_state.mastery[st.session_state.current_word['d']] - 1)

if st.session_state.answered:
    if st.button("Mot suivant ➡️", type="primary"):
        next_question()
        st.rerun()

# Dictionnaire du thème en bas
with st.expander("📚 Voir le dictionnaire de ce thème"):
    df = pd.DataFrame(RAW_DATA[st.session_state.current_theme])
    st.table(df)
