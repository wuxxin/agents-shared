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

// Patch buildRetainTemplateVars to use `basename` (not `path.basename`) and inject dynamic project variables
const targetOld = `function buildRetainTemplateVars(input) {
  const now = input.now ?? /* @__PURE__ */ new Date();
  const timestamp = now.toISOString().replace(/\\.\\d{3}Z$/, "Z");
  return {
    session_id: input.sessionId,
    bank_id: input.bankId,
    timestamp,
    user_id: input.userId ?? process.env.HINDSIGHT_USER_ID ?? ""
  };
}`;

const patchedVars = `function buildRetainTemplateVars(input) {
  const now = input.now ?? /* @__PURE__ */ new Date();
  const timestamp = now.toISOString().replace(/\\.\\d{3}Z$/, "Z");
  const dir = input.directory || process.cwd();
  const gitProj = deriveGitProjectName(dir, true) || (dir ? basename(dir) : "unknown");
  return {
    session_id: input.sessionId,
    bank_id: input.bankId,
    timestamp,
    user_id: input.userId ?? process.env.HINDSIGHT_USER_ID ?? gitProj,
    project: gitProj,
    gitProject: gitProj
  };
}`;

if (code.includes('gitProject: gitProj')) {
    // Replace existing broken patch if present
    code = code.replace(
        /function buildRetainTemplateVars\(input\) \{[\s\S]*?\n\}/,
        patchedVars
    );
    fs.writeFileSync(distPath, code, 'utf8');
    console.log(
        '[patch-hindsight-plus] Successfully updated buildRetainTemplateVars with correct scope bindings.'
    );
} else if (code.includes(targetOld)) {
    code = code.replace(targetOld, patchedVars);
    fs.writeFileSync(distPath, code, 'utf8');
    console.log(
        '[patch-hindsight-plus] Successfully applied buildRetainTemplateVars patch.'
    );
} else {
    console.warn(
        '[patch-hindsight-plus] Target template function not matched.'
    );
}
