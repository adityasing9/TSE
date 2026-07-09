#!/bin/bash

# Colors
CYAN='\033[0;96m'
MAGENTA='\033[0;95m'
GREEN='\033[0;92m'
YELLOW='\033[0;93m'
RED='\033[0;91m'
DIM='\033[0;90m'
BOLD='\033[1m'
RESET='\033[0m'

PROXY_URL="https://portal-olive-ten.vercel.app/api/chat"
CONFIG_URL="https://portal-olive-ten.vercel.app/api/admin/config"

# Cache admin passcode for session
CACHED_ADMIN_PASS="$ADMIN_PASS"

# Helper to get admin passcode
get_admin_passcode() {
    if [ -n "$CACHED_ADMIN_PASS" ]; then
        echo "$CACHED_ADMIN_PASS"
        return
    fi
    # Check local config file
    CONFIG_PATH="$HOME/.examai/.env"
    if [ -f "$CONFIG_PATH" ]; then
        CACHED_ADMIN_PASS=$(grep -E '^(admin_password|DB_PASSWORD)=' "$CONFIG_PATH" | head -n 1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
    if [ -z "$CACHED_ADMIN_PASS" ]; then
        echo -ne "${YELLOW}  [Auth] Enter Admin Passcode: ${RESET}" >&2
        read -s -r CACHED_ADMIN_PASS
        echo "" >&2
    fi
    echo "$CACHED_ADMIN_PASS"
}

# Helper to send config updates to Vercel
set_vercel_config() {
    local provider="$1"
    local model="$2"
    local pass
    pass=$(get_admin_passcode)

    if [ -z "$pass" ]; then
        echo -e "${RED}  Authorization failed. Could not update settings.${RESET}" >&2
        return 1
    fi

    # Build JSON payload using python3
    local payload
    payload=$(python3 -c "
import json
payload = {}
if '$provider': payload['provider'] = '$provider'
if '$model': payload['model'] = '$model'
print(json.dumps(payload))
")

    local response
    response=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $pass" -d "$payload" "$CONFIG_URL")
    
    local success
    success=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'success' in data and data['success']:
        print('OK')
    else:
        print('ERROR: ' + str(data.get('error', 'Unknown error')))
except:
    print('ERROR: Parse failed')
")

    if [ "$success" = "OK" ]; then
        return 0
    else
        echo -e "${RED}  Update failed: $success${RESET}" >&2
        return 1
    fi
}

# --- STARTUP ENVIRONMENT CONFIGURATION (OPTIONAL) ---
if [ -n "$SET_PROVIDER" ] || [ -n "$SET_MODEL" ]; then
    echo -e "${YELLOW}  ⚙️ Updating Vercel portal settings...${RESET}"
    if set_vercel_config "$SET_PROVIDER" "$SET_MODEL"; then
        echo -e "${GREEN}  ✔ Settings updated successfully!${RESET}"
    else
        echo -e "${YELLOW}  ⚠️ Settings update failed. Continuing with existing portal config...${RESET}"
    fi
    # Clean environment vars for this session
    unset SET_PROVIDER
    unset SET_MODEL
    echo ""
fi

clear
echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}  ║${MAGENTA}    ★  ASK AI  -  Terminal Assistant  ★   ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ║${DIM}      Powered by Google Gemini (Free)     ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${DIM}  Type your question. Type 'exit' to quit.${RESET}"
echo -e "${DIM}  Type '/provider [name]' or '/model [name]' to switch LLMs.${RESET}"
echo -e "${DIM}  ─────────────────────────────────────────────${RESET}"
echo ""

while true; do
    echo -ne "${GREEN}${BOLD}  You > ${RESET}"
    read -r question
    
    if [[ -z "$question" ]]; then
        continue
    fi
    
    # Handle quit
    if [[ "$question" == "exit" || "$question" == "quit" || "$question" == "q" ]]; then
        echo -e "\n${MAGENTA}  Goodbye!${RESET}\n"
        break
    fi
    
    # --- INTERACTIVE CHAT COMMANDS ---
    if [[ "$question" == /provider\ * ]]; then
        new_prov="${question:10}"
        # Trim whitespace
        new_prov=$(echo "$new_prov" | xargs)
        echo -e "${YELLOW}  Switching provider to '$new_prov'...${RESET}"
        if set_vercel_config "$new_prov" ""; then
            echo -e "${GREEN}  ✔ Active provider changed to '$new_prov'!${RESET}"
        fi
        echo ""
        continue
    fi

    if [[ "$question" == /model\ * ]]; then
        new_model="${question:7}"
        new_model=$(echo "$new_model" | xargs)
        echo -e "${YELLOW}  Switching model to '$new_model'...${RESET}"
        if set_vercel_config "" "$new_model"; then
            echo -e "${GREEN}  ✔ Active model changed to '$new_model'!${RESET}"
        fi
        echo ""
        continue
    fi

    echo -ne "${DIM}  Thinking...${RESET}"
    
    # Escape double quotes for JSON payload safely
    ESCAPED_QUESTION=$(echo "$question" | sed 's/"/\\"/g' | sed 's/\\/\\\\/g')
    
    # Build payload
    PAYLOAD=$(cat <<EOF
{
  "contents": [
    {
      "parts": [
        {
          "text": "${ESCAPED_QUESTION}"
        }
      ]
    }
  ],
  "systemInstruction": {
    "parts": [
      {
        "text": "You are a helpful, concise terminal assistant. Give short, clear answers. Do NOT use markdown formatting - no asterisks (*), no hash symbols (#), no backticks. Use plain text only. Use dashes (-) for bullet points. Keep answers brief and to the point unless the user asks for detail."
      }
    ]
  }
}
EOF
)

    # Call API proxy
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$PROXY_URL")
    
    # Clear "Thinking..." line
    echo -ne "\r\033[K"
    
    # Parse JSON response using python3
    ANSWER=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print('ERROR: ' + str(data['error']))
    elif 'candidates' in data and len(data['candidates']) > 0:
        print(data['candidates'][0]['content']['parts'][0]['text'])
    else:
        print('ERROR: Unexpected response format: ' + json.dumps(data))
except Exception as e:
    print('ERROR: Failed to parse response: ' + str(e))
")

    if [[ "$ANSWER" == ERROR:* ]]; then
        echo -e "${RED}  $ANSWER${RESET}\n"
    else
        echo -e "\n${CYAN}${BOLD}  AI >${RESET}\n"
        # Print with indent
        echo "$ANSWER" | while IFS= read -r line; do
            if [[ -z "$line" ]]; then
                echo ""
            else
                echo "    $line"
            fi
        done
        echo -e "\n${DIM}  ─────────────────────────────────────────────${RESET}\n"
    fi
done
