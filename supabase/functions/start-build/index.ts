import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": Deno.env.get("APP_ORIGIN") ?? "https://artemkinus-collab.github.io",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { ...corsHeaders, "Content-Type": "application/json" },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return reply({ error: "Method not allowed" }, 405);
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return reply({ error: "Authentication required" }, 401);

  const url = Deno.env.get("SUPABASE_URL");
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const githubToken = Deno.env.get("GITHUB_TOKEN");
  const owner = Deno.env.get("GITHUB_OWNER");
  const repo = Deno.env.get("GITHUB_REPO");
  if (!url || !anonKey || !serviceKey || !githubToken || !owner || !repo) return reply({ error: "Server is not configured" }, 503);

  const authClient = createClient(url, anonKey, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false } });
  const { data: { user }, error: authError } = await authClient.auth.getUser();
  if (authError || !user) return reply({ error: "Invalid session" }, 401);

  let input: Record<string, unknown>;
  try { input = await req.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
  const sourceRepository = String(input.source_repository ?? "");
  const sourceRef = String(input.source_ref ?? "main");
  const projectPath = String(input.project_path ?? ".");
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(sourceRepository) ||
      !sourceRef || sourceRef.length > 200 || sourceRef.startsWith("-") || sourceRef.includes("..") ||
      !projectPath || projectPath.startsWith("/") || projectPath.includes("\\") ||
      projectPath.split("/").includes("..") || projectPath.length > 240) {
    return reply({ error: "Invalid project parameters" }, 400);
  }

  const admin = createClient(url, serviceKey, { auth: { persistSession: false } });
  const { data: build, error: insertError } = await admin.from("builds").insert({
    owner_id: user.id, target: "web-zip", status: "queued",
    source_repository: sourceRepository, source_ref: sourceRef, project_path: projectPath,
  }).select("id").single();
  if (insertError || !build) return reply({ error: "Could not create build record" }, 500);

  const endpoint = "https://api.github.com/repos/" + owner + "/" + repo + "/actions/workflows/build-web.yml/dispatches";
  const dispatch = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Accept": "application/vnd.github+json", "Authorization": "Bearer " + githubToken,
      "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json", "User-Agent": "GPT-Build-Lab",
    },
    body: JSON.stringify({ ref: "main", inputs: {
      project_repository: sourceRepository, project_ref: sourceRef, project_path: projectPath, build_id: build.id,
    }}),
  });
  if (!dispatch.ok) {
    await admin.from("builds").update({
      status: "failed", error_message: "GitHub rejected workflow dispatch (" + dispatch.status + ")",
      updated_at: new Date().toISOString(),
    }).eq("id", build.id).eq("owner_id", user.id);
    return reply({ error: "Could not start GitHub Actions workflow" }, 502);
  }
  return reply({ build_id: build.id, status: "queued" }, 202);
});
