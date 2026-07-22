const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const { execFile } = require('child_process');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = __dirname;
const PYTHON_CMD = process.platform === 'win32' ? 'python' : 'python3';

// MIME Types
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// Execute Python Script & Return JSON Promise
function runPythonScript(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const fullScriptPath = path.join(__dirname, 'scripts', scriptPath);
    execFile(PYTHON_CMD, [fullScriptPath, ...args], { maxBuffer: 1024 * 1024 * 5 }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error running ${scriptPath}:`, stderr || error.message);
        return reject(error);
      }
      try {
        const parsed = JSON.parse(stdout.trim());
        resolve(parsed);
      } catch (parseErr) {
        resolve({ raw_output: stdout, parse_error: parseErr.message });
      }
    });
  });
}

// HTTP Server Listener
const server = http.createServer(async (req, res) => {
  const reqUrl = url.parse(req.url, true);
  const pathname = reqUrl.pathname;

  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  // --- API Endpoints ---
  if (pathname === '/api/yunqi') {
    const dateStr = reqUrl.query.date || new Date().toISOString().split('T')[0];
    try {
      const result = await runPythonScript('calculate_yunqi_api.py', [dateStr, '--json']);
      res.writeHead(200, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify(result));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  if (pathname === '/api/weather_alignment') {
    const dateStr = reqUrl.query.date || new Date().toISOString().split('T')[0];
    const cityStr = reqUrl.query.city || '北京';
    try {
      const result = await runPythonScript('weather_alignment.py', [dateStr, '--city', cityStr, '--mock', '--json']);
      res.writeHead(200, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify(result));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  if (pathname === '/api/personal_profile') {
    const birthDate = reqUrl.query.birth_date || '1990-05-20';
    try {
      const result = await runPythonScript('personal_yunqi_profile.py', [birthDate, '--json']);
      res.writeHead(200, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify(result));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  if (pathname === '/api/rag_search') {
    const query = reqUrl.query.q || reqUrl.query.query || '司天';
    try {
      const result = await runPythonScript('rag_search.py', [query, '--json']);
      res.writeHead(200, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify(result));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': MIME_TYPES['.json'] });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  // --- Static File Serving ---
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);
  const extname = path.extname(filePath).toLowerCase();

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      filePath = path.join(PUBLIC_DIR, 'index.html');
    }

    const contentType = MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
    fs.readFile(filePath, (readErr, content) => {
      if (readErr) {
        res.writeHead(500);
        return res.end('Server Error: File not readable.');
      }
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    });
  });
});

server.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`  ☯ 五运六气 AI Agent 可视化平台已启动  `);
  console.log(`  🔗 本地运行地址: http://localhost:${PORT}`);
  console.log(`  实时 RAG 文献检索与 Python 推算引擎 API 已就绪！`);
  console.log(`======================================================\n`);
});
