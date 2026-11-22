// Public username-only signup endpoint for GPT Build Lab.
// The service-role key is read only from Edge Function secrets and never sent to browsers.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const allowedOrigins = new Set([
  "https://artemkinus-collab.github.io",
]);

const corsHeaders = {
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info, x-supabase-api-version",
  "Vary": "Origin",
};

function json(body: Record<string, unknown>, status: number, origin: string | null) {
  const headers = new Headers(corsHeaders);
  headers.set("Content-Type", "application/json; charset=utf-8");
  if (origin && allowedOrigins.has(origin)) headers.set("Access-Control-Allow-Origin", origin);
  return new Response(JSON.stringify(body), { status, headers });
}

async function sha256(value: string) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  const origin = req.headers.get("origin");
  if (req.method === "OPTIONS") {
    if (!origin || !allowedOrigins.has(origin)) return new Response("Origin not allowed", { status: 403 });
    return new Response("ok", { headers: { ...corsHeaders, "Access-Control-Allow-Origin": origin } });
  }
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405, origin);
  if (!origin || !allowedOrigins.has(origin)) return json({ error: "Origin not allowed" }, 403, origin);

  let payload: unknown;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "Некорректный запрос." }, 400, origin);
  }

  const body = payload as { username?: unknown; password?: unknown };
  const username = typeof body.username === "string" ? body.username.trim().toLowerCase() : "";
  const password = typeof body.password === "string" ? body.password : "";

  if (!/^[a-z0-9_.-]{3,24}$/.test(username)) {
    return json({ error: "Имя должно содержать 3–24 символа: латиницу, цифры, точку, дефис или подчёркивание." }, 400, origin);
  }
  if (password.length < 8 || password.length > 72) {
    return json({ error: "Пароль должен содержать от 8 до 72 символов." }, 400, origin);
  }

  const ip = req.headers.get("cf-connecting-ip") || req.headers.get("x-real-ip");
  if (!ip) return json({ error: "Не удалось проверить источник запроса. Попробуй позже." }, 503, origin);

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceRoleKey) {
    return json({ error: "Сервер регистрации ещё не настроен администратором." }, 503, origin);
  }

  const admin = createClient(supabaseUrl, serviceRoleKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  try {
    const ipHash = await sha256(ip);
    const { data: allowed, error: limitError } = await admin.rpc("gbl_consume_signup_attempt", { p_ip_hash: ipHash });
    if (limitError) {
      console.error("Signup rate-limit check failed:", limitError.message);
      return json({ error: "Сервис регистрации временно недоступен." }, 503, origin);
    }
    if (allowed !== true) {
      return json({ error: "Слишком много попыток регистрации с этого подключения. Попробуй позже." }, 429, origin);
    }

    // Internal address is only an Auth identifier. No email is sent.
    const email = username + "@gptbuildlab.example.com";
    const { data, error } = await admin.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: { username },
    });

    if (error || !data.user) {
      const message = error?.message || "Account creation failed";
      console.error("Signup failed:", message);
      if (/already|registered|exists|duplicate/i.test(message)) {
        return json({ error: "Это имя уже занято. Если ты уже пробовал зарегистрироваться раньше, проверь список пользователей Supabase." }, 409, origin);
      }
      return json({ error: "Не удалось создать аккаунт. Проверь имя и попробуй позже." }, 400, origin);
    }

    return json({ ok: true, username }, 201, origin);
  } catch (error) {
    console.error("Unexpected signup error:", error instanceof Error ? error.message : "unknown");
    return json({ error: "Внутренняя ошибка сервера регистрации." }, 500, origin);
  }
});
