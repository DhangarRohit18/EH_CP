/**
 * WebGuard Extension Manifest V3 Build Script
 * Bundles TypeScript sources into extension/dist using esbuild
 */

import * as esbuild from 'esbuild';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const outDir = path.resolve(__dirname, 'dist');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

async function buildExtension() {
  console.log('[WebGuard Extension Build] Compiling Manifest V3 bundle...');

  try {
    // 1. Compile Service Worker
    await esbuild.build({
      entryPoints: [path.resolve(__dirname, 'src/background/service-worker.ts')],
      outfile: path.resolve(outDir, 'background/service-worker.js'),
      bundle: true,
      format: 'esm',
      target: 'es2022',
      platform: 'browser',
      minify: false,
      sourcemap: true,
    });

    // 2. Compile Content Script
    await esbuild.build({
      entryPoints: [path.resolve(__dirname, 'src/content/content.ts')],
      outfile: path.resolve(outDir, 'content/content.js'),
      bundle: true,
      format: 'iife',
      target: 'es2022',
      platform: 'browser',
      minify: false,
      sourcemap: true,
    });

    // 3. Compile Popup JS & HTML
    const popupDir = path.resolve(outDir, 'popup');
    if (!fs.existsSync(popupDir)) {
      fs.mkdirSync(popupDir, { recursive: true });
    }

    await esbuild.build({
      entryPoints: [path.resolve(__dirname, 'src/popup/App.tsx')],
      outfile: path.resolve(popupDir, 'index.js'),
      bundle: true,
      format: 'esm',
      target: 'es2022',
      platform: 'browser',
      jsx: 'automatic',
      minify: false,
      sourcemap: true,
    });

    // Write popup HTML
    const popupHtml = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>WebGuard Assessment</title>
    <style>
      body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; }
      #root { width: 360px; min-height: 480px; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="./index.js"></script>
  </body>
</html>`;
    fs.writeFileSync(path.resolve(popupDir, 'index.html'), popupHtml, 'utf-8');

    console.log('[WebGuard Extension Build] Successfully compiled extension/dist!');
  } catch (err) {
    console.error('[WebGuard Extension Build] Compilation error:', err);
    process.exit(1);
  }
}

buildExtension();
