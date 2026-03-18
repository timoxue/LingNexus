#!/usr/bin/env node
/**
 * Claude Code 代理服务器
 * 将 OpenClaw 的 x-api-key 头转换为 claude-code.club 要求的 Bearer 令牌格式
 *
 * 优化：
 * - 并发请求支持（无状态设计）
 * - 429 错误处理（速率限制）
 * - 指数退避重试机制
 * - 热更新 API Key（POST /admin/key，无需重启容器）
 */

const http = require('http');
const https = require('https');
const fs = require('fs');

const PROXY_PORT = 18790;
const TARGET_HOST = 'claude-code.club';
const TARGET_BASE = '/api';
const KEY_FILE = '/app/key-override.txt';

// 热更新 Key（优先级高于请求头中的 x-api-key）
let keyOverride = null;

// 启动时从文件加载持久化的 key
try {
  const saved = fs.readFileSync(KEY_FILE, 'utf8').trim();
  if (saved) {
    keyOverride = saved;
    console.log(`🔑 Loaded key override from ${KEY_FILE}: ${saved.slice(0, 8)}...`);
  }
} catch (_) {
  // 文件不存在时忽略
}

// 重试配置
const MAX_RETRIES = 3;
const INITIAL_BACKOFF_MS = 1000;  // 1 秒

// 流式超时：两次 chunk 之间最大空闲时间（上游慢时主动断开）
const STREAM_IDLE_TIMEOUT_MS = 30000;  // 30 秒无数据则断开

console.log('='.repeat(60));
console.log(' Claude Code Proxy Server (Enhanced)');
console.log('='.repeat(60));
console.log(`Listening on: http://localhost:${PROXY_PORT}`);
console.log(`Forwarding to: https://${TARGET_HOST}${TARGET_BASE}`);
console.log('');
console.log('Features:');
console.log('  - Header conversion: x-api-key → Authorization: Bearer');
console.log('  - Concurrent request support (stateless)');
console.log('  - 429 rate limit handling with exponential backoff');
console.log('  - Stream idle timeout: ' + STREAM_IDLE_TIMEOUT_MS + 'ms');
console.log('  - Max retries: ' + MAX_RETRIES);
console.log('='.repeat(60));

/**
 * 指数退避重试
 */
async function makeRequestWithRetry(options, reqBody, retryCount = 0) {
  return new Promise((resolve, reject) => {
    const proxyReq = https.request(options, (proxyRes) => {
      // 检查 429 错误
      if (proxyRes.statusCode === 429 && retryCount < MAX_RETRIES) {
        const backoffMs = INITIAL_BACKOFF_MS * Math.pow(2, retryCount);
        console.log(`  ⚠️  Rate limited (429), retrying in ${backoffMs}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`);

        // 消费响应体以释放连接
        proxyRes.resume();

        setTimeout(() => {
          makeRequestWithRetry(options, reqBody, retryCount + 1)
            .then(resolve)
            .catch(reject);
        }, backoffMs);
        return;
      }

      resolve(proxyRes);
    });

    proxyReq.on('error', (err) => {
      if (retryCount < MAX_RETRIES) {
        const backoffMs = INITIAL_BACKOFF_MS * Math.pow(2, retryCount);
        console.log(`  ⚠️  Request error: ${err.message}, retrying in ${backoffMs}ms`);

        setTimeout(() => {
          makeRequestWithRetry(options, reqBody, retryCount + 1)
            .then(resolve)
            .catch(reject);
        }, backoffMs);
      } else {
        reject(err);
      }
    });

    if (reqBody) {
      proxyReq.write(reqBody);
    }
    proxyReq.end();
  });
}

const server = http.createServer(async (req, res) => {
  // ── 管理端点：更新 Key ─────────────────────────────────────────
  if (req.url === '/admin/key' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const { key } = JSON.parse(body);
        if (!key || typeof key !== 'string' || !key.trim()) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Missing or invalid "key" field' }));
          return;
        }
        keyOverride = key.trim();
        fs.writeFileSync(KEY_FILE, keyOverride, 'utf8');
        console.log(`[${new Date().toISOString()}] 🔑 Key updated: ${keyOverride.slice(0, 8)}...`);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true, key_prefix: keyOverride.slice(0, 8) + '...' }));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON body' }));
      }
    });
    return;
  }

  // ── 管理端点：查看当前 Key 状态 ───────────────────────────────
  if (req.url === '/admin/key' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      key_override: keyOverride ? keyOverride.slice(0, 8) + '...' : null,
      source: keyOverride ? 'override' : 'per-request (x-api-key header)'
    }));
    return;
  }

  const startTime = Date.now();
  const requestId = Math.random().toString(36).substring(7);

  // 优先使用热更新的 key，否则从请求头取
  const apiKey = keyOverride || req.headers['x-api-key'];

  if (!apiKey) {
    console.error(`[${new Date().toISOString()}] [${requestId}] ❌ Missing x-api-key header (no override set)`);
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Missing x-api-key header. Set a key via POST /admin/key' }));
    return;
  }

  // 收集请求体
  let reqBody = '';
  req.on('data', chunk => {
    reqBody += chunk.toString();
  });

  req.on('end', async () => {
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
        'authorization': `Bearer ${apiKey}`,
        'content-length': Buffer.byteLength(reqBody)
      }
    };

    // 删除 x-api-key 头
    delete options.headers['x-api-key'];

    console.log(`[${new Date().toISOString()}] [${requestId}] ${req.method} ${targetPath}`);

    try {
      const proxyRes = await makeRequestWithRetry(options, reqBody);
      const firstByteTime = Date.now() - startTime;

      console.log(`  [${requestId}] ← ${proxyRes.statusCode} (TTFB: ${firstByteTime}ms)`);

      res.writeHead(proxyRes.statusCode, proxyRes.headers);

      // 流式超时检测：手动转发 chunk，监控空闲时间
      let idleTimer = null;
      let totalBytes = 0;
      let streamAborted = false;

      const resetIdleTimer = () => {
        if (idleTimer) clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
          if (!streamAborted) {
            streamAborted = true;
            console.error(`  [${requestId}] ⏱️  Stream idle timeout (${STREAM_IDLE_TIMEOUT_MS}ms), aborting`);
            proxyRes.destroy();
            res.destroy();
          }
        }, STREAM_IDLE_TIMEOUT_MS);
      };

      resetIdleTimer();  // 启动初始 timer

      proxyRes.on('data', (chunk) => {
        totalBytes += chunk.length;
        resetIdleTimer();  // 每次收到数据重置 timer
        if (!res.destroyed) {
          res.write(chunk);
        }
      });

      proxyRes.on('end', () => {
        if (idleTimer) clearTimeout(idleTimer);
        const totalDuration = Date.now() - startTime;
        console.log(`  [${requestId}] ✓ Stream complete (${totalBytes} bytes, ${totalDuration}ms total)`);
        if (!res.destroyed) {
          res.end();
        }
      });

      proxyRes.on('error', (err) => {
        if (idleTimer) clearTimeout(idleTimer);
        console.error(`  [${requestId}] ❌ Stream error: ${err.message}`);
        if (!res.destroyed) {
          res.destroy();
        }
      });
    } catch (err) {
      console.error(`  [${requestId}] ❌ Proxy error after ${MAX_RETRIES} retries: ${err.message}`);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: 'Proxy error',
        details: err.message,
        retries: MAX_RETRIES
      }));
    }
  });
});

server.listen(PROXY_PORT, () => {
  console.log(`\n✅ Proxy server running on port ${PROXY_PORT}\n`);
});
