import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": Deno.env.get("APP_ORIGIN") ?? "https://artemkinus-collab.github.io",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "GET") return Response.json({ error: "Method not allowed" }, { status: 405, headers: corsHeaders });
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return Response.json({ error: "Authentication required" }, { status: 401, headers: corsHeaders });
  const url = Deno.env.get("SUPABASE_URL");
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
  if (!url || !anonKey) return Response.json({ error: "Server not configured" }, { status: 503, headers: corsHeaders });
  const client = createClient(url, anonKey, {
    global: { headers: { Authorization: authHeader } },
    auth: { persistSession: false },
  });
  const { data: { user }, error: authError } = await client.auth.getUser();
  if (authError || !user) return Response.json({ error: "Invalid session" }, { status: 401, headers: corsHeaders });
  const buildId = new URL(req.url).searchParams.get("build_id");
  if (!buildId || !/^[0-9a-f-]{36}$/i.test(buildId)) return Response.json({ error: "Invalid build_id" }, { status: 400, headers: corsHeaders });
  const { data, error } = await client.from("builds")
    .select("id,status,source_repository,source_ref,project_path,artifact_name,workflow_url,error_message,created_at,updated_at")
    .eq("id", buildId).eq("owner_id", user.id).single();
  if (error || !data) return Response.json({ error: "Build not found" }, { status: 404, headers: corsHeaders });
  return Response.json({ build: data }, { headers: corsHeaders });
});
