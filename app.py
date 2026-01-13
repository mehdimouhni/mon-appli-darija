import streamlit as st
import random
from gtts import gTTS
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Darija Master Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .flashcard {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #10B981; margin-bottom: 20px;
    }
    .big-text { font-size: 2.5rem; font-weight: 600; color: #1F2937; margin: 10px 0; }
    .sub-text { color: #6B7280; font-size: 1.1rem; }
    .stButton>button {
        border-radius: 10px; height: 3.5em; font-weight: bold;
        border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover { border-color: #10B981; color: #10B981; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DONNÉES COMPLÈTE (12 Thèmes) ---
RAW_DATA = {
    "✨ Essentiels": [
        {"d": "Iyyeh", "f": "Oui"}, {"d": "Lla", "f": "Non"}, {"d": "Afak", "f": "S'il te plaît"},
        {"d": "Shokran", "f": "Merci"}, {"d": "Wakha", "f": "D'accord"}, {"d": "Safi", "f": "C'est bon / Ok"},
        {"d": "Mashi moshkil", "f": "Pas de problème"}, {"d": "Daba", "f": "Maintenant"}
    ],
    "🤝 Présentation": [
        {"d": "Smiyati...", "f": "Je m'appelle..."}, {"d": "Mnin nta?", "f": "D'où viens-tu ?"},
        {"d": "Msherefin", "f": "Enchanté"}, {"d": "Ki dayer?", "f": "Comment vas-tu ?"},
        {"d": "Labass", "f": "Ça va bien"}
    ],
    "🔢 Chiffres": [
        {"d": "Wahed", "f": "Un"}, {"d": "Jouj", "f": "Deux"}, {"d": "Tlata", "f": "Trois"},
        {"d": "Arba'a", "f": "Quatre"}, {"d": "Khamsa", "f": "Cinq"},
        {"d": "Sitta", "f": "Six"}, {"d": "Seb'a", "f": "Sept"}, {"d": "Tmania", "f": "Huit"},
        {"d": "Tes'a", "f": "Neuf"}, {"d": "Ashra", "f": "Dix"}
    ],
    "🏃 Verbes de Base": [
        {"d": "Mshi", "f": "Aller"}, {"d": "Koul", "f": "Manger"}, {"d": "Shrab", "f": "Boire"},
        {"d": "Dir", "f": "Faire"}, {"d": "N'ass", "f": "Dormir"}, {"d": "Shouf", "f": "Regarder"},
        {"d": "Hdar", "f": "Parler"}, {"d": "Fham", "f": "Comprendre"}
    ],
    "🗣️ Mes Premières Phrases": [
        {"d": "Bghit n'mshi l...", "f": "Je veux aller à..."}, {"d": "Fiyya l'jou'e", "f": "J'ai faim"},
        {"d": "Twahashtek", "f": "Tu me manques"}, {"d": "Ma fhemtsh", "f": "Je n'ai pas compris"},
        {"d": "Fin ghadin?", "f": "Où allons-nous ?"}
    ],
    "🥙 Nourriture & Café": [
        {"d": "L'fatura afak", "f": "L'addition svp"}, {"d": "Ma fihsh l'har", "f": "Ce n'est pas pimenté"},
        {"d": "Atay b'na'na", "f": "Thé à la menthe"}, {"d": "Qahwa k'hla", "f": "Café noir"},
        {"d": "L'makla bnina", "f": "La nourriture est bonne"}
    ],
    "🚕 Transport": [
        {"d": "Fin kayn taxi?", "f": "Où est le taxi ?"}, {"d": "Sir direct", "f": "Allez tout droit"},
        {"d": "Dor l'limen", "f": "Tourne à droite"}, {"d": "Dor l'lisser", "f": "Tourne à gauche"},
        {"d": "Hna afak", "f": "Arrêtez-vous ici"}
    ],
    "🏠 La Famille": [
        {"d": "Baba", "f": "Papa"}, {"d": "Mama", "f": "Maman"}, {"d": "Khouya", "f": "Mon frère"},
        {"d": "Khti", "f": "Ma sœur"}, {"d": "Wldi", "f": "Mon fils"}, {"d": "Bnti", "f": "Ma fille"}
    ],
    "👕 Shopping": [
        {"d": "Chhal hada?", "f": "Combien ça coûte ?"}, {"d": "Ghalia bzaf", "f": "C'est trop cher"},
        {"d": "Naqess shwiya", "f": "Baisse un peu le prix"}, {"d": "Akher taman", "f": "Dernier prix"}
    ],
    "⏰ Le Temps": [
        {"d": "L'youm", "f": "Aujourd'hui"}, {"d": "Ghedda", "f": "Demain"}, {"d": "L'barah", "f": "Hier"},
        {"d": "Daba", "f": "Maintenant"}, {"d": "Men be'ad", "f": "Plus tard"}
    ],
    "🚑 Santé": [
        {"d": "Ateqni", "f": "Aidez-moi"}, {"d": "Tbib", "f": "Docteur"},
        {"d": "Rassi kay dreni", "f": "J'ai mal à la tête"}, {"d": "Formasyan", "f": "Pharmacie"}
    ],
    "🌦️ Météo": [
        {"d": "Skhun", "f": "Chaud"}, {"d": "Bard", "f": "Froid"},
        {"d": "Shta", "f": "La pluie"}, {"d": "Shmesh", "f": "Le soleil"}
    ]
}

# --- 3. SESSION & LOGIQUE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'mastery' not in st.session_state: 
    st.session_state.mastery = {m['d']: 0 for t in RAW_DATA for m in RAW_DATA[t]}
if 'reports' not in st.session_state: st.session_state.reports = []

# Fonction de sélection de question
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

# --- 4. LOGIN ---
if st.session_state.user is None:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🇲🇦 Darija Master")
        st.info("Entre un pseudo pour suivre ta progression (Note: La sauvegarde s'efface si tu fermes l'onglet pour l'instant).")
        name = st.text_input("Pseudo :")
        if st.button("Commencer", type="primary"):
            if name:
                st.session_state.user = name
                st.rerun()
    st.stop()

# --- 5. INTERFACE PRINCIPALE ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.write("---")
    st.subheader("📊 Progression")
    st.caption("Il faut 5 bonnes réponses pour maîtriser un mot.")
    
    for t in RAW_DATA:
        # Calcul du pourcentage
        total_words = len(RAW_DATA[t])
        mastered_words = sum(1 for m in RAW_DATA[t] if st.session_state.mastery[m['d']] >= 5)
        # Affichage
        if mastered_words > 0:
            st.write(f"**{t}** ({mastered_words}/{total_words})")
            st.progress(mastered_words / total_words)
        else:
            st.write(f"{t}")

    if st.button("Déconnexion"):
        st.session_state.user = None
        st.rerun()

# Initialisation
if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

# Sélecteur de thème
theme_choice = st.selectbox("🎯 Changer de thème :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

# CARTE DE QUESTION
q_text = st.session_state.current_word['d'] if st.session_state.mode == "D->F" else st.session_state.current_word['f']
instruction = "Traduisez en Français 🇫🇷" if st.session_state.mode == "D->F" else "Traduisez en Darija 🇲🇦"

st.markdown(f"""
    <div class="flashcard">
        <div class="sub-text">{instruction}</div>
        <div class="big-text">{q_text}</div>
    </div>
""", unsafe_allow_html=True)

# AUDIO INTELLIGENT (Pas de spoiler)
# On affiche l'audio SI la question est en Darija (pour aider à lire)
# OU SI l'utilisateur a déjà répondu (pour entendre la correction)
col_a, col_b = st.columns([1, 1])
with col_a:
    show_audio = (st.session_state.mode == "D->F") or st.session_state.answered
    if show_audio:
        if st.button("🔈 Écouter prononciation"):
            tts = gTTS(text=st.session_state.current_word['d'], lang='ar')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format='audio/mp3', autoplay=True)
    else:
        st.write("🔇 Audio masqué (devine d'abord !)")

with col_b:
    if st.button("⚠️ Signaler erreur"):
        st.toast("Signalement envoyé à l'admin.", icon="✅")

# CHOIX DE RÉPONSE
st.write("---")
cols = st.columns(2)
correct_ans = st.session_state.current_word['f'] if st.session_state.mode == "D->F" else st.session_state.current_word['d']

for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        # Si on clique sur une réponse...
        if st.button(opt, key=f"btn_{i}", use_container_width=True):
            if opt == correct_ans:
                if not st.session_state.answered:
                    st.balloons()
                    st.success(f"Bravo ! Score maîtrise : {st.session_state.mastery[st.session_state.current_word['d']] + 1}/5")
                    st.session_state.mastery[st.session_state.current_word['d']] += 1
                    st.session_state.answered = True
            else:
                st.error(f"Faux ! La bonne réponse était : {correct_ans}")
                st.session_state.answered = True # On arrête le tour pour qu'il voie la correction

# BOUTON SUIVANT (Apparaît après réponse)
if st.session_state.answered:
    if st.button("Question Suivante ➡️", type="primary"):
        next_question()
        st.rerun()

# DICTIONNAIRE DU THÈME (Pour réviser)
with st.expander(f"📚 Dictionnaire : {st.session_state.current_theme}"):
    st.info("Révise les mots de ce thème ici.")
    # Affichage simple sans pandas pour éviter les erreurs
    for item in RAW_DATA[st.session_state.current_theme]:
        st.write(f"**{item['d']}** = {item['f']}")
