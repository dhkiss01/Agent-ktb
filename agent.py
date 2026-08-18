"""CLI entry point."""
import db
from core import MODEL, SYSTEM_PROMPT, step

def main() -> None:
    sessions = db.list_sessions()
    session_id = sessions[0]["id"] if sessions else db.create_session()
    messages = db.load_messages(session_id) or [{"role": "system", "content": SYSTEM_PROMPT}]
    db.replace_messages(session_id, messages)
    print(f"로컬 챗봇 ({MODEL}) — /exit 종료, /reset 새 대화")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다."); break
        if not text: continue
        if text == "/exit": break
        if text == "/reset":
            session_id = db.create_session()
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            db.replace_messages(session_id, messages)
            print("Bot: 새 대화를 시작했습니다."); continue
        messages.append({"role": "user", "content": text})
        failed = False
        for event in step(messages):
            if event[0] == "tool_call": print(f"  [도구 호출] {event[1]}({event[2]}) → {event[3]}")
            elif event[0] == "final": print(f"Bot: {event[1]}")
            else: failed = True; print(f"Bot: 요청을 처리하지 못했습니다. 원인: {event[1]}")
        if not failed:
            db.replace_messages(session_id, messages)
            if len(messages) <= 3: db.update_title(session_id, text[:30])

if __name__ == "__main__":
    main()
