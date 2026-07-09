import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

async function authenticate(req: NextRequest) {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return false;
  }
  const password = authHeader.split(" ")[1];

  const { data, error } = await supabase
    .from("examai_config")
    .select("value")
    .eq("key", "admin_password")
    .single();

  if (error || !data) {
    return false;
  }

  return password === data.value;
}

export async function GET(req: NextRequest) {
  const isAuth = await authenticate(req);
  if (!isAuth) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { data, error } = await supabase
    .from("examai_config")
    .select("key, value");

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const config: Record<string, string> = {};
  data.forEach((item) => {
    config[item.key] = item.value;
  });

  return NextResponse.json({
    provider: config.provider || "gemini",
    model: config.model || "gemini-2.5-flash",
    gemini_api_key: config.gemini_api_key || "",
    openai_api_key: config.openai_api_key || "",
    openrouter_api_key: config.openrouter_api_key || "",
    anthropic_api_key: config.anthropic_api_key || "",
    has_password: !!config.admin_password,
  });
}

export async function POST(req: NextRequest) {
  const isAuth = await authenticate(req);
  if (!isAuth) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const body = await req.json();
    const allowedKeys = [
      "provider", 
      "model", 
      "gemini_api_key", 
      "openai_api_key", 
      "openrouter_api_key", 
      "anthropic_api_key", 
      "admin_password"
    ];

    const updates = [];
    for (const key of allowedKeys) {
      if (body[key] !== undefined) {
        // Don't save empty/whitespace-only passwords
        if (key === "admin_password" && body[key].trim() === "") {
          continue;
        }
        updates.push({
          key,
          value: body[key],
          updated_at: new Date()
        });
      }
    }

    if (updates.length > 0) {
      const { error } = await supabase
        .from("examai_config")
        .upsert(updates);
      if (error) throw error;
    }

    return NextResponse.json({ success: true });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || err }, { status: 500 });
  }
}
