import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

// Helper to convert Gemini contents format to standard OpenAI messages
function convertToOpenAIMessages(contents: any[], systemInstruction: any) {
  const messages: any[] = [];
  
  if (systemInstruction?.parts?.[0]?.text) {
    messages.push({ role: "system", content: systemInstruction.parts[0].text });
  }
  
  contents.forEach((msg) => {
    const role = msg.role === "model" || msg.role === "assistant" ? "assistant" : "user";
    const text = msg.parts?.[0]?.text || "";
    messages.push({ role, content: text });
  });
  
  return messages;
}

// Fetch helper with exponential backoff and random jitter
async function fetchWithRetry(url: string, options: RequestInit, maxRetries = 4, baseDelayMs = 1500) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      // Retry on 429 (Rate Limit) or 503 (Server Overload/Unavailable)
      if (response.status === 429 || response.status === 503) {
        if (attempt === maxRetries - 1) {
          console.error(`Max retries reached. Returning final status error ${response.status}`);
          return response;
        }
        
        // Jittered backoff: (2^attempt * baseDelay) + random(0, 1000)
        const delay = Math.pow(2, attempt) * baseDelayMs + Math.random() * 1000;
        console.warn(`⚠️ API returned ${response.status} (Attempt ${attempt + 1}/${maxRetries}). Retrying in ${Math.round(delay)}ms...`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        continue;
      }
      
      return response;
    } catch (err) {
      if (attempt === maxRetries - 1) {
        throw err;
      }
      const delay = Math.pow(2, attempt) * baseDelayMs + Math.random() * 1000;
      console.warn(`⚠️ Connection failed (Attempt ${attempt + 1}/${maxRetries}). Retrying in ${Math.round(delay)}ms... Error:`, err);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error("API request failed after maximum retry attempts.");
}

export async function POST(req: NextRequest) {
  const startTime = Date.now();
  let questionLength = 0;
  let responseLength = 0;
  let statusCode = 200;

  try {
    const body = await req.json();
    const contents = body.contents || [];
    const systemInstruction = body.systemInstruction;
    
    try {
      questionLength = JSON.stringify(contents).length;
    } catch {}

    // 1. Fetch active provider, model, and keys from Supabase
    const { data: configRows, error: configError } = await supabase
      .from("tse_config")
      .select("key, value");

    if (configError || !configRows) {
      console.error("Database config fetch error:", configError);
      return NextResponse.json(
        { error: "System configuration could not be loaded." },
        { status: 500 }
      );
    }

    const config: Record<string, string> = {};
    configRows.forEach((row) => {
      config[row.key] = row.value;
    });

    const provider = (config.provider || "gemini").toLowerCase();
    const model = config.model || "gemini-2.5-flash";
    
    let apiKey = "";
    let answerText = "";
    let providerResponse: any = null;

    console.log(`Forwarding request to: ${provider} | Model: ${model}`);

    if (provider === "gemini") {
      apiKey = config.gemini_api_key;
      if (!apiKey) {
        return NextResponse.json({ error: "Gemini API key is not configured." }, { status: 400 });
      }

      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
      const response = await fetchWithRetry(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      statusCode = response.status;
      providerResponse = await response.json();

      if (!response.ok) {
        throw new Error(providerResponse?.error?.message || "Gemini API request failed.");
      }

      answerText = providerResponse?.candidates?.[0]?.content?.parts?.[0]?.text || "";

    } else if (provider === "openai") {
      apiKey = config.openai_api_key;
      if (!apiKey) {
        return NextResponse.json({ error: "OpenAI API key is not configured." }, { status: 400 });
      }

      const url = "https://api.openai.com/v1/chat/completions";
      const messages = convertToOpenAIMessages(contents, systemInstruction);
      
      const response = await fetchWithRetry(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`
        },
        body: JSON.stringify({ model, messages }),
      });

      statusCode = response.status;
      providerResponse = await response.json();

      if (!response.ok) {
        throw new Error(providerResponse?.error?.message || "OpenAI API request failed.");
      }

      answerText = providerResponse?.choices?.[0]?.message?.content || "";

    } else if (provider === "openrouter") {
      apiKey = config.openrouter_api_key;
      if (!apiKey) {
        return NextResponse.json({ error: "OpenRouter API key is not configured." }, { status: 400 });
      }

      const url = "https://openrouter.ai/api/v1/chat/completions";
      const messages = convertToOpenAIMessages(contents, systemInstruction);
      
      const response = await fetchWithRetry(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`,
          "HTTP-Referer": "https://github.com/adityasing9/TSE",
          "X-Title": "TSE Terminal Assistant"
        },
        body: JSON.stringify({ model, messages }),
      });

      statusCode = response.status;
      providerResponse = await response.json();

      if (!response.ok) {
        throw new Error(providerResponse?.error?.message || "OpenRouter API request failed.");
      }

      answerText = providerResponse?.choices?.[0]?.message?.content || "";

    } else if (provider === "anthropic") {
      apiKey = config.anthropic_api_key;
      if (!apiKey) {
        return NextResponse.json({ error: "Anthropic API key is not configured." }, { status: 400 });
      }

      const url = "https://api.anthropic.com/v1/messages";
      const anthropicMessages = contents.map((msg: any) => ({
        role: msg.role === "model" || msg.role === "assistant" ? "assistant" : "user",
        content: msg.parts?.[0]?.text || "",
      }));
      const system = systemInstruction?.parts?.[0]?.text || undefined;

      const response = await fetchWithRetry(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model,
          system,
          messages: anthropicMessages,
          max_tokens: 4096
        }),
      });

      statusCode = response.status;
      providerResponse = await response.json();

      if (!response.ok) {
        throw new Error(providerResponse?.error?.message || "Anthropic API request failed.");
      }

      answerText = providerResponse?.content?.[0]?.text || "";

    } else if (provider === "groq") {
      apiKey = config.groq_api_key;
      if (!apiKey) {
        return NextResponse.json({ error: "Groq API key is not configured." }, { status: 400 });
      }

      const url = "https://api.groq.com/openai/v1/chat/completions";
      const messages = convertToOpenAIMessages(contents, systemInstruction);
      
      const response = await fetchWithRetry(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${apiKey}`
        },
        body: JSON.stringify({ model, messages }),
      });

      statusCode = response.status;
      providerResponse = await response.json();

      if (!response.ok) {
        throw new Error(providerResponse?.error?.message || "Groq API request failed.");
      }

      answerText = providerResponse?.choices?.[0]?.message?.content || "";
    } else {
      return NextResponse.json({ error: `Unsupported provider: ${provider}` }, { status: 400 });
    }

    responseLength = answerText.length;

    // 2. Normalise output
    const normalizedResponse = {
      candidates: [
        {
          content: {
            parts: [
              {
                text: answerText
              }
            ],
            role: "model"
          },
          finishReason: "STOP",
          index: 0
        }
      ]
    };

    // 3. Log query stats
    const responseTimeMs = Date.now() - startTime;
    try {
      await supabase.from("tse_logs").insert({
        question_length: questionLength,
        response_length: responseLength,
        response_time_ms: responseTimeMs,
        status_code: statusCode,
      });
    } catch (dbErr) {
      console.error("Failed to execute log insert:", dbErr);
    }

    return NextResponse.json(normalizedResponse);

  } catch (err: any) {
    const responseTimeMs = Date.now() - startTime;
    console.error("Proxy error caught:", err);
    
    // Log the failure
    try {
      await supabase.from("tse_logs").insert({
        question_length: questionLength,
        response_length: 0,
        response_time_ms: responseTimeMs,
        status_code: statusCode === 200 ? 500 : statusCode,
      });
    } catch (dbErr) {
      console.error("Failed to execute error log insert:", dbErr);
    }

    return NextResponse.json(
      { error: err.message || err },
      { status: statusCode === 200 ? 500 : statusCode }
    );
  }
}
