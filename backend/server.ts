/**
 * WebGuard Full-Stack Dev Server & Canonical API Proxy
 * 
 * ARCHITECTURE PRINCIPLE (SINGLE SOURCE OF TRUTH):
 * All analysis scoring, ML inference, and database persistence are handled
 * exclusively by the canonical FastAPI backend (http://127.0.0.1:8000).
 * 
 * Express serves the compiled frontend assets and proxies /api/v1 requests
 * directly to FastAPI to prevent duplicate scoring engines or split persistence.
 */

import express, { Request, Response } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const FASTAPI_TARGET = process.env.FASTAPI_TARGET || 'http://127.0.0.1:8001';

app.use(express.json());

// ============================================================================
// Transparent Reverse-Proxy to Canonical FastAPI Service
// ============================================================================
function proxyToFastAPI(req: Request, res: Response) {
  const targetUrl = new URL(req.originalUrl, FASTAPI_TARGET);

  const proxyReq = http.request(
    targetUrl.toString(),
    {
      method: req.method,
      headers: {
        ...req.headers,
        host: targetUrl.host,
      },
    },
    proxyRes => {
      res.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
      proxyRes.pipe(res);
    }
  );

  proxyReq.on('error', err => {
    res.status(503).json({
      error: 'Canonical FastAPI Backend Unavailable',
      detail: `Could not reach ${FASTAPI_TARGET}. Ensure FastAPI is running via 'npm run dev:python'`,
      system: 'WebGuard Reverse Proxy',
      internal_error: err.message,
    });
  });

  if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
    const bodyData = JSON.stringify(req.body);
    proxyReq.setHeader('Content-Type', 'application/json');
    proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
    proxyReq.write(bodyData);
  }

  proxyReq.end();
}

// Route all /api/v1/*, /api/*, and /health to Canonical FastAPI
app.use(['/api/v1', '/api', '/health'], (req: Request, res: Response) => {
  proxyToFastAPI(req, res);
});

// ============================================================================
// Static Frontend & Vite Integration
// ============================================================================
async function startServer() {
  const isProd = process.env.NODE_ENV === 'production';

  if (!isProd) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      configFile: path.resolve(__dirname, '../frontend/vite.config.ts'),
      root: path.resolve(__dirname, '../frontend'),
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.resolve(__dirname, '../dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.resolve(distPath, 'index.html'));
    });
  }

  app.listen(Number(PORT), '0.0.0.0', () => {
    console.log(`[WebGuard Frontend Host] Running on http://localhost:${PORT}`);
    console.log(`[WebGuard API Forwarder] Proxying /api/v1 -> ${FASTAPI_TARGET}/api/v1`);
  });
}

startServer();
