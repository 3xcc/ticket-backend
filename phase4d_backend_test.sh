#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://ticket-backend-jdpp.onrender.com"
EMAIL="admin@example.com"
PASSWORD="NewStrongPassword123"

echo "🔑 Logging in..."
LOGIN_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=$EMAIL&password=$PASSWORD")

echo "Login response: $LOGIN_RESPONSE"
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "❌ Failed to get token"
  exit 1
fi
echo "✅ Got token"

echo "🖼  Creating dummy PNG..."
echo -n -e '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x8d\xf7\x00\x00\x00\x00IEND\xaeB`\x82' > /tmp/dummy.png

echo "📤 Uploading file..."
FILE_ID=$(curl -s -L -X POST "$BASE_URL/api/files/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/dummy.png;type=image/png" | jq -r '.id')

if [[ -z "$FILE_ID" || "$FILE_ID" == "null" ]]; then
  echo "❌ Failed to upload file"
  exit 1
fi
echo "✅ File uploaded: $FILE_ID"

echo "📝 Creating template..."
TEMPLATE_ID=$(curl -s -L -X POST "$BASE_URL/api/templates/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Phase4D Test Template\",\"background_file_id\":\"$FILE_ID\",\"fields\":[{\"name\":\"QR Code\",\"type\":\"qr\",\"x\":50,\"y\":50,\"width\":200,\"height\":200}]}" | jq -r '.id')

if [[ -z "$TEMPLATE_ID" || "$TEMPLATE_ID" == "null" ]]; then
  echo "❌ Failed to create template"
  exit 1
fi
echo "✅ Template created: $TEMPLATE_ID"

echo "📥 Fetching template..."
curl -s -L -X GET "$BASE_URL/api/templates/$TEMPLATE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo "🎯 Backend Phase 4D test complete."
