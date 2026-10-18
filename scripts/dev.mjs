import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';

const python = path.resolve(process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
if (!existsSync(python)) {
  console.error('Run uv sync first. Python 3.12 and uv are required.');
  process.exit(1);
}
const children = [
  spawn(python, ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8008'], { stdio: 'inherit' }),
  spawn(process.execPath, ['node_modules/next/dist/bin/next', 'dev', '--hostname', '127.0.0.1', '--port', '3000'], { stdio: 'inherit' }),
];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  children.forEach(child => child.kill());
  process.exitCode = code;
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
children.forEach(child => {
  child.on('error', error => { console.error(error); stop(1); });
  child.on('exit', code => stop(code || 0));
});
