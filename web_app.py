import streamlit as st
from streamlit_chat import message
import anthropic
import os
from dotenv import load_dotenv

# 1. AUTHENTICATION SETUP
load_dotenv()  # Looks for your .env file on your laptop

# This line handles both local testing (.env) and the live website (Streamlit Secrets)
api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")

if not api_key:
    st.error("⚠️ API Key Missing: Please ensure your .env file is set up correctly.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# 2. KNOWLEDGE BASE SETUP
try:
    with open("data/bg_data.txt", "r", encoding="utf-8") as f:
        bg_context = f.read()
except FileNotFoundError:
    st.error("⚠️ Data file not found! Ensure 'data/bg_data.txt' exists.")
    st.stop()

# 3. PAGE BRANDING
st.set_page_config(page_title="BG Customs Assistant", page_icon="👟")
st.title("👟 BG Customs Team Portal")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# 4. AI EMPLOYEE LOGIC
def ask_bg_bot(user_question):
    system_prompt = f"""
    IDENTITY:
    You are a core team member at BG Customs in Hull. Always use "we", "us", and "our". 
    Your tone is expert, friendly, and exclusive.

    KNOWLEDGE BASE (ONLY OFFER THESE):
    {bg_context}

    STRICT SALES RULES:
    1. ONLY sell/discuss the specific signature designs found in the data (Oasis, Nirvana, Liam Gallagher, etc.).
    2. If a customer asks for a "custom" design not listed, say: 
       "We are strictly focusing on our signature limited-edition drops right now and aren't taking random custom requests."
    3. Before giving a product link, ALWAYS ask: "Which of our signature designs were you looking at, and do you have a specific size in mind?"
    4. Mention: £60 deposit required to secure the order.
    5. Mention: 4-6 week lead time for handcrafted completion.

    AUTHENTICITY:
    - All shoes are 100% genuine Adidas purchased at full retail.
    """

    # Format the history for the Claude API
    formatted_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # FIXED MODEL NAME: Updated to 'latest' to avoid the 404 error
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=600,
        system=system_prompt,
        messages=formatted_history + [{"role": "user", "content": user_question}]
    )
    return response.content[0].text


# 5. THE CHAT UI
# Display existing messages
for msg in st.session_state.messages:
    message(msg["content"], is_user=(msg["role"] == "user"))

# Chat input box
if prompt := st.chat_input("Ask about our latest drops..."):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    message(prompt, is_user=True)

    # Generate and display AI response
    with st.spinner("Consulting the team..."):
        try:
            answer = ask_bg_bot(prompt)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            message(answer)
        except Exception as e:
            st.error(f"Something went wrong: {e}")