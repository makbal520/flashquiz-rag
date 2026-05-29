import streamlit as st
from core.evaluator import evaluate_answer
from core.qa import ask_document
import json

def show():
    cards = st.session_state.flashcards
    idx = st.session_state.card_index
    total = len(cards)
    card = cards[idx]
    mode = st.session_state.get("answer_mode", "Both")

    # ── Collapsible Q&A Sidebar ──────────────────────────────
    with st.sidebar:
        show_chat = st.toggle("💬 Q&A Chat", value=True)

        if show_chat:
            st.markdown("**Ask your document**")

            for msg in st.session_state.get("messages_display", []):
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            question = st.chat_input("Ask anything...")
            if question:
                st.session_state.messages_display.append(
                    {"role": "user", "content": question}
                )
                with st.spinner("Searching..."):
                    res = ask_document(
                        question,
                        st.session_state.vectorstore,
                        st.session_state.get("chat_history", [])
                    )
                st.session_state.chat_history = res["chat_history"]
                st.session_state.messages_display.append(
                    {"role": "assistant", "content": res["answer"]}
                )
                st.rerun()

            if st.session_state.get("messages_display"):
                if st.button("Clear chat"):
                    st.session_state.chat_history = []
                    st.session_state.messages_display = []
                    st.rerun()

        st.divider()
        if st.button("← Back to Upload"):
            st.session_state.page = "upload"
            st.rerun()

    # ── Main Flashcard Area ──────────────────────────────────
    st.markdown(f"**Card {idx + 1} of {total}** · Topic: `{card['topic']}`")
    st.progress((idx + 1) / total)
    st.divider()

    # Question
    st.markdown(f"### ❓ {card['q']}")
    st.divider()

    # Answer input (only if not submitted yet)
    if not card["submitted"]:
        user_answer = ""

        # Voice input
        if mode in ["🎤 Voice", "Both"]:
            st.markdown("**🎤 Voice Answer**")
            audio = st.audio_input("Record your answer")
            if audio:
                st.success("Voice recorded! Submit below to evaluate.")
                # Note: transcription requires Whisper API — use text for now
                st.info("Voice transcription coming soon. Please also type your answer below.")

        # Text input
        if mode in ["✏️ Text", "Both"]:
            st.markdown("**✏️ Text Answer**")
            user_answer = st.text_area(
                "Type your answer",
                placeholder="Write your answer here...",
                height=100,
                label_visibility="collapsed"
            )

        # Submit
        if st.button("Submit & Get AI Evaluation", type="primary", use_container_width=True):
            if not user_answer.strip():
                st.warning("Please write an answer before submitting.")
            else:
                with st.spinner("Evaluating your answer..."):
                    evaluation = evaluate_answer(
                        question=card["q"],
                        user_answer=user_answer,
                        correct_answer=card["a"],
                        vectorstore=st.session_state.vectorstore
                    )
                st.session_state.flashcards[idx]["evaluation"] = evaluation
                st.session_state.flashcards[idx]["submitted"] = True
                st.rerun()

    # Show evaluation result
    if card["submitted"] and card["evaluation"]:
        ev = card["evaluation"]
        score = ev.get("score", 0)

        # Score color
        color = "#E1F5EE" if score >= 7 else "#FAEEDA" if score >= 4 else "#FAECE7"
        text_color = "#085041" if score >= 7 else "#633806" if score >= 4 else "#712B13"

        st.markdown(
            f"""<div style="background:{color};border-radius:8px;padding:1rem;margin-bottom:1rem">
            <strong style="color:{text_color}">🤖 AI Evaluation — Score: {score}/10</strong><br>
            <span style="color:{text_color}">{ev.get('feedback','')}</span>
            </div>""",
            unsafe_allow_html=True
        )

        with st.expander("📖 Model Answer"):
            st.write(ev.get("model_answer", card["a"]))

        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if idx > 0 and st.button("← Previous"):
                st.session_state.card_index -= 1
                st.rerun()
        with col2:
            if idx < total - 1:
                if st.button("Next Card →", type="primary"):
                    st.session_state.card_index += 1
                    st.rerun()
            else:
                if st.button("See Summary 📊", type="primary"):
                    st.session_state.card_index += 1
                    st.rerun()

    # Summary screen
    # Summary screen — triggered when idx >= total
if st.session_state.card_index >= total:
    st.divider()
    st.markdown("## 📊 Session Summary")

    cards = st.session_state.flashcards
    submitted = [c for c in cards if c["evaluation"]]

    if not submitted:
        st.info("No cards were evaluated yet.")
    else:
        # Overall score
        avg = sum(c["evaluation"]["score"] for c in submitted) / len(submitted)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Score", f"{avg:.1f}/10")
        col2.metric("Cards Completed", f"{len(submitted)}/{total}")
        
        # Count by category
        good = [c for c in submitted if c["evaluation"]["score"] >= 7]
        partial = [c for c in submitted if 4 <= c["evaluation"]["score"] < 7]
        bad = [c for c in submitted if c["evaluation"]["score"] < 4]
        col3.metric("Need Review", len(bad) + len(partial))

        st.divider()

        # Category breakdown
        if good:
            st.markdown("### ✅ Mastered")
            for c in good:
                with st.expander(f"{c['topic']} — {c['q'][:60]}...  · Score: {c['evaluation']['score']}/10"):
                    st.write(f"**Feedback:** {c['evaluation']['feedback']}")
                    st.write(f"**Model Answer:** {c['evaluation']['model_answer']}")

        if partial:
            st.markdown("### 🤔 Partially Known")
            for c in partial:
                with st.expander(f"{c['topic']} — {c['q'][:60]}...  · Score: {c['evaluation']['score']}/10"):
                    st.write(f"**Feedback:** {c['evaluation']['feedback']}")
                    st.write(f"**Model Answer:** {c['evaluation']['model_answer']}")

        if bad:
            st.markdown("### 😕 Needs Review")
            for c in bad:
                with st.expander(f"{c['topic']} — {c['q'][:60]}...  · Score: {c['evaluation']['score']}/10"):
                    st.write(f"**Feedback:** {c['evaluation']['feedback']}")
                    st.write(f"**Model Answer:** {c['evaluation']['model_answer']}")

        st.divider()

        # Export as text
        if st.button("📥 Export Summary", use_container_width=True):
            summary_text = f"Flashquiz Session Summary\n{'='*40}\n"
            summary_text += f"Average Score: {avg:.1f}/10\n"
            summary_text += f"Cards: {len(submitted)}/{total}\n\n"
            for i, c in enumerate(submitted):
                summary_text += f"Card {i+1} [{c['topic']}]\n"
                summary_text += f"Q: {c['q']}\n"
                summary_text += f"Score: {c['evaluation']['score']}/10\n"
                summary_text += f"Feedback: {c['evaluation']['feedback']}\n"
                summary_text += f"Model Answer: {c['evaluation']['model_answer']}\n"
                summary_text += "-"*40 + "\n"
            
            st.download_button(
                label="Download as .txt",
                data=summary_text,
                file_name="flashquiz_summary.txt",
                mime="text/plain"
            )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Retry Wrong Cards", use_container_width=True):
            # Only keep cards that scored below 7
            retry_cards = [c for c in cards if c.get("evaluation") and c["evaluation"]["score"] < 7]
            if retry_cards:
                for c in retry_cards:
                    c["evaluation"] = None
                    c["submitted"] = False
                st.session_state.flashcards = retry_cards
                st.session_state.card_index = 0
                st.rerun()
            else:
                st.success("You mastered all cards!")
    with col2:
        if st.button("🏠 Start Over", use_container_width=True):
            st.session_state.flashcards = None
            st.session_state.card_index = 0
            st.session_state.page = "upload"
            st.rerun()