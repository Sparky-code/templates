// zod schemas shared by the API (validation) and the client (types, forms).
import { z } from 'zod';

export const EchoInput = z.object({
  message: z.string().trim().min(1).max(500),
});
export type EchoInput = z.infer<typeof EchoInput>;
