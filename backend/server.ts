import express, { Request, Response } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { analyzePayload } from '../frontend/src/engine/riskEngine';
import { DEMO_TEST_CASES } from '../frontend/src/engine/testCases';
import { AnalysisPayload, AnalysisResult } from '../frontend/src/types';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// In-memory persistent history store (seeded with the 5 test vectors)
const historyStore: AnalysisResult[] = DEMO_TEST_CASES.map(tc => analyzePayload(tc.data));

// ==========================================
// REST API v1 Routes
// ==========================================

// Health Check
app.get('/api/v1/health', (_req: Request, res: Response) => {
  res.json({
    status: 'online',
    service: 'WebGuard E-Commerce Fraud Risk Engine',
    timestamp: new Date().toISOString(),
    weights: {
      domain: 0.20,
      price: 0.20,
      reviews: 0.15,
      identity: 0.15,
      policy: 0.10,
      payment: 0.10,
      behaviour: 0.10,
      total: 1.00
    },
    ml_models: {
      isolation_forest: 'active',
      nlp_similarity: 'active'
    }
  });
});

// Analyze Storefront
app.post('/api/v1/analyze', (req: Request, res: Response) => {
  try {
    const payload: AnalysisPayload = req.body;
    if (!payload.url && !payload.domain) {
      return res.status(400).json({ error: 'URL or domain is required.' });
    }

    const result = analyzePayload(payload);
    // Prepend to history
    historyStore.unshift(result);
    // Keep max 100 items
    if (historyStore.length > 100) historyStore.pop();

    return res.json(result);
  } catch (err: any) {
    console.error('[WebGuard Server Error]', err);
    return res.status(500).json({ error: 'Internal risk engine error', details: err?.message });
  }
});

// History List
app.get('/api/v1/history', (req: Request, res: Response) => {
  const riskLevel = req.query.risk_level as string;
  const domain = req.query.domain as string;

  let items = [...historyStore];
  if (riskLevel) {
    items = items.filter(i => i.riskLevel.toUpperCase() === riskLevel.toUpperCase());
  }
  if (domain) {
    items = items.filter(i => i.domain.toLowerCase().includes(domain.toLowerCase()));
  }

  res.json(items);
});

// History Single Item
app.get('/api/v1/history/:id', (req: Request, res: Response) => {
  const item = historyStore.find(i => i.id === req.params.id);
  if (!item) {
    return res.status(404).json({ error: 'Analysis record not found' });
  }
  res.json(item);
});

// Clear history
app.delete('/api/v1/history', (_req: Request, res: Response) => {
  historyStore.length = 0;
  res.json({ message: 'History cleared' });
});

// ==========================================
// Vite / Static Middleware Mount
// ==========================================
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
    console.log(`[WebGuard Server] Running on http://localhost:${PORT}`);
  });
}

startServer();
