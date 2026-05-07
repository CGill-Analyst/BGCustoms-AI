import streamlit as st
from streamlit_chat import message
import anthropic
import os
from dotenv import load_dotenv

# 1. AUTHENTICATION
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")

if not api_key:
    st.error("⚠️ API Key Missing: Please check your Streamlit Secrets.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# 2. BRANDING & STYLE (Cyan & Black Theme)
st.set_page_config(page_title="BG Customs Portal", page_icon="👟")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    h1 {{ color: #00FFFF; font-family: 'Helvetica', sans-serif; font-weight: 800; text-transform: uppercase; }}
    .stMarkdown p {{ color: #FFFFFF; }}
    hr {{ border: 0; height: 1px; background: #00FFFF; opacity: 0.3; }}
    </style>
    """, unsafe_allow_html=True)

# 3. LOGO HEADER
col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("data/logo.png", width=120) 
    except:
        st.write("👟") 
with col2:
    st.title("BG CUSTOMS")
    st.write("### Handcrafted Signature Drops")

st.markdown("---")

# 4. KNOWLEDGE BASE
try:
    with open("data/bg_data.txt", "r", encoding="utf-8") as f:
        bg_context = f.read()
except FileNotFoundError:
    st.error("⚠️ Workshop Data missing.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. AI ENGINE (REVERTED TO STABLE VERSION)
def ask_bg_bot(user_question):
    system_prompt = f"You are a lead designer at BG Customs. Knowledge: {bg_context}"
    
    formatted_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    
    # REVERTED TO THIS SPECIFIC VERSION
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022", 
        max_tokens=600,
        system=system_prompt,
        messages=formatted_history + [{"role": "user", "content": user_question}]
    )
    return response.content[0].text

# 6. THE CHAT
for msg in st.session_state.messages:
    is_bot = msg["role"] == "assistant"
    message(
        msg["content"], 
        is_user=not is_bot, 
        logo="https://cdn-icons-png.flaticon.com/512/2589/2589902.png" if is_bot else None
    )

if prompt := st.chat_input("Ask about Oasis, Nirvana, or Liam Gallagher drops..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    message(prompt, is_user=True)
    
    with st.spinner("Checking the workshop..."):
        try:
            answer = ask_bg_bot(prompt)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            message(answer, logo="https://cdn-icons-png.flaticon.com/512/2589/2589902.png")
        except Exception as e:
            st.error(f"Error: {e}")
