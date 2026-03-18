#!/usr/bin/env node
/**
 * Claude Code 代理服务器
 * 将 OpenClaw 的 x-api-key 头转换为 claude-code.club 要求的 Bearer 令牌格式
 */

const http = require('http');
const https = require('https');

const PROXY_PORT = 18790;
const TARGET_HOST = 'claude-code.club';
const TARGET_BASE = '/api';

console.log('='.repeat(60));
console.log(' Claude Code Proxy Server');
console.log('='.repeat(60));
console.log(`Listening on: http://localhost:${PROXY_PORT}`);
console.log(`Forwarding to: https://${TARGET_HOST}${TARGET_BASE}`);
console.log('');
console.log('Header conversion:');
console.log('  x-api-key: cr_xxx  →  Authorization: Bearer cr_xxx');
console.log('='.repeat(60));

const server = http.createServer((req, res) => {
  const startTime = Date.now();

  // 提取 x-api-key 并转换为 Bearer token
  const apiKey = req.headers['x-api-key'];

  if (!apiKey) {
    console.error(`[${new Date().toISOString()}] ❌ Missing x-api-key header`);
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Missing x-api-key header' }));
    return;
  }

  // 构建目标请求
  const targetPath = req.url;
  const options = {
    hostname: TARGET_HOST,
    port: 443,
    path: `${TARGET_BASE}${targetPath}`,
    method: req.method,
    rejectUnauthorized: false,
    headers: {
      ...req.headers,
      'host': TARGET_HOST,
      'authorization': `Bearer ${apiKey}`
    }
  };

  // 删除 x-api-key 头
  delete options.headers['x-api-key'];

  console.log(`[${new Date().toISOString()}] ${req.method} ${targetPath}`);

  const proxyReq = https.request(options, (proxyRes) => {
    const duration = Date.now() - startTime;
    console.log(`  ← ${proxyRes.statusCode} (${duration}ms)`);

    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error(`  ❌ Proxy error: ${err.message}`);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Proxy error', details: err.message }));
  });

  req.pipe(proxyReq);
});

server.listen(PROXY_PORT, () => {
  console.log(`\n✅ Proxy server running on port ${PROXY_PORT}\n`);
});
