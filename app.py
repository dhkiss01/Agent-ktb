"""Polished Streamlit UI for the local Ollama agent."""

import streamlit as st

import db
from core import MODEL, step


st.set_page_config(
    page_title="Orbit · 나만의 에이전트",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root { --ink: #172033; --muted: #7c879d; --line: #e9edf4; --blue: #5b5ce2; --soft: #f6f7fb; }
    .stApp { background: #fbfcfe; color: var(--ink); font-family: 'Manrope', sans-serif; }
    [data-testid="stSidebar"] { background: #f2f4fa; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding: 2rem 1.1rem; }
    [data-testid="stSidebar"] .stButton button { border: 0; background: transparent; color: #606c83; text-align: left; padding: .7rem .8rem; border-radius: 12px; }
    [data-testid="stSidebar"] .stButton button:hover { background: #e6e9f6; color: var(--ink); }
    .brand { display: flex; align-items: center; gap: .7rem; margin-bottom: 2.5rem; }
    .brand-mark { width: 36px; height: 36px; display: grid; place-items: center; border-radius: 12px; color: white; background: linear-gradient(135deg, #7072f5, #4547bc); box-shadow: 0 8px 18px #6064d633; font-size: 1.2rem; }
    .brand-name { font-size: 1.12rem; font-weight: 800; letter-spacing: -.04em; }
    .brand-sub { color: var(--muted); font-size: .72rem; margin-top: .12rem; }
    .section-label { color: #9aa3b5; font-size: .68rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin: 1.2rem .5rem .55rem; }
    .hero { padding: 2.3rem 0 1.3rem; }
    .eyebrow { color: var(--blue); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .12em; text-transform: uppercase; }
    .hero h1 { color: var(--ink); font-size: clamp(2rem, 4vw, 3.25rem); letter-spacing: -.07em; line-height: 1.05; margin: .55rem 0 .7rem; }
    .hero p { color: var(--muted); font-size: .98rem; margin: 0; }
    .model-pill { display: inline-flex; align-items: center; gap: .45rem; padding: .52rem .78rem; background: white; border: 1px solid var(--line); border-radius: 999px; color: #68748b; font: 500 .72rem 'DM Mono', monospace; }
    .online-dot { width: 7px; height: 7px; border-radius: 50%; background: #45c98a; box-shadow: 0 0 0 4px #45c98a22; }
    .empty { border: 1px dashed #d9deea; border-radius: 20px; background: white; padding: 2.4rem; text-align: center; margin: 1.5rem 0; }
    .empty-icon { font-size: 2.2rem; margin-bottom: .7rem; }
    .empty h3 { margin: 0 0 .4rem; font-size: 1.05rem; }
    .empty p { color: var(--muted); margin: 0; font-size: .9rem; }
    [data-testid="stChatMessage"] { border: 0; padding: 1rem 0; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { line-height: 1.75; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { background: transparent; }
    [data-testid="stChatInput"] { padding-bottom: 1.4rem; }
    [data-testid="stChatInput"] > div { border: 1px solid #dfe4ef; border-radius: 16px; box-shadow: 0 10px 30px #2d3c6810; }
    .hint { color: #a0a9bb; font-size: .75rem; text-align: center; margin-top: .65rem; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_or_create_session() -> str:
    sessions = db.list_sessions()
    if "session_id" not in st.session_state:
        st.session_state.session_id = sessions[0]["id"] if sessions else db.create_session()
    return st.session_state.session_id


session_id = get_or_create_session()

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">✦</div><div><div class="brand-name">Orbit</div><div class="brand-sub">LOCAL AI WORKSPACE</div></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("＋  새 대화 시작", use_container_width=True):
        st.session_state.session_id = db.create_session()
        st.rerun()

    st.markdown('<div class="section-label">Conversations</div>', unsafe_allow_html=True)
    for session in db.list_sessions():
        title = session["title"] or "새 대화"
        marker = "●  " if session["id"] == st.session_state.session_id else ""
        if st.button(marker + title[:24], key=session["id"], use_container_width=True):
            st.session_state.session_id = session["id"]
            st.rerun()

    st.markdown('<div class="section-label">Agent status</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="model-pill"><span class="online-dot"></span>{MODEL} · LOCAL</div>',
        unsafe_allow_html=True,
    )


st.markdown(
    f'<div class="hero"><div class="eyebrow">PERSONAL ASSISTANT / 01</div><h1>무엇을 함께<br>정리해볼까요?</h1><p>생각을 정리하고, 필요한 일을 도구로 처리해드릴게요.</p></div>',
    unsafe_allow_html=True,
)

messages = db.load_messages(session_id)
visible_messages = [m for m in messages if m.get("role") in ("user", "assistant") and m.get("content")]
if not visible_messages:
    st.markdown(
        '<div class="empty"><div class="empty-icon">✧</div><h3>새로운 대화를 시작해보세요</h3><p>할 일 정리, 계산, 최신 게임 순위 조회를 요청할 수 있어요.</p></div>',
        unsafe_allow_html=True,
    )

for message in visible_messages:
    avatar = "🧑" if message.get("role") == "user" else "✦"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

user_input = st.chat_input("메시지를 입력하세요 · 예: 최근 게임 1위가 뭐야?")
if user_input:
    messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar="✦"):
        final_text = ""
        with st.status("에이전트가 생각하고 있어요…", expanded=True) as status:
            for event in step(messages):
                if event[0] == "tool_call":
                    st.write(f"`{event[1]}` 도구를 실행했습니다.")
                elif event[0] == "final":
                    final_text = event[1]
                else:
                    status.update(label="처리 중 오류가 발생했습니다", state="error")
                    st.error(event[1])
            if final_text:
                status.update(label="완료", state="complete", expanded=False)
        if final_text:
            st.markdown(final_text)
    db.replace_messages(session_id, messages)
    if len(messages) <= 3:
        db.update_title(session_id, user_input[:30])
    st.rerun()

st.markdown('<div class="hint">Orbit runs locally with Ollama · 대화는 이 컴퓨터의 SQLite에 저장됩니다</div>', unsafe_allow_html=True)
