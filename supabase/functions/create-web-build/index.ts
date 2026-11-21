import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
const corsHeaders = {
 "Access-Control-Allow-Origin": Deno.env.get("ALLOWED_ORIGIN") ?? "https://artemkinus-collab.github.io",
 "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
 "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function reply(body: unknown, status = 200) {
 return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json" } });
}
Deno.serve(async (req) => {
 if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
 if (req.method !== "POST") return reply({ error: "Method not allowed" }, 405);
 const authorization = req.headers.get("Authorization") ?? "";
 const jwt = authorization.startsWith("Bearer ") ? authorization.slice(7) : "";
 if (!jwt) return reply({ error: "Authentication required" }, 401);
 const url = Deno.env.get("SUPABASE_URL"), anon = Deno.env.get("SUPABASE_ANON_KEY");
 const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"), ghToken = Deno.env.get("GPT_BUILD_LAB_GITHUB_TOKEN");
 const workflowRepo = Deno.env.get("GPT_BUILD_LAB_REPOSITORY") ?? "artemkinus-collab/GPT-Build-Lab";
 if (!url || !anon || !service || !ghToken) return reply({ error: "Build service is not configured yet." }, 503);
 const authClient = createClient(url, anon, { auth: { persistSession: false } });
 const { data: authData, error: authError } = await authClient.auth.getUser(jwt);
 if (authError || !authData.user) return reply({ error: "Invalid session" }, 401);
 let input: Record<string, unknown>;
 try { input = await req.json(); } catch { return reply({ error: "Invalid JSON" }, 400); }
 const sourceRepository = String(input.source_repository ?? "");
 const sourceRef = String(input.source_ref ?? "main");
 const projectPath = String(input.project_path ?? ".");
 const projectName = String(input.project_name ?? "Web project").trim().slice(0, 80);
 if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(sourceRepository)) return reply({ error: "Repository must be owner/name." }, 400);
 if (!sourceRef || sourceRef.length > 200 || sourceRef.startsWith("-") || sourceRef.includes("..")) return reply({ error: "Invalid branch, tag, or commit." }, 400);
 if (!projectPath || projectPath.length > 240 || projectPath.startsWith("/") || projectPath.includes("\\") || projectPath.split("/").includes("..")) return reply({ error: "Project path must be a safe relative path." }, 400);
 if (!projectName) return reply({ error: "Project name is required." }, 400);
 const admin = createClient(url, service, { auth: { persistSession: false } });
 const { data: project, error: projectError } = await admin.from("projects").insert({
  user_id: authData.user.id, name: projectName, target: "web",
  source_repository: sourceRepository, source_ref: sourceRef, project_path: projectPath,
 }).select("id").single();
 if (projectError || !project) return reply({ error: "Could not save project." }, 500);
 const { data: build, error: insertError } = await admin.from("builds").insert({
  user_id: authData.user.id, project_id: project.id, target: "web", status: "queued",
 }).select("id").single();
 if (insertError || !build) return reply({ error: "Could not create build record." }, 500);
 const dispatch = await fetch(`https://api.github.com/repos/${workflowRepo}/actions/workflows/build-web.yml/dispatches`, {
  method: "POST",
  headers: { "Accept": "application/vnd.github+json", "Authorization": `Bearer ${ghToken}`, "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json" },
  body: JSON.stringify({ ref: "main", inputs: { project_repository: sourceRepository, project_ref: sourceRef, project_path: projectPath, build_id: build.id, project_name: projectName } }),
 });
 if (dispatch.status !== 204) {
  const detail = (await dispatch.text()).slice(0, 1200);
  await admin.from("builds").update({ status: "failed", error_message: `GitHub dispatch failed (${dispatch.status}): ${detail}`, completed_at: new Date().toISOString() }).eq("id", build.id).eq("user_id", authData.user.id);
  return reply({ error: "GitHub could not queue the build.", build_id: build.id }, 502);
 }
 return reply({ build_id: build.id, status: "queued" }, 202);
});
