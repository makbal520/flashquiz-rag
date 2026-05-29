import streamlit as st
import os
from core.loader import load_and_split
from core.vectorstore import get_vectorstore
from core.keywords import extract_keywords
from core.flashcard import generate_flashcard

def show():
    st.markdown("## 📚 Flashquiz ")
    st.markdown("Upload your study material and generate smart flashcards.")
    st.divider()

    # Step 1: Upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        temp_path = f"./doc/{uploaded_file.name}"
        os.makedirs("./doc", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process PDF only once
        if st.session_state.get("current_file") != uploaded_file.name:
            with st.status("Processing document...", expanded=True) as status:
                st.write("Loading PDF...")
                chunks = load_and_split(temp_path)
                st.write(f"✅ Loaded — {len(chunks)} chunks created")

                st.write("Building vector store...")
                st.session_state.vectorstore = get_vectorstore(chunks)  # set FIRST
                st.write("✅ Vector store ready")

                st.write("Extracting keywords...")
                # Only call after vectorstore is confirmed set
                if st.session_state.vectorstore is not None:
                    st.session_state.keywords = extract_keywords(st.session_state.vectorstore)
                    st.write(f"✅ Found {len(st.session_state.keywords)} topics")

                st.session_state.current_file = uploaded_file.name
                st.session_state.flashcards = None
                st.session_state.card_index = 0
                st.session_state.chat_history = []
                st.session_state.messages_display = []
                status.update(label="Document ready!", state="complete")
                
        # Step 2: Keyword selection
        if "keywords" in st.session_state:
            st.divider()
            st.markdown("### Select Topics to Study")

            selected = st.multiselect(
                "Choose one or more topics (auto-extracted from your document)",
                options=st.session_state.keywords,
                default=st.session_state.keywords[:2]
            )

            col1, col2 = st.columns(2)
            with col1:
                num_cards = st.selectbox("Cards per topic", [1, 2, 3], index=0)
            with col2:
                answer_mode = st.radio(
                    "Answer mode",
                    ["🎤 Voice", "✏️ Text", "Both"],
                    horizontal=True
                )
                st.session_state.answer_mode = answer_mode

            st.divider()

            if st.button("Generate Flashcards →", type="primary", use_container_width=True):
                if not selected:
                    st.warning("Please select at least one topic.")
                    return

                with st.spinner("Generating flashcards..."):
                    all_cards = []
                    for topic in selected:
                        result = generate_flashcard(
                            topic,
                            st.session_state.vectorstore,
                            num_questions=num_cards
                        )
                        for block in result.strip().split("\n\n"):
                            lines = block.strip().split("\n")
                            q = next((l.replace("Q:", "").strip() for l in lines if l.startswith("Q:")), "")
                            a = next((l.replace("A:", "").strip() for l in lines if l.startswith("A:")), "")
                            if q and a:
                                all_cards.append({
                                    "topic": topic,
                                    "q": q,
                                    "a": a,
                                    "evaluation": None,
                                    "submitted": False
                                })

                st.session_state.flashcards = all_cards
                st.session_state.card_index = 0
                st.session_state.page = "study"
                st.rerun()