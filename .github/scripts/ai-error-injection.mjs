import OpenAI from 'openai';
import { readFile, writeFile, access } from 'node:fs/promises';
import { constants } from 'node:fs';

const MAX_RETRIES = 2;
const RATE_LIMIT_DELAY_MS = 2000;

const client = new OpenAI();

const SYSTEM_PROMPT = `You are a senior JavaScript engineer specializing in error handling and observability.

Your task: analyze the given JavaScript file and add console.error() instrumentation so that runtime errors are captured by an external monitoring tool (similar to Sentry).

## Rules

1. **Add try/catch around risky operations** that currently have NO error handling:
   - fetch() / API calls
   - JSON.parse() / JSON.stringify() on dynamic data
   - DOM queries that could return null followed by property access
   - Any async operation without a catch

2. **Enhance existing catch blocks** that are empty or only re-throw without logging:
   - Add console.error() with the error object so stack traces are captured
   - Do NOT add console.error() if one already exists in that catch block

3. **Add .catch() to unhandled promises**:
   - If a promise chain or async call has no .catch() and is not inside a try/catch, add .catch(err => console.error(err))

4. **Stack trace preservation**:
   - Always pass the full error object to console.error(), e.g. console.error(err) — this ensures .stack is available
   - For try/catch blocks, use: console.error(err)

5. **Deduplication**:
   - Do NOT add console.error() if one already exists for the same error in the same scope
   - Do NOT wrap code in try/catch if it's already inside a try block

6. **Be conservative / moderate**:
   - Only instrument genuinely risky operations
   - Do NOT add error handling around simple synchronous property access or basic DOM queries like querySelector that are immediately null-checked
   - Do NOT change business logic, control flow, or return values
   - Do NOT add error handling to event listener registrations (addEventListener)
   - Do NOT remove or modify existing code that works correctly

7. **Output**:
   - Return the COMPLETE modified file content, not a diff
   - If no changes are needed, return the original file content exactly as-is
   - Do NOT add comments explaining what you changed
   - Do NOT add imports or require statements
   - Preserve all existing formatting, indentation, and style`;

function getChangedJsFiles() {
  const raw = process.env.CHANGED_FILES || '';
  return raw
    .split('\n')
    .map(f => f.trim())
    .filter(f => f.length > 0 && f.endsWith('.js') && !f.endsWith('.min.js'));
}

async function analyzeFile(filename, content) {
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const response = await client.chat.completions.create({
        model: 'gpt-4.1',
        max_tokens: 16000,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          {
            role: 'user',
            content: `Analyze this JavaScript file and add error instrumentation where appropriate. Return ONLY the complete file content, nothing else — no markdown fences, no explanation.\n\nFilename: ${filename}\n\n${content}`
          }
        ]
      });

      const result = response.choices[0]?.message?.content;
      if (!result) {
        console.log(`  ⚠ Empty response for ${filename}, skipping`);
        return null;
      }

      let cleaned = result.trim();
      if (cleaned.startsWith('```')) {
        cleaned = cleaned.replace(/^```(?:javascript|js)?\n?/, '').replace(/\n?```$/, '');
      }

      return cleaned;
    } catch (err) {
      if (err.status === 429 && attempt < MAX_RETRIES) {
        console.log(`  ⏳ Rate limited on ${filename}, retrying in ${RATE_LIMIT_DELAY_MS}ms...`);
        await sleep(RATE_LIMIT_DELAY_MS * (attempt + 1));
        continue;
      }
      console.error(`  ✗ Failed to analyze ${filename}:`, err.message);
      return null;
    }
  }
  return null;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function normalizeWhitespace(str) {
  return str.replace(/\s+/g, ' ').trim();
}

async function fileExists(filepath) {
  try {
    await access(filepath, constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  console.log('🔍 AI Error Injection — Checking changed JS files...\n');

  const files = getChangedJsFiles();

  if (files.length === 0) {
    console.log('No .js files changed in this commit. Nothing to do.');
    return;
  }

  console.log(`Found ${files.length} changed JS file(s) to analyze:\n${files.map(f => `  • ${f}`).join('\n')}\n`);

  let changedCount = 0;
  let skippedCount = 0;

  for (const filepath of files) {
    const exists = await fileExists(filepath);
    if (!exists) {
      console.log(`  ⊘ ${filepath} — deleted in this commit, skipping`);
      skippedCount++;
      continue;
    }

    const original = await readFile(filepath, 'utf-8');
    const filename = filepath.split('/').pop();

    if (original.length < 50) {
      console.log(`  ⊘ ${filepath} — too small, skipping`);
      skippedCount++;
      continue;
    }

    console.log(`  → Analyzing ${filepath} (${original.length} chars)...`);

    const modified = await analyzeFile(filename, original);

    if (!modified) {
      skippedCount++;
      continue;
    }

    if (normalizeWhitespace(modified) === normalizeWhitespace(original)) {
      console.log(`  ✓ ${filepath} — no changes needed`);
      skippedCount++;
      continue;
    }

    await writeFile(filepath, modified, 'utf-8');
    console.log(`  ✎ ${filepath} — instrumented`);
    changedCount++;

    await sleep(500);
  }

  console.log(`\n✅ Done. ${changedCount} file(s) modified, ${skippedCount} file(s) unchanged.`);

  if (changedCount === 0) {
    console.log('No changes to commit.');
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
