import { NextRequest } from 'next/server';
import { createSuccessResponse } from '@/lib/api-response';
import { logStructured } from '@/lib/logger';

export async function GET(request: NextRequest) {
  const correlationId = request.headers.get('x-correlation-id') || `web-${Date.now()}`;

  logStructured('INFO', 'Health check requested', { service: 'web-api', correlationId });

  return createSuccessResponse(
    {
      status: 'HEALTHY',
      service: 'web-api-gateway',
      version: '0.1.0',
      timestamp: new Date().toISOString(),
    },
    correlationId
  );
}
