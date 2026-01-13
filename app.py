import streamlit as st
import random
from gtts import gTTS
import io

# --- CONFIGURATION ET DESIGN ---
st.set_page_config(page_title="Darija Master Pro 🇲🇦", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Ubuntu', sans-serif; }
    .main { background-color: #f7f9fc; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: white; color: #1E3A8A;
        border: 2px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        font-weight: bold; transition: all 0.2s;
    }
    .stButton>button:hover { border-color: #1E3A8A; color: #1E3A8A; transform: translateY(-2px); }
    .card {
        background: white; padding: 2rem; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        text-align: center; border-top: 5px solid #1E3A8A;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- BASE DE DONNÉES COMPLÈTE ---
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui"}, {"d": "Lla", "f": "Non"}, {"d": "Afak", "f": "S'il te plaît"},
        {"d": "Shokran", "f": "Merci"}, {"d": "Wakha", "f": "D'accord"}, {"d": "Mashi moshkil", "f": "Pas de problème"}, {"d": "Safi", "f": "C'est bon / Ok"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati...", "f": "Je m'appelle..."}, {"d": "Mnin nta?", "f": "D'où viens-tu ?"},
        {"d": "Msherefin", "f": "Enchanté"}, {"d": "Smili", "f": "Excuse-moi"}, {"d": "Ki dayer?", "f": "Comment vas-tu ?"}
    ],
    "🏃 Verbes de Base": [
        {"d": "Mshi", "f": "Aller"}, {"d": "Koul", "f": "Manger"}, {"d": "Shrab", "f": "Boire"},
        {"d": "Dir", "f": "Faire"}, {"d": "N'ass", "f": "Dormir"}, {"d": "Shouf", "f": "Regarder"}
    ],
    "🗣️ Mes Premières Phrases": [
        {"d": "Bghit n'mshi l...", "f": "Je veux aller à..."}, {"d": "Fiyya l'jou'e", "f": "J'ai faim"},
        {"d": "Twahashtek", "f": "Tu me manques"}, {"d": "Fin ghadin?", "f": "Où allons-nous ?"}
    ],
    "🔢 Chiffres": [
        {"d": "Wahed", "f": "Un"}, {"d": "Jouj", "f": "Deux"}, {"d": "Tlata", "f": "Trois"},
        {"d": "Arba'a", "f": "Quatre"}, {"d": "Khamsa", "f": "Cinq"}, {"d": "Ashra", "f": "Dix"}
    ],
    "🚕 Transport": [
        {"d": "Fin kayn taxi?", "f": "Où est le taxi ?"}, {"d": "Sir direct", "f": "Allez tout droit"},
        {"d": "Hna afak", "f": "Ici s'il vous plaît"}
    ],
    "👕 Shopping": [
        {"d": "Chhal hada?", "f": "Combien ça coûte ?"}, {"d": "Ghalia bzaf", "f": "C'est trop cher"},
        {"d": "Naqess shwiya", "f": "Baisse un peu"}
    ]
}

# --- INITIALISATION SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'reports' not in st.session_state: st.session_state.reports = []
if 'mastery' not in st.session_state: 
    st.session_state.mastery = {m['d']: 0 for t in RAW_DATA for m in RAW_DATA[t]}

# --- ECRAN DE CONNEXION ---
if st.session_state.user is None:
    st.title("🇲🇦 Darija Master")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Ton prénom / Pseudo")
        if st.button("Commencer l'apprentissage"):
            if name:
                st.session_state.user = name
                st.rerun()
    st.stop()

# --- LOGIQUE DE JEU ---
def next_question():
    theme = st.session_state.current_theme
    pool = RAW_DATA[theme]
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"])
    
    correct = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']
    others = [(w['f'] if st.session_state.mode == "D->F" else w['d']) for w in pool if w['d'] != st.session_state.current_word['d']]
    random.shuffle(others)
    
    opts = list(dict.fromkeys([correct] + others[:3]))
    random.shuffle(opts)
    st.session_state.options = opts
    st.session_state.answered = False

# --- INTERFACE PRINCIPALE ---
with st.sidebar:
    st.title(f"Salut, {st.session_state.user}!")
    st.header("📊 Ta Maîtrise")
    for t in RAW_DATA:
        acquis = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        st.write(f"{t} ({acquis}/{len(RAW_DATA[t])})")
        st.progress(acquis / len(RAW_DATA[t]))
    
    if st.button("Se déconnecter"):
        st.session_state.user = None
        st.rerun()

# Initialisation de la première question
if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

# Zone centrale
theme_choice = st.selectbox("🎯 Choisis ta thématique :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

st.markdown(f"""<div class="card">
    <p style="color: #6B7280; font-size: 1.2rem;">{"Traduisez vers le Français" if st.session_state.mode == "D->F" else "Traduisez vers le Darija"}</p>
    <h1 style="color: #1E3A8A; font-size: 3.5rem; margin: 10px 0;">
        {st.session_state.current_word['d'] if st.session_state.mode == "D->F" else st.session_state.current_word['f']}
    </h1>
</div>""", unsafe_allow_stdio=True)

# Boutons d'action
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🔈 Écouter l'accent"):
        tts = gTTS(text=st.session_state.current_word['d'], lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3', autoplay=True)
with c2:
    if st.button("⚠️ Signaler une erreur"):
        st.session_state.reports.append(st.session_state.current_word['d'])
        st.toast("Signalement enregistré !")

# Options de réponse
st.write("---")
cols = st.columns(2)
correct_ans = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']

for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        if st.button(opt, key=f"btn_{i}"):
            if opt == correct_ans:
                if not st.session_state.answered:
                    st.balloons()
                    st.session_state.mastery[st.session_state.current_word['d']] += 1
                    st.session_state.answered = True
                    st.success("🎯 Parfait !")
            else:
                st.error("Ce n'est pas ça...")

if st.session_state.answered:
    if st.button("Continuer ➡️", type="primary"):
        next_question()
        st.rerun()

# Section Admin cachée pour les signalements
if st.session_state.user.lower() == "admin":
    with st.expander("🛠️ Signalements d'erreurs"):
        st.write(st.session_state.reports)
