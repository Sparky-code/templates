// Production server: the API plus the built client (pnpm build first).
import { serve } from '@hono/node-server';
import { serveStatic } from '@hono/node-server/serve-static';
import { Hono } from 'hono';
import api from './app.ts';

const app = new Hono()
  .route('/', api)
  .use('*', serveStatic({ root: './dist/client' }))
  .get('*', serveStatic({ path: './dist/client/index.html' }));

const port = Number(process.env.PORT ?? 3000);
serve({ fetch: app.fetch, port }, (info) => {
  console.log(`listening on http://localhost:${info.port}`);
});
