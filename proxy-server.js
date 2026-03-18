#!/usr/bin/env node
/**
 * Claude Code 代理服务器
 * 将 OpenClaw 的 x-api-key 头转换为 claude-code.club 要求的 Bearer 令牌格式
 *
 * 优化：
 * - 并发请求支持（无状态设计）
 * - 429 错误处理（速率限制）
 * - 指数退避重试机制
 */

const http = require('http');
const https = require('https');

const PROXY_PORT = 18790;
const TARGET_HOST = 'claude-code.club';
const TARGET_BASE = '/api';

// 重试配置
const MAX_RETRIES = 3;
const INITIAL_BACKOFF_MS = 1000;  // 1 秒

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
  const startTime = Date.now();
  const requestId = Math.random().toString(36).substring(7);

  // 提取 x-api-key 并转换为 Bearer token
  const apiKey = req.headers['x-api-key'];

  if (!apiKey) {
    console.error(`[${new Date().toISOString()}] [${requestId}] ❌ Missing x-api-key header`);
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Missing x-api-key header' }));
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
      const duration = Date.now() - startTime;

      console.log(`  [${requestId}] ← ${proxyRes.statusCode} (${duration}ms)`);

      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
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
