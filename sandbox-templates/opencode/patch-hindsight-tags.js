#!/usr/bin/env node
// patch-hindsight-tags.js
// Idempotent patch for @toady00/opencode-hindsight plugin to support runtime
// template variable resolution ({project}, {gitProject}, {directory}, {pwd}) in retain tags.

import fs from 'node:fs';
import path from 'node:path';

function findAllTargets() {
    const home = process.env.HOME || '';
    const candidates = [
        path.join(home, '.config/opencode/node_modules/@toady00/opencode-hindsight/dist/index.js'),
        path.join(home, '.cache/opencode/packages/@toady00/opencode-hindsight/dist/index.js'),
        path.resolve(process.cwd(), 'node_modules/@toady00/opencode-hindsight/dist/index.js'),
    ];
    return candidates.filter(p => fs.existsSync(p));
}

const targetPaths = findAllTargets();

if (targetPaths.length === 0) {
    console.log('[patch-hindsight-tags] No target @toady00/opencode-hindsight files found.');
    process.exit(0);
}

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

for (const targetPath of targetPaths) {
    let code = fs.readFileSync(targetPath, 'utf8');

    if (code.includes('resolveTemplateTags(')) {
        console.log(`[patch-hindsight-tags] Already patched: ${targetPath}`);
        continue;
    }

    // Append helper function at top or bottom
    code = templateResolverFn + '\n' + code;

    // Inject resolveTemplateTags call into retain options
    // Replace: tags: options.tags or tags: params.tags
    let patchedCode = code.replace(/tags:\s*options\.tags/g, 'tags: resolveTemplateTags(options.tags)');
    patchedCode = patchedCode.replace(/tags:\s*params\.tags/g, 'tags: resolveTemplateTags(params.tags)');

    if (patchedCode !== code) {
        fs.writeFileSync(targetPath, patchedCode, 'utf8');
        console.log(`[patch-hindsight-tags] Successfully patched: ${targetPath}`);
    } else {
        console.warn(`[patch-hindsight-tags] Target pattern not found in: ${targetPath}`);
    }
}
