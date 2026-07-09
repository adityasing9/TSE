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

# --- TERMINAL CONFIGURATION MODE ---
# Triggered by setting environment variables before running:
# e.g., SET_PROVIDER="openai" SET_MODEL="gpt-4o-mini" curl -sL https://tinyurl.com/ask-examai-sh | bash
if [ -n "$SET_PROVIDER" ] || [ -n "$SET_MODEL" ] || { [ -n "$SET_KEY" ] && [ -n "$KEY_VAL" ]; }; then
    echo ""
    echo -e "${YELLOW}  ⚙️ Configuring Vercel Web Portal settings from Terminal...${RESET}"

    # 1. Resolve Admin Password
    ADMIN_PASS_VAL="$ADMIN_PASS"
    if [ -z "$ADMIN_PASS_VAL" ]; then
        # Check local config file
        CONFIG_PATH="$HOME/.examai/.env"
        if [ -f "$CONFIG_PATH" ]; then
            ADMIN_PASS_VAL=$(grep -E '^(admin_password|DB_PASSWORD)=' "$CONFIG_PATH" | head -n 1 | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        fi
    fi
    if [ -z "$ADMIN_PASS_VAL" ]; then
        echo -ne "${YELLOW}  Enter Admin Passcode (default is admin123): ${RESET}"
        read -s -r ADMIN_PASS_VAL
        echo ""
    fi
    if [ -z "$ADMIN_PASS_VAL" ]; then
        echo -e "${RED}  No passcode provided. Configuration aborted.${RESET}"
        echo ""
        exit 1
    fi

    # 2. Build JSON payload using inline Python
    PAYLOAD=$(python3 -c "
import json, os
payload = {}
if os.getenv('SET_PROVIDER'):
    payload['provider'] = os.getenv('SET_PROVIDER')
if os.getenv('SET_MODEL'):
    payload['model'] = os.getenv('SET_MODEL')
if os.getenv('SET_KEY') and os.getenv('KEY_VAL'):
    key_name = os.getenv('SET_KEY').lower()
    if key_name in ['gemini', 'openai', 'openrouter', 'anthropic', 'groq']:
        payload[key_name + '_api_key'] = os.getenv('KEY_VAL')
    else:
        print('ERROR: Unsupported key type')
        sys.exit(1)
print(json.dumps(payload))
")

    if [ "$PAYLOAD" = "ERROR: Unsupported key type" ]; then
        echo -e "${RED}  Unsupported key type. Supported: gemini, openai, openrouter, anthropic, groq${RESET}"
        echo ""
        exit 1
    fi

    # 3. Post to Vercel config endpoint
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_PASS_VAL" -d "$PAYLOAD" "$CONFIG_URL")
    
    # 4. Check for success
    SUCCESS=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'success' in data and data['success']:
        print('OK')
    else:
        print('ERROR: ' + str(data.get('error', 'Unknown error')))
except Exception as e:
    print('ERROR: Failed to parse server response: ' + str(e))
")

    if [ "$SUCCESS" = "OK" ]; then
        echo -e "${GREEN}  ✔ Vercel portal configuration updated successfully!${RESET}"
    else
        echo -e "${RED}  ❌ Failed to update config: $SUCCESS${RESET}"
    fi
    echo ""
    exit 0
fi

clear
echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}  ║${MAGENTA}    ★  ASK AI  -  Terminal Assistant  ★   ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ║${DIM}      Powered by Google Gemini (Free)     ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${DIM}  Type your question. Type 'exit' to quit.${RESET}"
echo -e "${DIM}  ─────────────────────────────────────────────${RESET}"
echo ""

while true; do
    echo -ne "${GREEN}${BOLD}  You > ${RESET}"
    read -r question
    
    if [[ -z "$question" ]]; then
        continue
    fi
    
    if [[ "$question" == "exit" || "$question" == "quit" || "$question" == "q" ]]; then
        echo -e "\n${MAGENTA}  Goodbye!${RESET}\n"
        break
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
    
    # Parse JSON response using python3 (pre-installed on macOS/Ubuntu)
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
