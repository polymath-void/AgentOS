const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 18790;
const PUBLIC_DIR = path.join(__dirname, 'public');

function execPromise(cmd) {
  return new Promise((resolve) => {
    exec(cmd, (error, stdout) => {
      resolve(stdout ? stdout.trim() : '');
    });
  });
}

const server = http.createServer(async (req, res) => {
  const host = req.headers.host || 'localhost';
  const url = new URL(req.url, 'http://' + host);

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // API Endpoint: /api/telemetry
  if (url.pathname === '/api/telemetry' && req.method === 'GET') {
    let batInfo = {};
    try {
      const batRaw = await execPromise('termux-battery-status');
      if (batRaw) batInfo = JSON.parse(batRaw);
    } catch (e) {}

    let openclawStatus = 'offline';
    try {
      const curlOut = await execPromise('curl -s -I http://127.0.0.1:18789/');
      if (curlOut.includes('200 OK')) openclawStatus = 'online';
    } catch (e) {}

    const telemetry = {
      timestamp: new Date().toISOString(),
      battery: {
        percentage: batInfo.percentage || 0,
        status: batInfo.status || 'UNKNOWN',
        plugged: batInfo.plugged || 'UNKNOWN',
        temperature: batInfo.temperature || 0.0,
        health: batInfo.health || 'GOOD'
      },
      openclaw: {
        gatewayUrl: 'http://127.0.0.1:18789/',
        status: openclawStatus,
        model: 'google/gemini-3.5-flash'
      },
      device: {
        model: 'Nothing Phone (2a)',
        arch: 'aarch64',
        os: 'Android 16 (Termux)'
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(telemetry));
    return;
  }

  // API Endpoint: /api/clip
  if (url.pathname === '/api/clip' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body || '{}');
        let textToProcess = payload.text;

        if (!textToProcess) {
          textToProcess = await execPromise('termux-clipboard-get');
        }

        if (!textToProcess || !textToProcess.trim()) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Clipboard is empty' }));
          return;
        }

        const prompt = 'Summarize and format this text clearly for mobile view:\n\n' + textToProcess;
        const cmd = 'openclaw agent --agent main --message ' + JSON.stringify(prompt) + ' 2>&1';
        const rawAiOut = await execPromise(cmd);

        let cleaned = rawAiOut;
        if (rawAiOut.includes('◇')) {
          cleaned = rawAiOut.split('◇').pop().trim();
        }

        // Copy back to clipboard
        await execPromise('echo ' + JSON.stringify(cleaned) + ' | termux-clipboard-set 2>/dev/null || true');
        await execPromise("termux-toast 'Dashboard: Result copied to clipboard!' 2>/dev/null || true");

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          input: textToProcess,
          result: cleaned
        }));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  // Serve Static Files
  let filePath = path.join(PUBLIC_DIR, url.pathname === '/' ? 'index.html' : url.pathname);
  const ext = path.extname(filePath);
  const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml'
  };

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        fs.readFile(path.join(PUBLIC_DIR, 'index.html'), (err2, fallback) => {
          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(fallback);
        });
      } else {
        res.writeHead(500);
        res.end('Server Error: ' + err.code);
      }
    } else {
      res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
      res.end(content);
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('🚀 [Sentinel Dashboard] Server running at http://127.0.0.1:' + PORT + '/');
});
