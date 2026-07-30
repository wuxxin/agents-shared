#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';

const distPath = path.join(
    process.env.HOME || '',
    '.config/opencode/node_modules/opencode-hindsight-plus/dist/index.js'
);

if (!fs.existsSync(distPath)) {
    console.log('[patch-hindsight-plus] Target file not found:', distPath);
    process.exit(0);
}

let code = fs.readFileSync(distPath, 'utf8');

// Patch 1: Dynamic gitProject / project_id resolution in buildRetainTemplateVars
const oldTemplateVars = `function buildRetainTemplateVars(input) {
  const now = input.now ?? /* @__PURE__ */ new Date();
  const timestamp = now.toISOString().replace(/\\.\\d{3}Z$/, "Z");
  return {
    session_id: input.sessionId,
    bank_id: input.bankId,
    timestamp,
    user_id: input.userId ?? process.env.HINDSIGHT_USER_ID ?? ""
  };
}`;

const newTemplateVars = `function buildRetainTemplateVars(input) {
  const now = input.now ?? /* @__PURE__ */ new Date();
  const timestamp = now.toISOString().replace(/\\.\\d{3}Z$/, "Z");
  const dir = input.directory || process.cwd();
  const gitProj = deriveGitProjectName(dir, true) || (dir ? path.basename(dir) : "unknown");
  return {
    session_id: input.sessionId,
    bank_id: input.bankId,
    timestamp,
    user_id: input.userId ?? process.env.HINDSIGHT_USER_ID ?? gitProj,
    project: gitProj,
    gitProject: gitProj
  };
}`;

if (code.includes(oldTemplateVars)) {
    code = code.replace(oldTemplateVars, newTemplateVars);
    fs.writeFileSync(distPath, code, 'utf8');
    console.log(
        '[patch-hindsight-plus] Successfully patched buildRetainTemplateVars for dynamic project tagging.'
    );
} else if (code.includes('gitProject: gitProj')) {
    console.log('[patch-hindsight-plus] Already patched.');
} else {
    console.warn(
        '[patch-hindsight-plus] Warning: Target template pattern not matched.'
    );
}
