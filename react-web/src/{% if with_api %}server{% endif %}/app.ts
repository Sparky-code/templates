// The API. In development Vite serves it at /api (see vite.config.ts); in
// production src/server/index.ts serves it with the built client.
import { zValidator } from '@hono/zod-validator';
import { Hono } from 'hono';
import { EchoInput } from '../shared/schemas.ts';

const app = new Hono()
  .basePath('/api')
  .get('/health', (c) => c.json({ status: 'ok' }))
  .post('/echo', zValidator('json', EchoInput), (c) => {
    const { message } = c.req.valid('json');
    return c.json({ message, length: message.length });
  });

export type AppType = typeof app;
export default app;
