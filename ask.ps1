# ============================================================
#  ASK AI - Simple Terminal LLM Assistant
#  Run directly: irm https://raw.githubusercontent.com/adityasing9/examai-cli/master/ask.ps1 | iex
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

    # Banner
    Write-Host ""
    Write-Host "$cyan$bold  ╔══════════════════════════════════════════╗$reset"
    Write-Host "$cyan$bold  ║$magenta    ★  ASK AI  -  Terminal Assistant  ★   $cyan║$reset"
    Write-Host "$cyan$bold  ║$dim      Powered by Google Gemini (Free)     $cyan║$reset"
    Write-Host "$cyan$bold  ╚══════════════════════════════════════════╝$reset"
    Write-Host ""

    # Check/Get API Key
    $apiKey = $env:GEMINI_API_KEY
    if (-not $apiKey) {
        $configPath = "$env:USERPROFILE\.examai\.env"
        if (Test-Path $configPath) {
            $envContent = Get-Content $configPath -ErrorAction SilentlyContinue
            foreach ($line in $envContent) {
                if ($line -match "^GEMINI_API_KEY=(.+)$") {
                    $apiKey = $Matches[1].Trim().Trim('"').Trim("'")
                    break
                }
            }
        }
    }

    if (-not $apiKey) {
        Write-Host "$yellow  No API key found.$reset"
        Write-Host "$dim  Get a free key at: ${cyan}https://aistudio.google.com/apikey$reset"
        Write-Host ""
        $apiKey = Read-Host "  Paste your Gemini API Key"
        if (-not $apiKey) {
            Write-Host "$red  No key provided. Exiting.$reset"
            return
        }
        # Save for future use
        $envDir = "$env:USERPROFILE\.examai"
        if (-not (Test-Path $envDir)) { New-Item -ItemType Directory -Path $envDir -Force | Out-Null }
        $envFile = "$envDir\.env"
        if (Test-Path $envFile) {
            $content = Get-Content $envFile -Raw
            if ($content -match "GEMINI_API_KEY=") {
                $content = $content -replace "GEMINI_API_KEY=.*", "GEMINI_API_KEY=$apiKey"
                Set-Content $envFile $content -NoNewline
            } else {
                Add-Content $envFile "`nGEMINI_API_KEY=$apiKey"
            }
        } else {
            Set-Content $envFile "GEMINI_API_KEY=$apiKey"
        }
        $env:GEMINI_API_KEY = $apiKey
        Write-Host "$green  Key saved to ~\.examai\.env$reset"
        Write-Host ""
    }

    Write-Host "$dim  Type your question and press Enter. Type 'exit' or 'q' to quit.$reset"
    Write-Host "$dim  ─────────────────────────────────────────────$reset"
    Write-Host ""

    # Chat loop
    while ($true) {
        Write-Host -NoNewline "$green$bold  You > $reset"
        $question = Read-Host
        if (-not $question -or $question.Trim().ToLower() -in @('exit', 'quit', 'q', 'bye')) {
            Write-Host ""
            Write-Host "$magenta  Goodbye! $dim(Session ended)$reset"
            Write-Host ""
            break
        }

        # Show thinking indicator
        Write-Host -NoNewline "$dim  Thinking...$reset"

        # Build request
        $url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$apiKey"
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
            $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json; charset=utf-8" -ErrorAction Stop

            # Clear "Thinking..."
            Write-Host "`r$(' ' * 30)`r" -NoNewline

            # Extract answer
            $answer = $response.candidates[0].content.parts[0].text

            # Clean any remaining markdown artifacts
            $answer = $answer -replace '\*\*\*(.+?)\*\*\*', '$1'
            $answer = $answer -replace '\*\*(.+?)\*\*', '$1'
            $answer = $answer -replace '\*(.+?)\*', '$1'
            $answer = $answer -replace '`{3}[\s\S]*?`{3}', '$&'  # preserve code blocks
            $answer = $answer -replace '(?m)^#{1,6}\s+', ''       # remove heading markers
            $answer = $answer -replace '`([^`]+)`', '$1'          # remove inline backticks

            # Print formatted answer
            Write-Host ""
            Write-Host "$cyan$bold  AI >$reset"
            Write-Host ""

            # Print each line with indent
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
            if ($errMsg -match "403") {
                Write-Host "$red  Invalid API key. Get a free key at: https://aistudio.google.com/apikey$reset"
            } elseif ($errMsg -match "429") {
                Write-Host "$red  Rate limit hit. Wait a moment and try again.$reset"
            } else {
                Write-Host "$red  Error: $errMsg$reset"
            }
            Write-Host ""
        }
    }
}

# Auto-run when piped via iex
Start-AskAI
