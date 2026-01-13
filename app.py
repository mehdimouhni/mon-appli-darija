import streamlit as st
import random
from gtts import gTTS
import io

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Darija Master Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Amiri:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .arabe-text { font-family: 'Amiri', serif; font-size: 3.5rem; color: #065F46; direction: rtl; line-height: 1.2; }
    .flashcard {
        background-color: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #10B981; margin-bottom: 20px;
    }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    .btn-darija { background-color: #f0fff4 !important; border: 1px solid #c6f6d5 !important; }
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
    try:
        tts = gTTS(text=text_ar, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        # On remet le curseur au début du fichier mémoire
        fp.seek(0)
        # On affiche le lecteur SANS autoplay pour éviter le blocage mobile
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.error("L'audio n'a pas pu être chargé. Réessayez.")

def next_question():
    theme = st.session_state.current_theme
    pool = RAW_DATA[theme]
    st.session_state.current_word = random.choice(pool)
    st.session_state.mode = random.choice(["D->F", "F->D"])
    
    # Correction du bug : On mélange les indices au lieu des objets
    correct_idx = pool.index(st.session_state.current_word)
    other_indices = [i for i in range(len(pool)) if i != correct_idx]
    random.shuffle(other_indices)
    
    selected_indices = [correct_idx] + other_indices[:3]
    random.shuffle(selected_indices)
    
    st.session_state.options = [pool[i] for i in selected_indices]
    st.session_state.answered = False

# --- LOGIN ---
if st.session_state.user is None:
    st.title("🇲🇦 Darija Master")
    name = st.text_input("Pseudo pour ta session :")
    if st.button("Lancer l'apprentissage"):
        if name: st.session_state.user = name; st.rerun()
    st.stop()

# --- SIDEBAR & PROGRESSION ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.divider()
    st.subheader("📊 Ta Progression")
    for t in RAW_DATA:
        total = len(RAW_DATA[t])
        # Un mot est considéré en cours si mastery > 0
        points = sum(st.session_state.mastery[m['d']] for m in RAW_DATA[t])
        max_points = total * 5
        st.write(f"**{t}**")
        st.progress(min(points / max_points, 1.0) if max_points > 0 else 0)

# --- ZONE DE JEU ---
if 'current_word' not in st.session_state:
    st.session_state.current_theme = "✨ Essentiels"
    next_question()

theme_choice = st.selectbox("🎯 Choisir un thème :", list(RAW_DATA.keys()))
if theme_choice != st.session_state.current_theme:
    st.session_state.current_theme = theme_choice
    next_question()
    st.rerun()

word = st.session_state.current_word
st.markdown(f"""<div class="flashcard">
    <div style="color:#6B7280; margin-bottom:10px">{"Comment dit-on en Français ?" if st.session_state.mode == "D->F" else "Comment dit-on en Darija ?"}</div>
    <div class="arabe-text">{word['a'] if st.session_state.mode == "D->F" else ""}</div>
    <div style="font-size:2.5rem; font-weight:600">{word['d'] if st.session_state.mode == "D->F" else word['f']}</div>
</div>""", unsafe_allow_html=True)

# BOUTON AUDIO PRINCIPAL (Si Darija est affiché)
if st.session_state.mode == "D->F":
    if st.button("🔈 Écouter la question"):
        play_audio(word['a'])

# RÉPONSES
st.write("---")
cols = st.columns(2)
for i, opt in enumerate(st.session_state.options):
    with cols[i % 2]:
        # Texte du bouton
        btn_label = opt['f'] if st.session_state.mode == "D->F" else f"{opt['d']} / {opt['a']}"
        
        # Ligne de réponse
        if st.button(btn_label, key=f"ans_{i}", use_container_width=True):
            if opt['d'] == word['d']:
                if not st.session_state.answered:
                    st.success("🎯 Bravo !")
                    st.session_state.mastery[word['d']] = min(st.session_state.mastery[word['d']] + 1, 5)
                    st.session_state.answered = True
                    st.balloons()
            else:
                st.error(f"Faux ! La réponse était : {word['f'] if st.session_state.mode == 'D->F' else word['d']}")
                st.session_state.answered = True

        # Audio SOUS les propositions (uniquement si les propositions sont en Darija)
        if st.session_state.mode == "F->D":
            if st.button(f"🔈 Écouter l'option {i+1}", key=f"vol_{i}"):
                play_audio(opt['a'])

if st.session_state.answered:
    if st.button("Question Suivante ➡️", type="primary", use_container_width=True):
        next_question()
        st.rerun()

# --- DICTIONNAIRE ---
st.divider()
with st.expander(f"📚 Dictionnaire complet : {st.session_state.current_theme}"):
    for item in RAW_DATA[st.session_state.current_theme]:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{item['f']}** : {item['d']} ({item['a']})")
        if c2.button("🔈", key=f"dic_{item['d']}"):
            play_audio(item['a'])
