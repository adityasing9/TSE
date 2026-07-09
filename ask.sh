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

clear
echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}  ║${MAGENTA}    ★  ASK AI  -  Terminal Assistant  ★   ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ║${DIM}      Powered by Google Gemini (Free)     ${CYAN}║${RESET}"
echo -e "${CYAN}${BOLD}  ╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${DIM}  Type your question. Type 'exit' to quit.${RESET}"
echo -e "${DIM}  ─────────────────────────────────────────────${RESET}"
echo ""

PROXY_URL="https://portal-olive-ten.vercel.app/api/chat"

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
