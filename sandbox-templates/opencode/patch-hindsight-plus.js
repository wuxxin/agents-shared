#!/usr/bin/env node
// DEPRECATED — 2026-07-31
// This script is no longer needed. The project switched from opencode-hindsight-plus
// to @toady00/opencode-hindsight (github:Toady00/opencode-hindsight#v0.2.2) which
// supports per-agent bank routing and project tags natively via defaults.tags and
// per-agent options.hindsight.tags. No runtime patching required.
//
// This file is retained for reference. It is NOT called during install.
//
// Original purpose: Patch opencode-hindsight-plus to:
//   1. Inject robust project-name resolution into buildRetainTemplateVars
//      so {user_id}, {project}, {gitProject} always resolve to a real name.
//   2. Fix resolveRetainTags to not drop tags just because the value after
//      a colon is empty (e.g. "project:" when cwd is /).
//
// Primary strategy: regex-match and replace. Falls back to broader patterns.

import fs from 'node:fs';
import path from 'node:path';

const home = process.env.HOME || '';

// Find all installed copies — bun install puts one in node_modules,
// but OpenCode loads plugins from its own package cache (multiple paths).
function findAllTargets() {
    const home = process.env.HOME || '';
    const patterns = [
        path.join(home, '.config/opencode/node_modules/opencode-hindsight-plus/dist/index.js'),
        path.join(home, '.cache/opencode/packages/opencode-hindsight-plus@latest/node_modules/opencode-hindsight-plus/dist/index.js'),
        path.join(home, '.cache/opencode/packages/opencode-hindsight-plus/node_modules/opencode-hindsight-plus/dist/index.js'),
    ];
    return patterns.filter(p => fs.existsSync(p));
}

const targetPaths = findAllTargets();

if (targetPaths.length === 0) {
    console.log('[patch-hindsight-plus] No target files found.');
    process.exit(0);
}

let code = fs.readFileSync(targetPaths[0], 'utf8');

// ────────────────────────────────────────────────────────────────
// Patch 1: buildRetainTemplateVars — robust project name derivation
// Falls back: deriveGitProjectName → basename(dir) → PWD basename → "unknown-project"
// ────────────────────────────────────────────────────────────────
const patchedBuildFn = `function buildRetainTemplateVars(input) {
  const now = input.now ?? /* @__PURE__ */ new Date();
  const timestamp = now.toISOString().replace(/\\.\\d{3}Z$/, "Z");
  const dir = input.directory || process.cwd();
  let gitProj = deriveGitProjectName(dir, true);
  if (!gitProj) gitProj = dir ? basename(dir) : "";
  if (!gitProj && process.env.PWD) gitProj = basename(process.env.PWD);
  if (!gitProj) gitProj = "unknown-project";
  return {
    session_id: input.sessionId,
    bank_id: input.bankId,
    timestamp,
    user_id: input.userId ?? process.env.HINDSIGHT_USER_ID ?? gitProj,
    project: gitProj,
    gitProject: gitProj
  };
}`;

// ────────────────────────────────────────────────────────────────
// Patch 2: resolveRetainTags — don't drop tags with empty colon-values
// The original skips "project:" when {user_id} is empty. We keep it.
// ────────────────────────────────────────────────────────────────
const patchedResolveTagsFn = `function resolveRetainTags(rawTags, vars) {
  if (!rawTags.length) return void 0;
  const tags = [];
  for (const original of rawTags) {
    const resolved = applyTemplateString(original, vars).trim();
    if (!resolved) continue;
    tags.push(resolved);
  }
  return tags.length ? tags : void 0;
}`;

// ── Apply Patch 1: buildRetainTemplateVars ──
const buildFnRegex = /\bfunction buildRetainTemplateVars\(input\)\s*\{[\s\S]*?\n\}/;
const buildMatch = code.match(buildFnRegex);

if (buildMatch) {
    code = code.replace(buildFnRegex, patchedBuildFn);
    console.log('[patch-hindsight-plus] Patch 1: buildRetainTemplateVars — updated.');
} else {
    // Broader fallback
    const broadRegex = /\bfunction buildRetainTemplateVars\([\s\S]*?\breturn\s*\{[\s\S]*?\n  \};[\s\S]*?\n\}/;
    const broadMatch = code.match(broadRegex);
    if (broadMatch) {
        code = code.replace(broadRegex, patchedBuildFn);
        console.log('[patch-hindsight-plus] Patch 1: buildRetainTemplateVars — updated (broad match).');
    } else {
        console.warn('[patch-hindsight-plus] Patch 1 FAILED: could not find buildRetainTemplateVars.');
    }
}

// ── Apply Patch 2: resolveRetainTags ──
const resolveTagsRegex = /\bfunction resolveRetainTags\(rawTags,\s*vars\)\s*\{[\s\S]*?\n\}/;
const resolveMatch = code.match(resolveTagsRegex);

if (resolveMatch) {
    code = code.replace(resolveTagsRegex, patchedResolveTagsFn);
    console.log('[patch-hindsight-plus] Patch 2: resolveRetainTags — updated (colon-value filter removed).');
} else {
    console.warn('[patch-hindsight-plus] Patch 2 FAILED: could not find resolveRetainTags.');
}

for (const p of targetPaths) {
    fs.writeFileSync(p, code, 'utf8');
}
console.log('[patch-hindsight-plus] Patched', targetPaths.length, 'file(s):');
for (const p of targetPaths) {
    console.log('  ' + p);
}
