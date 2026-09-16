/**
 * Environment Variable Validation and Management
 */

export const env = {
  // Server-only environment variables
  NODE_ENV: process.env.NODE_ENV || 'development',
  DATABASE_URL: process.env.DATABASE_URL || '',
  FASTAPI_SERVICE_URL: process.env.FASTAPI_SERVICE_URL || 'http://localhost:8000',
  API_FOOTBALL_KEY: process.env.API_FOOTBALL_KEY || '',
  MODAL_TOKEN: process.env.MODAL_TOKEN || '',

  // Client-exposed environment variables
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
};

export function validateServerEnv(): { valid: boolean; missing: string[] } {
  const missing: string[] = [];
  // For Stage 3 application skeleton, check required base variables
  if (!process.env.DATABASE_URL) missing.push('DATABASE_URL');
  return {
    valid: missing.length === 0,
    missing,
  };
}
