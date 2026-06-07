#!/bin/bash
# 전세안심 배포 검증 체크리스트

set -e

DEPLOY_URL="${1:-http://localhost:3000}"

echo "=== 전세안심 배포 검증 ==="
echo "URL: $DEPLOY_URL"
echo ""

# 1. 공개 URL 접근
echo "1. 공개 URL 접근 확인..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOY_URL")
if [ "$HTTP_CODE" = "200" ]; then
  echo "   ✅ HTTP 200 OK"
else
  echo "   ❌ HTTP $HTTP_CODE (expected 200)"
  exit 1
fi

# 2. Health check
echo "2. Health check..."
HEALTH=$(curl -s "$DEPLOY_URL/api/health")
echo "   $HEALTH"

# 3. 분석 API 응답 시간 (P4: 5초 이내)
echo "3. 분석 API 응답 시간..."
START=$(date +%s%N)
ANALYZE_RESP=$(curl -s -X POST "$DEPLOY_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"address":"서울특별시 강남구 테헤란로 152","jibun_address":"서울특별시 강남구 역삼동 798-22","building_name":"삼성역빌딩","sigungu_code":"11680","rental_type":"jeonse","deposit":50000}')
END=$(date +%s%N)
ELAPSED_MS=$(( (END - START) / 1000000 ))
echo "   응답 시간: ${ELAPSED_MS}ms"
if [ "$ELAPSED_MS" -lt 5000 ]; then
  echo "   ✅ 5초 이내 응답"
else
  echo "   ⚠️ 5초 초과 (P4 위반)"
fi
echo "   응답: $ANALYZE_RESP"

# 4. 캐싱 동작 (동일 요청 2회)
echo "4. 캐싱 동작 확인..."
START2=$(date +%s%N)
curl -s -X POST "$DEPLOY_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"address":"서울특별시 강남구 테헤란로 152","jibun_address":"서울특별시 강남구 역삼동 798-22","building_name":"삼성역빌딩","sigungu_code":"11680","rental_type":"jeonse","deposit":50000}' > /dev/null
END2=$(date +%s%N)
ELAPSED_MS2=$(( (END2 - START2) / 1000000 ))
echo "   2회째 응답 시간: ${ELAPSED_MS2}ms"
if [ "$ELAPSED_MS2" -lt "$ELAPSED_MS" ]; then
  echo "   ✅ 캐싱 적용됨 (1회: ${ELAPSED_MS}ms → 2회: ${ELAPSED_MS2}ms)"
else
  echo "   ⚠️ 캐싱 미적용"
fi

echo ""
echo "=== 검증 완료 ==="
