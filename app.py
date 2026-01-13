import streamlit as st
import random
from gtts import gTTS
import io

# --- 1. CONFIGURATION ET CORRECTION DU BUG ---
st.set_page_config(page_title="Darija Master Pro 🇲🇦", layout="wide")

# C'est ici que l'erreur se trouvait. J'ai remis "unsafe_allow_html=True"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    /* Design des cartes */
    .flashcard {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
        border-top: 6px solid #2ecc71;
    }
    
    /* Gros texte */
    .big-text {
        color: #2c3e50;
        font-size: 3rem;
        font-weight: 600;
        margin: 10px 0;
    }
    
    /* Sous-titre discret */
    .sub-text {
        color: #7f8c8d;
        font-size: 1.2rem;
    }

    /* Boutons stylisés */
    .stButton>button {
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
        border: 2px solid #ecf0f1;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #2ecc71;
        color: #2ecc71;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES COMPLÈTE ---
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui"}, {"d": "Lla", "f": "Non"}, {"d": "Afak", "f": "S'il te plaît"},
        {"d": "Shokran", "f": "Merci"}, {"d": "Wakha", "f": "D'accord"}, {"d": "Safi", "f": "C'est bon / Ok"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati...", "f": "Je m'appelle..."}, {"d": "Mnin nta?", "f": "D'où viens-tu ?"},
        {"d": "Msherefin", "f": "Enchanté"}, {"d": "Ki dayer?", "f": "Comment vas-tu ?"}
    ],
    "🏃 Verbes de Base": [
        {"d": "Mshi", "f": "Aller"}, {"d": "Koul", "f": "Manger"}, {"d": "Shrab", "f": "Boire"},
        {"d": "Dir", "f": "Faire"}, {"d": "N'ass", "f": "Dormir"}, {"d": "Shouf", "f": "Regarder"}
    ],
    "🗣️ Premières Phrases": [
        {"d": "Bghit n'mshi l...", "f": "Je veux aller à..."}, {"d": "Fiyya l'jou'e", "f": "J'ai faim"},
        {"d": "Twahashtek", "f": "Tu me manques"}, {"d": "Ma fhemtsh", "f": "Je n'ai pas compris"}
    ],
    "🔢 Chiffres": [
        {"d": "Wahed", "f": "Un"}, {"d": "Jouj", "f": "Deux"}, {"d": "Tlata", "f": "Trois"},
        {"d": "Arba'a", "f": "Quatre"}, {"d": "Khamsa", "f": "Cinq"}, {"d": "Ashra", "f": "Dix"}
    ]
}

# --- 3. INITIALISATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'mastery' not in st.session_state: 
    st.session_state.mastery = {m['d']: 0 for t in RAW_DATA for m in RAW_DATA[t]}
if 'reports' not in st.session_state: st.session_state.reports = []

# --- 4. ÉCRAN DE LOGIN ---
if st.session_state.user is None:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🇲🇦 Darija Master")
        st.write("Connecte-toi pour sauvegarder ta session (temporaire).")
        name = st.text_input("Ton prénom :")
        if st.button("🚀 Commencer l'aventure", type="primary"):
            if name:
                st.session_state.user = name
                st.rerun()
    st.stop()

# --- 5. LOGIQUE DU JEU ---
def next_question():
    theme = st.session_state.current_theme
    pool = RAW_DATA[theme]
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"])
    
    correct = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']
    others = [(w['f'] if st.session_state.mode == "D->F" else w['d']) for w in pool if w['d'] != st.session_state.current_word['d']]
    
    random.shuffle(others)
    opts = list(dict.fromkeys([correct] + others[:3])) # Anti-doublons
    random.shuffle(opts)
    
    st.session_state.options = opts
    st.session_state.answered = False

if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

# --- 6. INTERFACE PRINCIPALE ---
# Barre latérale
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.write("---")
    st.subheader("📊 Progression")
    for t in RAW_DATA:
        total = len(RAW_DATA[t])
        acquis = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        st.write(f"{t}")
        st.progress(acquis / total)
    
    if st.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

# Zone Principale
theme_choice = st.selectbox("🎯 Changer de thème :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

# Carte de question (Design HTML)
question_text = st.session_state.current_word['d'] if st.session_state.mode == "D->F" else st.session_state.current_word['f']
instruction = "Comment dit-on en Français ?" if st.session_state.mode == "D->F" else "Comment dit-on en Darija ?"

st.markdown(f"""
    <div class="flashcard">
        <div class="sub-text">{instruction}</div>
        <div class="big-text">{question_text}</div>
    </div>
""", unsafe_allow_html=True)

# Boutons Audio & Signalement
col_a, col_b = st.columns([1, 1])
with col_a:
    # Audio seulement utile si le mot affiché est en Arabe OU pour écouter la réponse
    if st.button("🔈 Écouter la prononciation"):
        tts = gTTS(text=st.session_state.current_word['d'], lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
with col_b:
    if st.button("⚠️ Signaler une erreur"):
        st.session_state.reports.append(st.session_state.current_word)
        st.toast("Merci, c'est noté !", icon="✅")

# Options de réponse
st.write("---")
cols = st.columns(2)
correct_ans = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']

for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        if st.button(opt, key=f"btn_{i}", use_container_width=True):
            if opt == correct_ans:
                if not st.session_state.answered:
                    st.balloons()
                    st.success("✨ Excellente réponse !")
                    st.session_state.mastery[st.session_state.current_word['d']] += 1
                    st.session_state.answered = True
            else:
                st.error("Oups, essaie encore !")

# Bouton Suivant (apparaît seulement après bonne réponse)
if st.session_state.answered:
    if st.button("Mot Suivant ➡️", type="primary"):
        next_question()
        st.rerun()

# Panneau Admin (caché)
if st.session_state.user.lower() == "admin" and st.session_state.reports:
    with st.expander("🕵️ Admin - Signalements"):
        st.write(st.session_state.reports)
