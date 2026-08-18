#!/usr/bin/env bash
set -u

echo "== Ollama 설치 =="
if ! command -v ollama >/dev/null 2>&1; then
  echo "실패: Ollama가 설치되어 있지 않습니다."
  exit 1
fi
ollama --version

echo "== Ollama 서버 =="
if curl -fsS --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo '정상: 서버가 실행 중입니다. `ollama serve`를 다시 실행하지 마세요.'
else
  echo "실패: 서버에 연결할 수 없습니다."
  echo "Ollama 앱을 실행하거나, 별도 터미널에서 `ollama serve`를 실행하세요."
  exit 1
fi

echo "== 모델 =="
if ollama list | awk 'NR > 1 {found=1} END {exit !found}'; then
  ollama list
else
  echo "실패: 다운로드된 모델이 없습니다."
  echo "실행: ollama pull llama3.2"
  exit 1
fi

echo "== 챗봇 코드 =="
python3 -m py_compile chatbot.py
echo "정상: chatbot.py 문법 검사 통과"
echo ""
echo "실행: python3 chatbot.py"
