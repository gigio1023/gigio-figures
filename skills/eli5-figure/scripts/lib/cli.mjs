// Shared command-line plumbing: argument parsing with a usage line, and one-line errors.
import { parseArgs } from 'node:util';

export function parseCli(usage, options, { min = 1, max = 1 } = {}) {
  let parsed;
  try {
    parsed = parseArgs({ allowPositionals: true, options });
  } catch (e) {
    fail(`${e.message}\nusage: ${usage}`);
  }
  const n = parsed.positionals.length;
  if (n < min || n > max) fail(`usage: ${usage}`);
  return parsed;
}

function fail(message, code = 2) {
  console.error(message);
  process.exit(code);
}

// Errors from Playwright carry "page.evaluate: Error: ..." prefixes and a stack; keep the message.
const clean = (e) => String(e && e.message ? e.message : e)
  .replace(/^[\w.]+: (?=Error:)/, '')
  .replace(/^(Type|Range|Syntax)?Error: /, '')
  .split('\n    at ')[0]
  .trimEnd();

// Runs main; any error prints as `<file>: <message>` and exits with the error's exitCode or 2.
export async function run(main, file) {
  try {
    await main();
  } catch (e) {
    fail(file ? `${file}: ${clean(e)}` : `error: ${clean(e)}`, e && e.exitCode ? e.exitCode : 2);
  }
}
