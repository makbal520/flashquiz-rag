import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Flashquiz", layout="wide")

# Initialize ALL session state variables here
defaults = {
    "page": "upload",
    "vectorstore": None,
    "keywords": None,
    "current_file": None,
    "flashcards": None,
    "card_index": 0,
    "chat_history": [],
    "messages_display": [],
    "answer_mode": "Both"
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Route to correct page
if st.session_state.page == "upload":
    from ui.page1_upload import show
    show()
elif st.session_state.page == "study":
    from ui.page2_study import show
    show()