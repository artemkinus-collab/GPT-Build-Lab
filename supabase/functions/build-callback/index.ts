import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": Deno.env.get("APP_ORIGIN") ?? "https://artemkinus-collab.github.io",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-build-callback-secret",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return Response.json({ error: "Method not allowed" }, { status: 405, headers: corsHeaders });
  const expected = Deno.env.get("BUILD_CALLBACK_SECRET");
  const supplied = req.headers.get("x-build-callback-secret");
  if (!expected || !supplied || supplied !== expected) return Response.json({ error: "Unauthorized" }, { status: 401, headers: corsHeaders });

  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) return Response.json({ error: "Server not configured" }, { status: 503, headers: corsHeaders });
  const body = await req.json().catch(() => null);
  const buildId = body?.build_id;
  const status = body?.status;
  if (typeof buildId !== "string" || !/^[0-9a-f-]{36}$/i.test(buildId) ||
      !["completed", "failed", "cancelled"].includes(status)) {
    return Response.json({ error: "Invalid callback payload" }, { status: 400, headers: corsHeaders });
  }
  const admin = createClient(url, serviceKey, { auth: { persistSession: false } });
  const { error } = await admin.from("builds").update({
    status,
    artifact_name: typeof body.artifact_name === "string" ? body.artifact_name.slice(0, 120) : null,
    workflow_url: typeof body.workflow_url === "string" ? body.workflow_url.slice(0, 500) : null,
    error_message: typeof body.error_message === "string" ? body.error_message.slice(0, 500) : null,
    updated_at: new Date().toISOString(),
  }).eq("id", buildId);
  if (error) return Response.json({ error: "Could not update build status" }, { status: 500, headers: corsHeaders });
  return Response.json({ ok: true }, { headers: corsHeaders });
});
