import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { root, playwrightClient, responseText } from './mcp_client.mjs';

const report = { verifiedAt: new Date().toISOString(), scope: 'tooling only; no application URLs or data' };
let browser;
try {
  browser = await playwrightClient();
  const tools = await browser.listTools();
  const navigation = await browser.callTool({ name: 'browser_navigate', arguments: { url: 'about:blank' } });
  if (navigation.isError) throw new Error('Isolated blank-page browser launch failed');
  const snapshot = await browser.callTool({ name: 'browser_snapshot', arguments: {} });
  if (snapshot.isError) throw new Error('Blank-page accessibility snapshot failed');
  report.playwright = { connected: true, toolCount: tools.tools.length,
    browserNavigationAvailable: tools.tools.some(tool => tool.name === 'browser_navigate'),
    isolatedChromeLaunchSucceeded: true, blankPageSnapshotSucceeded: true };
} catch (error) {
  report.playwright = { connected: false, error: String(error.message).slice(0, 200) };
} finally { await browser?.close(); }

const docs = new Client({ name: 'wardrobe-docs-verification', version: '1.0.0' }, { capabilities: {} });
try {
  await docs.connect(new StreamableHTTPClientTransport(new URL('https://mcp.context7.com/mcp')));
  const tools = await docs.listTools();
  const result = await docs.callTool({ name: 'resolve-library-id',
    arguments: { libraryName: 'FastAPI', query: 'SQLAlchemy database sessions and yield dependencies' } });
  const lookup = responseText(result);
  const libraryId = lookup.match(/Context7-compatible library ID:\s*(\/[^\s]+)/i)?.[1];
  if (result.isError || !libraryId) throw new Error('FastAPI library lookup returned no usable library ID');
  const documentation = await docs.callTool({ name: 'query-docs', arguments: {
    libraryId, query: 'How should FastAPI dependencies with yield close a database session?'
  } });
  if (documentation.isError || responseText(documentation).length < 100)
    throw new Error('Context7 documentation query did not return usable text');
  report.context7 = { connected: true, tools: tools.tools.map(tool => tool.name),
    anonymousLookupSucceeded: true, documentationQuerySucceeded: true, libraryId,
    credentialsCreated: false };
} catch (error) {
  report.context7 = { connected: false, error: String(error.message).slice(0, 200), credentialsCreated: false };
} finally { await docs.close(); }

await mkdir(resolve(root, '.tools/artifacts'), { recursive: true });
await writeFile(resolve(root, '.tools/artifacts/mcp-verification.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
if (!report.playwright?.isolatedChromeLaunchSucceeded || !report.context7?.documentationQuerySucceeded)
  process.exitCode = 1;
