import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { ListRootsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

export async function playwrightClient({webOrigin = 'http://127.0.0.1:8080', apiOrigin = 'http://127.0.0.1:8000'} = {}) {
  if (!['http://127.0.0.1:8080', 'http://127.0.0.1:8081'].includes(webOrigin) ||
      !['http://127.0.0.1:8000', 'http://127.0.0.1:8001'].includes(apiOrigin))
    throw new Error('Browser verification supports only the approved loopback development origins');
  const raw = await readFile(resolve(root, '.tools/node/runtime.json'), 'utf8');
  const runtime = JSON.parse(raw.replace(/^\uFEFF/, ''));
  const transport = new StdioClientTransport({
    command: resolve(runtime.directory, 'node.exe'),
    args: [resolve(root, 'tools/browser/node_modules/@playwright/mcp/cli.js'),
      '--headless', '--isolated', '--browser', 'chrome', '--no-webmcp',
      '--allowed-origins', `${webOrigin};${apiOrigin};https://www.gstatic.com;https://fonts.gstatic.com`,
      '--output-dir', resolve(root, '.tools/artifacts/browser')],
    cwd: root,
    stderr: 'pipe',
  });
  const client = new Client({ name: 'wardrobe-development-verification', version: '1.0.0' },
    { capabilities: { roots: { listChanged: true } } });
  client.setRequestHandler(ListRootsRequestSchema, async () => ({
    roots: [{ uri: pathToFileURL(root).href, name: 'Wardrobe-WIZzz' }],
  }));
  await client.connect(transport);
  return client;
}

export function responseText(result) {
  return (result.content ?? []).filter(item => item.type === 'text').map(item => item.text).join('\n');
}
