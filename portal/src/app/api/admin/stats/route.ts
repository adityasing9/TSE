import { NextRequest, NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

async function authenticate(req: NextRequest) {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return false;
  }
  const password = authHeader.split(" ")[1];

  const { data, error } = await supabase
    .from("tse_config")
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

  try {
    // 1. Fetch total requests count
    const { count: totalRequests, error: countError } = await supabase
      .from("tse_logs")
      .select("*", { count: "exact", head: true });

    if (countError) throw countError;

    // 2. Fetch requests today (UTC day start)
    const todayStart = new Date();
    todayStart.setUTCHours(0, 0, 0, 0);

    const { count: requestsToday, error: todayError } = await supabase
      .from("tse_logs")
      .select("*", { count: "exact", head: true })
      .gte("timestamp", todayStart.toISOString());

    if (todayError) throw todayError;

    // 3. Fetch requests in the last minute (for RPM check)
    const oneMinuteAgo = new Date(Date.now() - 60000);
    const { count: requestsLastMinute, error: minuteError } = await supabase
      .from("tse_logs")
      .select("*", { count: "exact", head: true })
      .gte("timestamp", oneMinuteAgo.toISOString());

    if (minuteError) throw minuteError;

    // 4. Fetch last 15 detailed logs
    const { data: logs, error: logsError } = await supabase
      .from("tse_logs")
      .select("*")
      .order("timestamp", { ascending: false })
      .limit(15);

    if (logsError) throw logsError;

    // 5. Calculate average response time and success rate
    let avgResponseTimeMs = 0;
    let successRate = 100;

    if (logs && logs.length > 0) {
      const successful = logs.filter((l) => l.status_code >= 200 && l.status_code < 300);
      successRate = Math.round((successful.length / logs.length) * 100);

      const totalTime = logs.reduce((acc, curr) => acc + (curr.response_time_ms || 0), 0);
      avgResponseTimeMs = Math.round(totalTime / logs.length);
    }

    return NextResponse.json({
      total_requests: totalRequests || 0,
      requests_today: requestsToday || 0,
      requests_last_minute: requestsLastMinute || 0,
      avg_response_time_ms: avgResponseTimeMs,
      success_rate: successRate,
      logs: logs || [],
      // Gemini 2.5 Flash Free Tier limit is 15 RPM
      rpm_limit: 15,
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message || err }, { status: 500 });
  }
}
