import streamlit as st
import os
import json
import asyncio
import edge_tts
import uuid
import datetime
import base64
import re
import streamlit.components.v1 as components
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader
from datetime import datetime, timedelta, timezone

# 1. Load Keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="StudyDeck", page_icon="🧠", layout="wide")

# --- EXTREME UI OVERHAUL CSS (WITH MOBILE OPTIMIZATION) ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E2E2E2; }
        h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; }
        
        .stApp {
            background-color: #0F0B14;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(138, 43, 226, 0.15) 0%, transparent 25%),
                radial-gradient(circle at 85% 80%, rgba(255, 75, 75, 0.15) 0%, transparent 25%),
                radial-gradient(circle at 80% 15%, rgba(0, 255, 128, 0.1) 0%, transparent 20%);
            background-attachment: fixed;
        }

        header, footer { visibility: hidden; }
        .block-container { padding-top: 4rem; padding-bottom: 4rem; max-width: 1000px; }

        h1 { font-size: 4rem !important; font-weight: 800 !important; color: white !important; line-height: 1.1 !important; letter-spacing: -1px; text-align: center; margin-bottom: 1rem !important; }
        h2 { font-size: 2rem !important; color: white !important; font-weight: 700 !important; text-align: center; }
        
        .stMarkdown p { font-size: 1.1rem; color: #E2E2E2; text-align: left !important; line-height: 1.6; }
        .hero-text p { text-align: center !important; color: #A0A0AB; }

        .stCard { background: #1A1622; border: 1px solid #332B40; border-radius: 24px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); transition: all 0.3s ease; }
        .stCard:hover { transform: translateY(-5px); box-shadow: 0 15px 50px rgba(255, 75, 75, 0.1); border-color: #ff4b4b; }

        .stButton > button { background: #ff4b4b !important; color: white !important; border-radius: 50px !important; padding: 12px 30px !important; font-family: 'Outfit', sans-serif !important; font-weight: 600 !important; font-size: 1.1rem !important; border: none !important; transition: all 0.2s !important; width: 100%; }
        .stButton > button:hover { background: #ff6b6b !important; transform: scale(1.02) !important; }
        
        .stButton > button[kind="secondary"] { background: transparent !important; border: 2px solid #332B40 !important; color: #A0A0AB !important; }
        .stButton > button[kind="secondary"]:hover { border-color: #ff4b4b !important; color: #ff4b4b !important; }

        .stTabs [data-baseweb="tab-list"] { gap: 30px; border-bottom: 1px solid #332B40; margin-bottom: 40px; justify-content: center; }
        .stTabs [data-baseweb="tab"] { padding-bottom: 15px; font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.1rem; color: #888; }
        .stTabs [aria-selected="true"] { color: #ff4b4b !important; border-bottom: 3px solid #ff4b4b !important; }
        
        [data-testid="stFileUploadDropzone"] { background-color: #1A1622 !important; border: 2px dashed #332B40 !important; border-radius: 24px !important; padding: 60px 20px !important; text-align: center; transition: all 0.2s; }
        [data-testid="stFileUploadDropzone"]:hover { border-color: #ff4b4b !important; background-color: rgba(255, 75, 75, 0.05) !important; }
        
        .stTextInput > div > div > input, .stTextArea > div > div > textarea { background-color: #1A1622 !important; border: 1px solid #332B40 !important; color: white !important; border-radius: 12px !important; padding: 15px !important; }
        
        table { width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #1A1622; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        th, td { padding: 15px; border-bottom: 1px solid #332B40; text-align: left; }
        th { background-color: #0F0B14; color: #ff4b4b; font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.05rem; }
        td { color: #E2E2E2; font-size: 1rem; }

        /* 🚨 MOBILE OPTIMIZATION */
        @media (max-width: 768px) {
            /* Stack columns vertically */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 15px !important;
            }
            [data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            
            /* Reduce massive typography for smaller screens */
            h1 { font-size: 2.5rem !important; }
            h2 { font-size: 1.5rem !important; }
            
            /* Reduce container padding to maximize screen real estate */
            .block-container {
                padding-top: 1.5rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            
            /* Make buttons easier to tap with thumbs */
            .stButton > button {
                padding: 15px 20px !important;
                font-size: 1.1rem !important;
            }
            
            /* Adjust cards for mobile screens */
            .stCard {
                padding: 20px !important;
                margin-bottom: 15px !important;
            }

            /* Make markdown tables scrollable horizontally on mobile */
            .stMarkdown table {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- HELPER FUNCTIONS ---
def card(content):
    st.markdown(f'<div class="stCard">{content}</div>', unsafe_allow_html=True)

def format_markdown(text):
    text = re.sub(r'([^\n])\n(\|)', r'\1\n\n\2', text)
    text = re.sub(r'(\|[^\n]+)\n([^\|\n])', r'\1\n\n\2', text)
    return text

# ==========================================
# 🚨 FIXED AUTHENTICATION & CACHING
# ==========================================
@st.cache_resource
def init_supabase():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        client.auth.sign_in_anonymously()
    except Exception as e:
        st.error(f"Ensure Anonymous Sign-Ins are enabled in Supabase. Error: {e}")
    return client

supabase = init_supabase()

if "user" not in st.session_state:
    session = supabase.auth.get_session()
    if session:
        st.session_state.user = session.user
    else:
        try:
            res = supabase.auth.sign_in_anonymously()
            st.session_state.user = res.user
        except Exception as e:
            st.error(f"Auth failed: {e}")
            st.stop()

USER_ID = st.session_state.user.id
is_guest = st.session_state.user.is_anonymous

groq_client = Groq(api_key=GROQ_API_KEY)

def get_decks():
    res = supabase.table("study_decks").select("*").eq("user_id", USER_ID).order("created_at", desc=True).execute()
    return res.data

def get_all_cards():
    decks = get_decks()
    if not decks: return []
    deck_ids = [d['id'] for d in decks]
    all_cards = []
    for d_id in deck_ids:
        res = supabase.table("study_cards").select("*").eq("deck_id", d_id).execute()
        all_cards.extend(res.data)
    return all_cards

def speak_text(text, key):
    text_to_speak = text[:3000] if len(text) > 3000 else text
    async def generate_audio_bytes():
        communicate = edge_tts.Communicate(text_to_speak, "en-US-EmmaMultilingualNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(generate_audio_bytes())
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.error(f"Could not generate audio: {e}")

def render_text_with_audio(text, key_prefix):
    text = format_markdown(text)
    
    if re.search(r'^#{1,3} ', text, flags=re.MULTILINE):
        chunks = re.split(r'(?=\n#{1,3} )', '\n' + text)
        if chunks[0].strip() == "":
            chunks = chunks[1:]
    else:
        chunks = text.split('\n\n')
        
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(chunk)
        with col2:
            st.write("") 
            if st.button("🔊", key=f"{key_prefix}_chunk_{i}", help="Listen", type="secondary"):
                clean_text = re.sub(r'[#*`|]', '', chunk)
                st.session_state[f"play_{key_prefix}_{i}"] = clean_text
        
        if st.session_state.get(f"play_{key_prefix}_{i}"):
            speak_text(st.session_state[f"play_{key_prefix}_{i}"], key=f"{key_prefix}_audio_{i}")

# ==========================================
# 🚨 SIDEBAR (Login)
# ==========================================
with st.sidebar:
    st.title("Account")
    if is_guest:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
        with tab2:
            new_email = st.text_input("Email", key="signup_email")
            new_pass = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Sign Up"):
                try:
                    res = supabase.auth.sign_up({"email": new_email, "password": new_pass})
                    st.success("Account created! Please log in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
    else:
        st.success(f"Logged in as:\n**{st.session_state.user.email}**")
        if st.button("Logout"):
            supabase.auth.sign_out()
            del st.session_state.user
            st.rerun()

# ==========================================
# 🚨 MAIN APP UI
# ==========================================
tab_options = ["🏠 Dashboard", "✨ Create Deck", "📚 Study", "🛠️ Manage"]
st.markdown("""
<style>
    div[role="radiogroup"] { justify-content: center; gap: 30px; margin-bottom: 40px; }
    div[role="radiogroup"] label { font-family: 'Outfit'; font-size: 1.1rem; font-weight: 600; color: #888; }
    div[role="radiogroup"] label[data-checked="true"] { color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)

menu = st.radio("Navigation", tab_options, horizontal=True, label_visibility="collapsed")

# ==========================================
# 🚨 DASHBOARD
# ==========================================
if menu == "🏠 Dashboard":
    st.markdown('<div class="hero-text"><h1>Other apps guess.<br>StudyDeck <span style=\'color:#ff4b4b;\'>knows.</span></h1><p>Powered by AI. Turn your notes, videos, and PDFs into custom practice materials to ace your next exam.</p></div>', unsafe_allow_html=True)
    st.write("---")
    
    if is_guest:
        st.warning("⚠️ **Guest Mode:** Your data is temporary. Open the sidebar (top left) to sign in and save permanently.")
        
    all_cards = get_all_cards()
    
    if not all_cards:
        card("<h3 style='text-align:center;'>👋 Welcome to StudyDeck</h3><p style='text-align:center;'>You don't have any study material yet. Go to the <b>✨ Create Deck</b> tab to get started.</p>")
    else:
        now_utc = datetime.now(timezone.utc)
        total_cards = len(all_cards)
        due_cards = sum(1 for c in all_cards if datetime.fromisoformat(c['next_review_date'].replace('Z', '+00:00')) <= now_utc)
        mastered_cards = sum(1 for c in all_cards if c.get('interval', 0) >= 21)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            card(f"<h3 style='text-align:center; color:#888; margin:0;'>Total Cards</h3><p style='font-size:2.5rem; font-weight:800; color:white; text-align:center; margin:0;'>{total_cards}</p>")
        with col2:
            card(f"<h3 style='text-align:center; color:#888; margin:0;'>Due Today</h3><p style='font-size:2.5rem; font-weight:800; color:#ff4b4b; text-align:center; margin:0;'>{due_cards}</p>")
        with col3:
            card(f"<h3 style='text-align:center; color:#888; margin:0;'>Mastered</h3><p style='font-size:2.5rem; font-weight:800; color:#00ff80; text-align:center; margin:0;'>{mastered_cards}</p>")

        st.markdown("<h2 style='margin-top: 40px;'>Your Decks</h2>", unsafe_allow_html=True)
        for d in get_decks():
            card(f"<b style='font-size:1.2rem; color:white;'>📁 {d['title']}</b> <span style='color:#888;'>({d['source_type']})</span>")

# ==========================================
# 🚨 CREATE DECK
# ==========================================
elif menu == "✨ Create Deck":
    st.markdown("<h2>Create New Study Materials</h2>", unsafe_allow_html=True)
    
    source_type = st.radio("Choose your source:", ["PDF Upload", "📷 Image Upload", "YouTube Video", "Paste Text"], horizontal=True, label_visibility="collapsed")
    st.write("")
    
    raw_text = ""
    base64_image = None

    if source_type == "PDF Upload":
        uploaded_file = st.file_uploader("Drag & Drop your PDF here, or click to browse", type="pdf")
        if uploaded_file is not None:
            with st.spinner("Extracting text from PDF..."):
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text: raw_text += text + "\n"
                    st.success(f"✅ Extracted {len(raw_text)} characters from PDF!")
                except Exception as e:
                    st.error(f"Could not read PDF. Error: {e}")
                    
    elif source_type == "📷 Image Upload":
        uploaded_image = st.file_uploader("Drag & Drop a photo of your notes/textbook here", type=["png", "jpg", "jpeg"])
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
            bytes_data = uploaded_image.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            st.success("✅ Image loaded and ready for AI!")

    elif source_type == "YouTube Video":
        url = st.text_input("Paste a YouTube URL here:", placeholder="https://www.youtube.com/watch?v=...")
        if url:
            with st.spinner("Extracting transcript..."):
                try:
                    if "youtu.be/" in url: video_id = url.split("youtu.be/")[1].split("?")[0]
                    elif "shorts/" in url: video_id = url.split("shorts/")[1].split("?")[0]
                    elif "v=" in url: video_id = url.split("v=")[1].split("&")[0]
                    else: video_id = url
                    
                    ytt_api = YouTubeTranscriptApi()
                    transcript = ytt_api.fetch(video_id)
                    raw_text = " ".join([snippet.text for snippet in transcript])
                    st.success(f"✅ Extracted {len(raw_text)} characters from YouTube!")
                except Exception as e:
                    st.error(f"Could not fetch YouTube video. Error: {e}")
                    
    elif source_type == "Paste Text":
        raw_text = st.text_area("Paste your notes or text here:", height=250, placeholder="Paste your class notes, an article, or any text here...")

    st.write("")
    if st.button("✨ Generate Flashcards & Study Guide", type="primary"):
        
        if source_type == "📷 Image Upload" and base64_image is None:
            st.warning("Please upload an image first!")
        elif source_type != "📷 Image Upload" and not raw_text.strip():
            st.warning("Please provide some text first!")
        else:
            with st.spinner("🧠 AI is reading, naming your deck, and creating flashcards..."):
                try:
                    prompt_text = """
                    You are an expert tutor. Read the provided material.
                    1. Create a short title.
                    2. Create a study guide summary using markdown. You MUST use '##' headers to separate sections. ALWAYS put a blank line before and after any table.
                    3. Extract flashcards.
                    Output JSON ONLY: {"deck_title": "...", "summary": "...", "flashcards": [{"front": "...", "back": "..."}]}
                    """
                    
                    if source_type == "📷 Image Upload":
                        response = groq_client.chat.completions.create(
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                    ]
                                }
                            ],
                            model="qwen/qwen3.8-27b",
                            response_format={"type": "json_object"},
                            temperature=0.3
                        )
                    else:
                        response = groq_client.chat.completions.create(
                            messages=[{"role": "user", "content": f"{prompt_text}\n\nText: {raw_text[:12000]}"}],
                            model="openai/gpt-oss-120b",
                            response_format={"type": "json_object"},
                            temperature=0.3
                        )

                    result = json.loads(response.choices[0].message.content)
                    deck_title = result.get("deck_title", f"Untitled {source_type}")
                    summary = result.get("summary", "No summary generated.")
                    flashcards = result.get("flashcards", [])
                    
                    if flashcards:
                        st.success(f"✅ Created Deck: **{deck_title}**")
                        deck_data = {"user_id": USER_ID, "title": deck_title, "source_type": source_type, "summary": summary}
                        deck_response = supabase.table("study_decks").insert(deck_data).execute()
                        deck_id = deck_response.data[0]['id']
                        
                        cards_to_insert = [{"deck_id": deck_id, "front": c.get("front"), "back": c.get("back"), "next_review_date": datetime.now(timezone.utc).isoformat()} for c in flashcards]
                        supabase.table("study_cards").insert(cards_to_insert).execute()
                        st.balloons()
                        st.success("🎉 Deck saved! Go to the '📚 Study' tab.")
                    else:
                        st.error("The AI couldn't generate flashcards from this material.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# ==========================================
# 🚨 STUDY
# ==========================================
elif menu == "📚 Study":
    decks = get_decks()
    if not decks:
        card("<h3 style='text-align:center;'>No decks found.</h3><p style='text-align:center;'>Create one in the ✨ Create Deck tab first!</p>")
    else:
        col1, col2 = st.columns([4, 1])
        with col1:
            deck_options = {f"{d['title']} ({d['source_type']})": d['id'] for d in decks}
            selected_deck_label = st.selectbox("Select a deck:", list(deck_options.keys()))
            selected_deck_id = deck_options[selected_deck_label]
        with col2:
            st.write("") 
            st.write("") 
            if st.button("🗑️", type="primary"):
                st.session_state.confirm_delete_deck = selected_deck_id
                
        if "confirm_delete_deck" in st.session_state and st.session_state.confirm_delete_deck == selected_deck_id:
            st.warning(f"⚠️ Delete **{selected_deck_label}** permanently?")
            c_yes, c_no = st.columns(2)
            if c_yes.button("Yes, delete", type="primary"):
                supabase.table("study_decks").delete().eq("id", selected_deck_id).execute()
                del st.session_state.confirm_delete_deck
                st.rerun()
            if c_no.button("Cancel"):
                del st.session_state.confirm_delete_deck
                st.rerun()

        if "confirm_delete_deck" not in st.session_state or st.session_state.confirm_delete_deck != selected_deck_id:
            deck_data = next(d for d in decks if d['id'] == selected_deck_id)
            
            if deck_data.get('summary'):
                with st.expander("📖 Read Study Guide", expanded=False):
                    render_text_with_audio(deck_data['summary'], key_prefix=f"guide_{selected_deck_id}")
                    
                with st.expander("💬 Chat with your Tutor", expanded=False):
                    strict_mode = st.toggle("📄 Strict Document Mode", value=False)
                    if strict_mode: st.info("Strict: AI answers ONLY using your document.")
                    else: st.info("Expanded: AI uses your document AND general knowledge.")
                    
                    if f"chat_history_{selected_deck_id}" not in st.session_state:
                        st.session_state[f"chat_history_{selected_deck_id}"] = []
                        
                    for i, msg in enumerate(st.session_state[f"chat_history_{selected_deck_id}"]):
                        with st.chat_message(msg["role"]):
                            st.markdown(format_markdown(msg["content"]))
                            
                            if msg["role"] == "assistant":
                                if st.button("🔊 Listen to Answer", key=f"tts_chat_{selected_deck_id}_{i}"):
                                    st.session_state[f"play_chat_{selected_deck_id}_{i}"] = msg["content"]
                                
                                if st.session_state.get(f"play_chat_{selected_deck_id}_{i}"):
                                    speak_text(st.session_state[f"play_chat_{selected_deck_id}_{i}"], key=f"chat_audio_{selected_deck_id}_{i}")
                            
                    if user_query := st.chat_input("Ask a question..."):
                        with st.chat_message("user"):
                            st.write(user_query)
                        st.session_state[f"chat_history_{selected_deck_id}"].append({"role": "user", "content": user_query})
                        
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                instruction = "Answer based STRICTLY on the document." if strict_mode else "Answer using the document and general knowledge."
                                chat_prompt = f"Document: {deck_data.get('summary')}\n\nQuestion: {user_query}\n\n{instruction}"
                                chat_res = groq_client.chat.completions.create(messages=[{"role": "user", "content": chat_prompt}], model="openai/gpt-oss-120b", temperature=0.4)
                                ai_response = chat_res.choices[0].message.content
                                
                                st.markdown(format_markdown(ai_response))
                                if st.button("🔊 Listen to Answer", key=f"tts_chat_new_{selected_deck_id}"):
                                    st.session_state[f"play_chat_new_{selected_deck_id}"] = ai_response
                                    
                                if st.session_state.get(f"play_chat_new_{selected_deck_id}"):
                                    speak_text(st.session_state[f"play_chat_new_{selected_deck_id}"], key=f"chat_audio_new_{selected_deck_id}")
                                    
                        st.session_state[f"chat_history_{selected_deck_id}"].append({"role": "assistant", "content": ai_response})
            
            st.write("---")
            st.markdown("<h2>Test Your Knowledge</h2>", unsafe_allow_html=True)
            
            cram_mode = st.toggle("⚡ Cram Mode (Ignore schedule)", value=False)
            
            if cram_mode:
                cards_res = supabase.table("study_cards").select("*").eq("deck_id", selected_deck_id).execute()
            else:
                now_utc = datetime.now(timezone.utc).isoformat()
                cards_res = supabase.table("study_cards").select("*").eq("deck_id", selected_deck_id).lte("next_review_date", now_utc).execute()
                
            due_cards = cards_res.data
            
            if not due_cards:
                card("<h3 style='text-align:center;'>🎉 All caught up!</h3><p style='text-align:center;'>No cards due right now. Use Cram Mode to study anyway.</p>")
            else:
                if "current_card_index" not in st.session_state:
                    st.session_state.current_card_index = 0
                    
                if st.session_state.current_card_index >= len(due_cards):
                    card("<h3 style='text-align:center;'>✅ Session Finished!</h3><p style='text-align:center;'>Great job reviewing your cards.</p>")
                    if st.button("Reload Session"):
                        st.session_state.current_card_index = 0
                        st.rerun()
                else:
                    card_data = due_cards[st.session_state.current_card_index]
                    
                    st.markdown(f"<p style='text-align:center; color:#888; font-weight:600; letter-spacing:2px;'>CARD {st.session_state.current_card_index + 1} OF {len(due_cards)}</p>", unsafe_allow_html=True)

                    # 🚨 MOBILE OPTIMIZED FLASHCARD
                    flip_html = f"""
                    <html>
                    <head>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&display=swap');
                        body {{ margin: 0; background-color: transparent; }}
                        .scene {{ width: 100%; height: 40vh; min-height: 250px; max-height: 400px; perspective: 1000px; }}
                        .card {{ width: 100%; height: 100%; position: relative; transition: transform 0.6s; transform-style: preserve-3d; cursor: pointer; }}
                        .card.is-flipped {{ transform: rotateY(180deg); }}
                        .card-face {{ position: absolute; width: 100%; height: 100%; backface-visibility: hidden; display: flex; align-items: center; justify-content: center; border-radius: 24px; padding: 20px; box-sizing: border-box; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }}
                        .card-front {{ background: #1A1622; border: 2px solid #332B40; color: white; }}
                        .card-back {{ background: #16121C; border: 2px solid #ff4b4b; color: white; transform: rotateY(180deg); }}
                        h2, h3 {{ font-family: 'Outfit', sans-serif; margin: 0; font-size: clamp(1.2rem, 4vw, 1.8rem); line-height: 1.4; }}
                    </style>
                    </head>
                    <body>
                        <div class="scene">
                            <div class="card" onclick="this.classList.toggle('is-flipped')">
                                <div class="card-face card-front">
                                    <h2>{card_data['front']}</h2>
                                </div>
                                <div class="card-face card-back">
                                    <h3>{card_data['back']}</h3>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    components.html(flip_html, height=360)

                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c2:
                        col_audio_front, col_audio_back = st.columns(2)
                        if col_audio_front.button("🔊 Q", type="secondary", help="Listen to question"):
                            st.session_state.play_card_audio = card_data['front']
                        if col_audio_back.button("🔊 A", type="secondary", help="Listen to answer"):
                            st.session_state.play_card_audio = card_data['back']
                            
                    if "play_card_audio" in st.session_state:
                        speak_text(st.session_state.play_card_audio, key="flash_audio")

                    st.write("")

                    if cram_mode:
                        if st.button("Next Card ➡️", type="primary"):
                            st.session_state.current_card_index += 1
                            if "play_card_audio" in st.session_state: del st.session_state.play_card_audio
                            st.rerun()
                    else:
                        col1, col2 = st.columns(2)
                        if col1.button("❌ Again (Wrong)"):
                            next_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
                            supabase.table("study_cards").update({"interval": 1, "repetitions": 0, "next_review_date": next_date}).eq("id", card_data['id']).execute()
                            st.session_state.current_card_index += 1
                            if "play_card_audio" in st.session_state: del st.session_state.play_card_audio
                            st.rerun()
                            
                        if col2.button("✅ Good (Right)"):
                            new_reps = card_data['repetitions'] + 1
                            new_interval = 1 if new_reps == 1 else (6 if new_reps == 2 else int(card_data['interval'] * card_data['ease_factor']))
                            next_date = (datetime.now(timezone.utc) + timedelta(days=new_interval)).isoformat()
                            supabase.table("study_cards").update({"interval": new_interval, "repetitions": new_reps, "next_review_date": next_date}).eq("id", card_data['id']).execute()
                            st.session_state.current_card_index += 1
                            if "play_card_audio" in st.session_state: del st.session_state.play_card_audio
                            st.rerun()

# ==========================================
# 🚨 MANAGE
# ==========================================
elif menu == "🛠️ Manage":
    st.markdown("<h2>Manage Cards</h2>", unsafe_allow_html=True)
    decks = get_decks()
    if not decks:
        card("<h3 style='text-align:center;'>No decks found.</h3>")
    else:
        deck_options = {f"{d['title']} ({d['source_type']})": d['id'] for d in decks}
        selected_deck_label = st.selectbox("Select a deck to edit:", list(deck_options.keys()))
        selected_deck_id = deck_options[selected_deck_label]
        
        cards_res = supabase.table("study_cards").select("*").eq("deck_id", selected_deck_id).execute()
        cards = cards_res.data
        
        if not cards:
            st.warning("This deck has no cards.")
        else:
            for c in cards:
                with st.expander(f"Q: {c['front'][:60]}..."):
                    with st.form(key=f"form_{c['id']}"):
                        new_front = st.text_input("Question (Front)", value=c['front'])
                        new_back = st.text_area("Answer (Back)", value=c['back'])
                        if st.form_submit_button("💾 Save Changes"):
                            supabase.table("study_cards").update({"front": new_front, "back": new_back}).eq("id", c['id']).execute()
                            st.success("Card updated!")
                            st.rerun()