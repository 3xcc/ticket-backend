#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
BASE_URL="https://ticket-backend-jdpp.onrender.com"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="NewStrongPassword123"

# Test data identifiers
TEST_USER_EMAIL="testuser@example.com"
EVENT_ID=""
TICKET_ID=""
TEMPLATE_ID=""
FILE_ID=""
TOKEN=""

# --- Helper: check if resource exists ---
resource_exists() {
  local method=$1
  local url=$2
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
    -H "Authorization: Bearer $TOKEN")
  [[ "$status" == "200" ]]
}

# --- Cleanup function ---
cleanup() {
  echo "🧹 Cleaning up test data..."
  if [[ -n "$TOKEN" ]]; then
    if [[ -n "$TEST_USER_EMAIL" ]] && resource_exists GET "$BASE_URL/api/admin/delete_user?email=$TEST_USER_EMAIL"; then
      curl -s -X DELETE "$BASE_URL/api/admin/delete_user" \
        -H "Authorization: Bearer $TOKEN" \
        --get --data-urlencode "email=$TEST_USER_EMAIL" >/dev/null || true
      echo "  - Test user deleted"
    fi
    if [[ -n "$EVENT_ID" ]] && resource_exists GET "$BASE_URL/api/events/$EVENT_ID"; then
      curl -s -X DELETE "$BASE_URL/api/events/$EVENT_ID" \
        -H "Authorization: Bearer $TOKEN" >/dev/null || true
      echo "  - Test event deleted"
    fi
    if [[ -n "$TICKET_ID" ]] && resource_exists GET "$BASE_URL/api/tickets/$TICKET_ID"; then
      curl -s -X DELETE "$BASE_URL/api/tickets/$TICKET_ID" \
        -H "Authorization: Bearer $TOKEN" >/dev/null || true
      echo "  - Test ticket deleted"
    fi
    if [[ -n "$TEMPLATE_ID" ]] && resource_exists GET "$BASE_URL/api/templates/$TEMPLATE_ID"; then
      curl -s -X DELETE "$BASE_URL/api/templates/$TEMPLATE_ID" \
        -H "Authorization: Bearer $TOKEN" >/dev/null || true
      echo "  - Test template deleted"
    fi
    if [[ -n "$FILE_ID" ]] && resource_exists GET "$BASE_URL/api/files/$FILE_ID"; then
      curl -s -X DELETE "$BASE_URL/api/files/$FILE_ID" \
        -H "Authorization: Bearer $TOKEN" >/dev/null || true
      echo "  - Test file deleted"
    fi
  fi
}
trap cleanup EXIT

# --- Login ---
echo "🔑 Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

echo "Login raw response: $LOGIN_RESPONSE"
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null || echo "")

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
  echo "❌ Failed to get admin token"
  exit 1
fi
echo "✅ Admin token acquired"

# -------------------------
# Phase 1: Core Foundations
# -------------------------

echo "👤 Creating test user..."
USER_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/admin/create_user" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_USER_EMAIL\",\"password\":\"TestPass123\",\"role\":\"scanner\"}")

echo "User creation raw response: $USER_RESPONSE"
if echo "$USER_RESPONSE" | grep -qi "created"; then
  echo "✅ User created successfully"
else
  echo "❌ Failed to create user"
  exit 1
fi

echo "📅 Creating test event..."
EVENT_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/events/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Event","date":"2025-12-31","location":"Test Venue"}')

echo "Event creation raw response: $EVENT_RESPONSE"
EVENT_ID=$(echo "$EVENT_RESPONSE" | jq -r '.id' 2>/dev/null || echo "")
if [[ -z "$EVENT_ID" || "$EVENT_ID" == "null" ]]; then
  echo "❌ Failed to create event"
  exit 1
fi
echo "✅ Event created: $EVENT_ID"

echo "🎟 Issuing ticket to test user..."
TICKET_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/tickets/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"$EVENT_ID\",\"user_id\":\"$ADMIN_EMAIL\"}")

echo "Ticket creation raw response: $TICKET_RESPONSE"
TICKET_ID=$(echo "$TICKET_RESPONSE" | jq -r '.id' 2>/dev/null || echo "")
if [[ -z "$TICKET_ID" || "$TICKET_ID" == "null" ]]; then
  echo "❌ Failed to create ticket"
  exit 1
fi
echo "✅ Ticket created: $TICKET_ID"

# -------------------------
# Phase 3: File Handling
# -------------------------

echo "🖼 Creating dummy PNG..."
echo -n -e '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x8d\xf7\x00\x00\x00\x00IEND\xaeB`\x82' > /tmp/dummy.png

echo "📤 Uploading background file..."
FILE_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/files/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/dummy.png;type=image/png")

echo "File upload raw response: $FILE_RESPONSE"
FILE_ID=$(echo "$FILE_RESPONSE" | jq -r '.id' 2>/dev/null || echo "")
if [[ -z "$FILE_ID" || "$FILE_ID" == "null" ]]; then
  echo "❌ Failed to upload file"
  exit 1
fi
echo "✅ File uploaded: $FILE_ID"

# -------------------------
# Phase 4D: Ticket Template
# -------------------------

echo "📝 Creating ticket template..."
TEMPLATE_RESPONSE=$(curl -s -L -X POST "$BASE_URL/api/templates/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Full Test Template\",\"background_file_id\":\"$FILE_ID\",\"fields\":[{\"name\":\"QR Code\",\"type\":\"qr\",\"x\":50,\"y\":50,\"width\":200,\"height\":200}]}")

echo "Template creation raw response: $TEMPLATE_RESPONSE"
TEMPLATE_ID=$(echo "$TEMPLATE_RESPONSE" | jq -r '.id' 2>/dev/null || echo "")
if [[ -z "$TEMPLATE_ID" || "$TEMPLATE_ID" == "null" ]]; then
  echo "❌ Failed to create template"
  exit 1
fi
echo "✅ Template created: $TEMPLATE_ID"

echo "📥 Fetching template..."
curl -s -L -X GET "$BASE_URL/api/templates/$TEMPLATE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo "🎨 Rendering ticket..."
curl -s -L -X GET "$BASE_URL/api/render/$TEMPLATE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  --output fulltest_render.png

if [[ ! -s fulltest_render.png ]]; then
  echo "❌ Rendered PNG is empty or missing"
  exit 1
fi

FILE_SIZE=$(stat -c%s "fulltest_render.png")
echo "✅ Rendered PNG saved as fulltest_render.png (${FILE_SIZE} bytes)"

echo "🎯 Full backend test (Phase 1 → Phase 4D) complete."
