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

    # Cached admin passcode for the session
    $script:cachedAdminPass = $env:ADMIN_PASS

    # Helper to resolve admin password
    function Get-AdminPasscode {
        if ($script:cachedAdminPass) {
            return $script:cachedAdminPass
        }
        # Check local file
        $configPath = "$env:USERPROFILE\.examai\.env"
        if (Test-Path $configPath) {
            $envContent = Get-Content $configPath -ErrorAction SilentlyContinue
            foreach ($line in $envContent) {
                if ($line -match "^admin_password=(.+)$" -or $line -match "^DB_PASSWORD=(.+)$") {
                    $script:cachedAdminPass = $Matches[1].Trim().Trim('"').Trim("'")
                    return $script:cachedAdminPass
                }
            }
        }
        # Prompt user
        Write-Host -NoNewline "$yellow  [Auth] Enter Admin Passcode: $reset"
        $script:cachedAdminPass = Read-Host
        return $script:cachedAdminPass
    }

    # Helper to send config update to Vercel
    function Set-VercelConfig {
        param(
            [string]$provider,
            [string]$model
        )
        $pass = Get-AdminPasscode
        if (-not $pass) {
            Write-Host "$red  Authorization failed. Could not update settings.$reset"
            return $false
        }

        $payload = @{}
        if ($provider) { $payload["provider"] = $provider }
        if ($model) { $payload["model"] = $model }
        $json = $payload | ConvertTo-Json

        try {
            $response = Invoke-RestMethod -Uri $configUrl -Method POST -Headers @{ Authorization = "Bearer $pass" } -Body $json -ContentType "application/json" -ErrorAction Stop
            return $true
        } catch {
            Write-Host "$red  Update failed: $_$reset"
            return $false
        }
    }

    # --- STARTUP ENVIRONMENT CONFIGURATION (OPTIONAL) ---
    if ($env:SET_PROVIDER -or $env:SET_MODEL) {
        Write-Host "$yellow  ⚙️ Updating Vercel portal settings...$reset"
        $ok = Set-VercelConfig -provider $env:SET_PROVIDER -model $env:SET_MODEL
        if ($ok) {
            Write-Host "$green  ✔ Settings updated successfully!$reset"
        } else {
            Write-Host "$yellow  ⚠️ Settings update failed. Continuing with existing portal config...$reset"
        }
        # Clean environment vars for this session
        $env:SET_PROVIDER = $null
        $env:SET_MODEL = $null
        Write-Host ""
    }

    # Banner
    Write-Host ""
    Write-Host "$cyan$bold  ╔══════════════════════════════════════════╗$reset"
    Write-Host "$cyan$bold  ║$magenta    ★  ASK AI  -  Terminal Assistant  ★   $cyan║$reset"
    Write-Host "$cyan$bold  ║$dim      Powered by Google Gemini (Free)     $cyan║$reset"
    Write-Host "$cyan$bold  ╚══════════════════════════════════════════╝$reset"
    Write-Host ""

    Write-Host "$dim  Type your question. Type 'exit' to quit.$reset"
    Write-Host "$dim  Type '/switch' to change LLMs, or '/password' to change admin passcode.$reset"
    Write-Host "$dim  ─────────────────────────────────────────────$reset"
    Write-Host ""

    # Chat loop
    while ($true) {
        Write-Host -NoNewline "$green$bold  You > $reset"
        $question = Read-Host
        if (-not $question) { continue }
        
        $trimmed = $question.Trim()
        if ($trimmed.ToLower() -in @('exit', 'quit', 'q', 'bye')) {
            Write-Host ""
            Write-Host "$magenta  Goodbye!$reset"
            Write-Host ""
            break
        }

        # --- INTERACTIVE SWITCH MENU ---
        if ($trimmed -eq "/switch") {
            $pass = Get-AdminPasscode
            if (-not $pass) {
                Write-Host "$red  Authorization failed. Could not switch settings.$reset"
                Write-Host ""
                continue
            }

            Write-Host ""
            Write-Host "$cyan  ┌─── Select AI Provider ───┐$reset"
            Write-Host "$cyan  │ 1. Google Gemini (Free)   │$reset"
            Write-Host "$cyan  │ 2. Groq (Ultra-fast)      │$reset"
            Write-Host "$cyan  │ 3. OpenAI (ChatGPT)       │$reset"
            Write-Host "$cyan  │ 4. OpenRouter             │$reset"
            Write-Host "$cyan  │ 5. Anthropic (Claude)     │$reset"
            Write-Host "$cyan  └───────────────────────────┘$reset"
            Write-Host -NoNewline "$yellow  Choose option (1-5): $reset"
            $opt = Read-Host
            
            $prov = $null
            $mdl = $null
            switch ($opt.Trim()) {
                "1" { $prov = "gemini"; $mdl = "gemini-2.5-flash" }
                "2" { $prov = "groq"; $mdl = "llama-3.3-70b-versatile" }
                "3" { $prov = "openai"; $mdl = "gpt-4o-mini" }
                "4" { $prov = "openrouter"; $mdl = "google/gemini-2.5-flash" }
                "5" { $prov = "anthropic"; $mdl = "claude-3-5-sonnet-20241022" }
                default { Write-Host "$red  Invalid selection.$reset`n"; continue }
            }

            Write-Host "$yellow  Switching to $prov ($mdl) centrally...$reset"
            $ok = Set-VercelConfig -provider $prov -model $mdl
            if ($ok) {
                Write-Host "$green  ✔ Centrally switched active model to $prov ($mdl)!$reset"
            }
            Write-Host ""
            continue
        }

        # --- CHANGE PASSWORD INTERACTIVELY ---
        if ($trimmed -eq "/password") {
            $currentPass = Get-AdminPasscode
            if (-not $currentPass) {
                Write-Host "$red  Authorization failed.$reset"
                Write-Host ""
                continue
            }
            
            Write-Host -NoNewline "$yellow  Enter NEW Admin Passcode: $reset"
            $newPass = Read-Host
            if (-not $newPass.Trim()) {
                Write-Host "$red  Passcode cannot be empty.$reset`n"
                continue
            }
            
            Write-Host "$yellow  Updating passcode centrally...$reset"
            $payload = @{ admin_password = $newPass }
            $json = $payload | ConvertTo-Json
            
            try {
                $response = Invoke-RestMethod -Uri $configUrl -Method POST -Headers @{ Authorization = "Bearer $currentPass" } -Body $json -ContentType "application/json" -ErrorAction Stop
                $script:cachedAdminPass = $newPass
                Write-Host "$green  ✔ Passcode updated successfully! Use the new passcode next time.$reset"
            } catch {
                Write-Host "$red  ❌ Failed to update passcode: $_$reset"
            }
            Write-Host ""
            continue
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
                $trimmedLine = $line.TrimEnd()
                if ($trimmedLine -eq "") {
                    Write-Host ""
                } else {
                    Write-Host "    $trimmedLine"
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
