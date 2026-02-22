#!/usr/bin/env node
/**
 * Check OS and open Chrome (handles Windows and macOS).
 * Usage: node scripts/check-os-and-chrome.js [url]
 */

const { execSync } = require('child_process');
const os = require('os');

const platform = os.platform(); // 'darwin' | 'win32' | ...
const url = process.argv[2] || '';

const isMac = platform === 'darwin';
const isWindows = platform === 'win32';

console.log('OS:', isMac ? 'macOS' : isWindows ? 'Windows' : platform);
console.log('Platform:', platform);

if (isMac) {
  // Use full path so it works when PATH is minimal (e.g. launched from IDE)
  const open = '/usr/bin/open';
  if (url) {
    execSync(`${open} -a "Google Chrome" --new --args "${url.replace(/"/g, '\\"')}"`, {
      stdio: 'inherit',
      shell: true,
    });
  } else {
    execSync(`${open} -a "Google Chrome"`, { stdio: 'inherit', shell: true });
  }
  console.log(url ? `Opened Chrome with ${url}` : 'Opened Chrome');
} else if (isWindows) {
  const chromePath =
    process.env.LOCALAPPDATA +
    '\\Google\\Chrome\\Application\\chrome.exe';
  const target = url || 'about:blank';
  execSync(`"${chromePath}" "${target}"`, { stdio: 'inherit', shell: true });
  console.log(url ? `Opened Chrome with ${url}` : 'Opened Chrome');
} else {
  console.log('Unsupported platform for this script.');
  process.exit(1);
}
