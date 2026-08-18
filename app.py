"""Optional Streamlit web UI sharing the same core agent loop."""
import streamlit as st
import db
from core import MODEL, step

st.set_page_config(page_title="나만의 에이전트", page_icon="🤖")
sessions = db.list_sessions()
if "session_id" not in st.session_state:
    st.session_state.session_id = sessions[0]["id"] if sessions else db.create_session()

with st.sidebar:
    st.header("대화 목록")
    if st.button("+ 새 대화", use_container_width=True):
        st.session_state.session_id = db.create_session()
        st.rerun()
    for session in db.list_sessions():
        if st.button(session["title"] or "(빈 대화)", key=session["id"], use_container_width=True):
            st.session_state.session_id = session["id"]
            st.rerun()

st.title("🤖 나만의 에이전트")
st.caption(f"모델: {MODEL}")
session_id = st.session_state.session_id
messages = db.load_messages(session_id)
for message in messages:
    if message.get("role") in ("system", "tool"):
        continue
    st.chat_message(message.get("role", "assistant")).markdown(message.get("content", ""))

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)
    with st.chat_message("assistant"):
        final_text = ""
        for event in step(messages):
            if event[0] == "tool_call":
                st.caption(f"도구: {event[1]} → {event[3]}")
            elif event[0] == "final":
                final_text = event[1]
            else:
                st.error(event[1])
        if final_text:
            st.markdown(final_text)
    db.replace_messages(session_id, messages)
    if len(messages) <= 3:
        db.update_title(session_id, user_input[:30])
    st.rerun()
