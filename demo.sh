#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
./check_local.sh

echo ""
echo "== 팀 데모 시작 =="
printf '%s\n' \
  '안녕. 오늘 할 일을 우선순위별로 세 가지 정리해줘.' \
  '125 * 48을 계산하고 결과를 한 문장으로 설명해줘.' \
  '방금 계산 결과를 기억하고 있다고 가정하고, 핵심만 요약해줘.' \
  '/exit' | python3 agent.py
