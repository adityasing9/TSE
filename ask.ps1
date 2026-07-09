# ============================================================
#  ASK AI - Simple Terminal LLM Assistant
#  Run directly: irm https://tinyurl.com/ask-examai | iex
#  Zero setup required - works instantly on any computer!
# ============================================================

function Start-AskAI {
    $ESC = [char]27

    # Colors
    $cyan = "$ESC[96m"
    $magenta = "$ESC[95m"
    $green = "$ESC[92m"
    $yellow = "$ESC[93m"
    $red = "$ESC[91m"
    $dim = "$ESC[90m"
    $bold = "$ESC[1m"
    $reset = "$ESC[0m"

    $proxyUrl = "https://portal-olive-ten.vercel.app/api/chat"
    $configUrl = "https://portal-olive-ten.vercel.app/api/admin/config"

    # --- TERMINAL CONFIGURATION MODE ---
    # Triggered by setting environment variables before running:
    # e.g., $env:SET_PROVIDER="openai"; $env:SET_MODEL="gpt-4o-mini"; irm ... | iex
    if ($env:SET_PROVIDER -or $env:SET_MODEL -or ($env:SET_KEY -and $env:KEY_VAL)) {
        Write-Host ""
        Write-Host "$yellow  ⚙️ Configuring Vercel Web Portal settings from Terminal...$reset"

        # 1. Resolve Admin Password
        $adminPass = $env:ADMIN_PASS
        if (-not $adminPass) {
            # Check local file
            $configPath = "$env:USERPROFILE\.examai\.env"
            if (Test-Path $configPath) {
                $envContent = Get-Content $configPath -ErrorAction SilentlyContinue
                foreach ($line in $envContent) {
                    if ($line -match "^admin_password=(.+)$" -or $line -match "^DB_PASSWORD=(.+)$") {
                        $adminPass = $Matches[1].Trim().Trim('"').Trim("'")
                        break
                    }
                }
            }
        }
        if (-not $adminPass) {
            # Default fallback or prompt
            Write-Host -NoNewline "$yellow  Enter Admin Passcode (default is admin123): $reset"
            $adminPass = Read-Host
        }
        if (-not $adminPass) {
            Write-Host "$red  No passcode provided. Configuration aborted.$reset"
            return
        }

        # 2. Build configuration payload
        $payload = @{}
        if ($env:SET_PROVIDER) { $payload["provider"] = $env:SET_PROVIDER }
        if ($env:SET_MODEL) { $payload["model"] = $env:SET_MODEL }
        if ($env:SET_KEY -and $env:KEY_VAL) {
            $keyName = $env:SET_KEY.ToLower()
            if ($keyName -in @('gemini', 'openai', 'openrouter', 'anthropic', 'groq')) {
                $payload["${keyName}_api_key"] = $env:KEY_VAL
            } else {
                Write-Host "$red  Unsupported key type: $keyName. Supported: gemini, openai, openrouter, anthropic, groq$reset"
                return
            }
        }

        $jsonPayload = $payload | ConvertTo-Json

        try {
            # 3. Post to Vercel config endpoint
            $response = Invoke-RestMethod -Uri $configUrl -Method POST -Headers @{ Authorization = "Bearer $adminPass" } -Body $jsonPayload -ContentType "application/json" -ErrorAction Stop
            Write-Host "$green  ✔ Vercel portal configuration updated successfully!$reset"
        } catch {
            Write-Host "$red  ❌ Failed to update config: $_$reset"
        }

        # 4. Clean up environment variables so next session starts normal chat
        $env:SET_PROVIDER = $null
        $env:SET_MODEL = $null
        $env:SET_KEY = $null
        $env:KEY_VAL = $null
        Write-Host ""
        return
    }

    # Banner
    Write-Host ""
    Write-Host "$cyan$bold  ╔══════════════════════════════════════════╗$reset"
    Write-Host "$cyan$bold  ║$magenta    ★  ASK AI  -  Terminal Assistant  ★   $cyan║$reset"
    Write-Host "$cyan$bold  ║$dim      Powered by Google Gemini (Free)     $cyan║$reset"
    Write-Host "$cyan$bold  ╚══════════════════════════════════════════╝$reset"
    Write-Host ""

    Write-Host "$dim  Type your question. Type 'exit' to quit.$reset"
    Write-Host "$dim  ─────────────────────────────────────────────$reset"
    Write-Host ""

    # Chat loop
    while ($true) {
        Write-Host -NoNewline "$green$bold  You > $reset"
        $question = Read-Host
        if (-not $question -or $question.Trim().ToLower() -in @('exit', 'quit', 'q', 'bye')) {
            Write-Host ""
            Write-Host "$magenta  Goodbye!$reset"
            Write-Host ""
            break
        }

        # Show thinking indicator
        Write-Host -NoNewline "$dim  Thinking...$reset"

        # Build payload matching Gemini structure
        $body = @{
            contents = @(
                @{
                    role = "user"
                    parts = @(@{ text = $question })
                }
            )
            systemInstruction = @{
                parts = @(@{
                    text = "You are a helpful, concise terminal assistant. Give short, clear answers. Do NOT use markdown formatting - no asterisks (*), no hash symbols (#), no backticks. Use plain text only. Use dashes (-) for bullet points. Keep answers brief and to the point unless the user asks for detail."
                })
            }
        } | ConvertTo-Json -Depth 10

        try {
            # Call our Vercel API proxy
            $response = Invoke-RestMethod -Uri $proxyUrl -Method POST -Body $body -ContentType "application/json; charset=utf-8" -ErrorAction Stop

            # Clear "Thinking..."
            Write-Host "`r$(' ' * 30)`r" -NoNewline

            # Extract answer
            $answer = $response.candidates[0].content.parts[0].text

            # Clean any remaining markdown artifacts
            $answer = $answer -replace '\*\*\*(.+?)\*\*\*', '$1'
            $answer = $answer -replace '\*\*(.+?)\*\*', '$1'
            $answer = $answer -replace '\*(.+?)\*', '$1'
            $answer = $answer -replace '`{3}[\s\S]*?`{3}', '$&'
            $answer = $answer -replace '(?m)^#{1,6}\s+', ''
            $answer = $answer -replace '`([^`]+)`', '$1'

            # Print formatted answer
            Write-Host ""
            Write-Host "$cyan$bold  AI >$reset"
            Write-Host ""

            $lines = $answer -split "`n"
            foreach ($line in $lines) {
                $trimmed = $line.TrimEnd()
                if ($trimmed -eq "") {
                    Write-Host ""
                } else {
                    Write-Host "    $trimmed"
                }
            }

            Write-Host ""
            Write-Host "$dim  ─────────────────────────────────────────────$reset"
            Write-Host ""

        } catch {
            Write-Host "`r$(' ' * 30)`r" -NoNewline
            $errMsg = $_.Exception.Message
            if ($errMsg -match "503") {
                Write-Host "$red  Gemini API is currently overloaded. Please wait a moment and try again.$reset"
            } else {
                Write-Host "$red  Error contacting admin portal proxy: $errMsg$reset"
            }
            Write-Host ""
        }
    }
}

# Auto-run
Start-AskAI
