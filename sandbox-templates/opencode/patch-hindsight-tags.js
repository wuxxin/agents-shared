#!/usr/bin/env node
// patch-hindsight-tags.js
// Idempotent runtime patcher for sandbox OpenCode plugins:
// 1. @toady00/opencode-hindsight: Builds dist/index.js if missing, injects tag template variable resolution ({project}, {gitProject}, {directory}, {pwd}) + export id: "hindsight".
// 2. oh-my-opencode-slim: Defensive guard for minimumExpectedToolCount when disabledTools is undefined/non-array.

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

function findPkgDirs(pkgName) {
    const home = process.env.HOME || '';
    const bases = [
        path.join(home, '.config/opencode/node_modules'),
        path.join(home, '.cache/opencode/packages'),
        path.resolve(process.cwd(), 'node_modules'),
    ];
    const results = [];
    for (const base of bases) {
        const full = path.join(base, pkgName);
        if (fs.existsSync(full)) {
            results.push(full);
        }
    }
    return results;
}

// ────────────────────────────────────────────────────────────────
// Patch 1: @toady00/opencode-hindsight
// ────────────────────────────────────────────────────────────────
const hindsightPkgDirs = findPkgDirs('@toady00/opencode-hindsight');

if (hindsightPkgDirs.length === 0) {
    console.log('[patch-hindsight-tags] No target @toady00/opencode-hindsight directories found.');
} else {
    const templateResolverFn = `
function resolveTemplateTags(rawTags) {
  if (!Array.isArray(rawTags) || rawTags.length === 0) return rawTags;
  const dir = process.cwd();
  let project = process.env.PWD ? path.basename(process.env.PWD) : "";
  if (!project && dir) project = path.basename(dir);
  if (!project) project = "unknown-project";
  return rawTags.map(tag => {
    if (typeof tag !== "string") return tag;
    let t = tag;
    t = t.replaceAll("{project}", project);
    t = t.replaceAll("{gitProject}", project);
    t = t.replaceAll("{directory}", dir);
    t = t.replaceAll("{pwd}", dir);
    return t;
  });
}
`;

    for (const pkgDir of hindsightPkgDirs) {
        const distFile = path.join(pkgDir, 'dist/index.js');
        const srcDir = path.join(pkgDir, 'src');

        // Ensure dist/index.js is built if missing
        if (!fs.existsSync(distFile) && fs.existsSync(srcDir)) {
            console.log(`[patch-hindsight-tags] Building missing dist/index.js in: ${pkgDir}`);
            try {
                execSync('bun install && bun run build', { cwd: pkgDir, stdio: 'ignore' });
            } catch (buildErr) {
                console.warn(`[patch-hindsight-tags] Warning: bun build failed in ${pkgDir}: ${buildErr.message}`);
            }
        }

        const candidateFiles = [
            distFile,
            path.join(pkgDir, 'src/index.ts'),
            path.join(pkgDir, 'src/hindsight-client.ts'),
            path.join(pkgDir, 'src/shared-retain.ts'),
            path.join(pkgDir, 'src/auto-retain.ts'),
            path.join(pkgDir, 'src/tools.ts'),
        ].filter(p => fs.existsSync(p));

        for (const targetPath of candidateFiles) {
            let code = fs.readFileSync(targetPath, 'utf8');
            let modified = false;

            // 1a: Inject resolveTemplateTags into tag retention options
            if (!code.includes('resolveTemplateTags(')) {
                code = templateResolverFn + '\n' + code;
                code = code.replace(/tags:\s*options\.tags/g, 'tags: resolveTemplateTags(options.tags)');
                code = code.replace(/tags:\s*params\.tags/g, 'tags: resolveTemplateTags(params.tags)');
                code = code.replace(/tags:\s*config\.tags/g, 'tags: resolveTemplateTags(config.tags)');
                modified = true;
            }

            // 1b: Ensure plugin default export includes id: "hindsight"
            if (!code.includes('id: "hindsight"') && !code.includes('id:"hindsight"')) {
                code = code.replace('pluginModule = { server };', 'pluginModule = { id: "hindsight", server };');
                code = code.replace('pluginModule: PluginModule = { server };', 'pluginModule: PluginModule = { id: "hindsight", server };');
                code = code.replace('var pluginModule = { server };', 'var pluginModule = { id: "hindsight", server };');
                if (targetPath.endsWith('index.ts') || targetPath.endsWith('index.js')) {
                    code += '\nexport const id = "hindsight";\nif (typeof exports !== "undefined") { exports.id = "hindsight"; }\n';
                }
                modified = true;
            }

            if (modified) {
                fs.writeFileSync(targetPath, code, 'utf8');
                console.log(`[patch-hindsight-tags] Patched: ${targetPath}`);
            } else {
                console.log(`[patch-hindsight-tags] Already fully patched: ${targetPath}`);
            }
        }
    }
}

// ────────────────────────────────────────────────────────────────
// Patch 2: oh-my-opencode-slim — defensive guard for minimumExpectedToolCount
// ────────────────────────────────────────────────────────────────
const ohMyPkgDirs = findPkgDirs('oh-my-opencode-slim');

for (const pkgDir of ohMyPkgDirs) {
    const targetPath = path.join(pkgDir, 'dist/index.js');
    if (!fs.existsSync(targetPath)) continue;

    let code = fs.readFileSync(targetPath, 'utf8');

    if (code.includes('if (!Array.isArray(disabledTools)) disabledTools = [];')) {
        console.log(`[patch-hindsight-tags] Already patched oh-my-opencode-slim: ${targetPath}`);
        continue;
    }

    const targetFn = 'function minimumExpectedToolCount(disabledTools = []) {';
    const replacementFn = 'function minimumExpectedToolCount(disabledTools = []) { if (!Array.isArray(disabledTools)) disabledTools = [];';

    if (code.includes(targetFn)) {
        code = code.replace(targetFn, replacementFn);
        fs.writeFileSync(targetPath, code, 'utf8');
        console.log(`[patch-hindsight-tags] Patched oh-my-opencode-slim tool filter: ${targetPath}`);
    }
}
