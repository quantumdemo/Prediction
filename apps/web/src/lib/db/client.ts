/**
 * Web Application Database Access Boundary Helper
 */

import { env } from '@/lib/env';

export interface DatabaseConfig {
  connectionString: string;
  isConfigured: boolean;
}

export function getDatabaseConfig(): DatabaseConfig {
  const connectionString = env.DATABASE_URL;
  return {
    connectionString,
    isConfigured: Boolean(connectionString),
  };
}
