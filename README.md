# 로컬 Ollama 에이전트 실습

CLI와 Streamlit 웹 UI가 공통 에이전트 루프와 도구를 사용하는 구조입니다. UI는 Orbit이라는 이름의 로컬 AI 작업공간으로 구성되어 있습니다.

- CLI에서 대화가 이어짐
- 대화 이력을 SQLite 세션 DB에 저장
- 모델이 필요할 때 `calculate` 도구를 선택하고 호출
- 최신 Steam 한국 스토어 판매 인기 1위를 `recent_game_winner` 도구로 조회
- API 오류와 도구 오류를 대화 가능한 메시지로 처리

## 구조

| 파일 | 역할 |
|---|---|
| `agent.py` | CLI 진입점 |
| `core.py` | Ollama 호출과 도구 실행 루프 |
| `tools.py` | `calculate`, `recent_game_winner` 도구 선언·구현 |
| `db.py` | SQLite 세션·메시지 저장 |
| `app.py` | Streamlit 웹 UI |
| `chatbot.py` | 기존 실행 명령 호환용 래퍼 |

## 실행

```bash
# Ollama 설치 후 한 번 실행
brew install ollama
ollama serve

# 별도 터미널에서 모델 다운로드
ollama pull llama3.2

cd /Users/lukas.lee/agent-practice
python3 agent.py
```

모델은 기본적으로 로컬 `llama3.2`를 사용합니다. 다른 모델을 쓸 경우:

```bash
export OLLAMA_MODEL="qwen2.5:7b"
```

종료는 `/exit`, 새 대화는 `/reset`입니다.

### 웹 UI 실행

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

브라우저에서 `http://localhost:8501`을 열면 Orbit UI를 사용할 수 있습니다. 화면에는 대화 세션 목록, 현재 로컬 모델 상태, 도구 실행 상태가 표시됩니다. Ollama가 이미 실행 중이면 `ollama serve`를 다시 실행하지 않습니다.

UI에서 지원하는 예시:

- `오늘 할 일을 우선순위별로 정리해줘.`
- `125 * 48을 계산해줘.`
- `최근 게임 1위가 뭔지 알려줘.`

## 테스트 예시

```text
You: 안녕. 오늘 할 일을 정리하는 걸 도와줘.
You: 125 * 48을 계산하고, 결과를 한 문장으로 설명해줘.
You: 최근 게임 1등이 뭔지 알려줘.
You: 방금 계산 결과를 기억해둬.
```

모델이 도구를 선택하면 `core.py`가 실제 도구를 실행한 뒤 결과를 다시 모델에 전달합니다.

## 팀 데모

Ollama 앱이 실행 중인지 확인한 뒤 다음 명령을 실행합니다. 앱이 이미 서버를 실행 중이면 `ollama serve`를 다시 실행하지 않습니다.

```bash
./demo.sh
```

문제가 생기면 먼저 로컬 환경을 점검합니다.

```bash
./check_local.sh
```

현재 상태와 남은 개선 과제는 [RETROSPECTIVE.md](RETROSPECTIVE.md)에 기록되어 있습니다.
