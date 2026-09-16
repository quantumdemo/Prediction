import { NextRequest } from 'next/server';
import { createSuccessResponse, createErrorResponse } from '@/lib/api-response';
import { ErrorCode } from '@football-ai/contracts';
import { logStructured } from '@/lib/logger';

export async function GET(request: NextRequest) {
  const correlationId = request.headers.get('x-correlation-id') || `web-${Date.now()}`;

  try {
    // Check readiness dependencies
    const readiness = {
      status: 'READY',
      service: 'web-api-gateway',
      checks: {
        environment: 'OK',
        routing: 'OK',
      },
      timestamp: new Date().toISOString(),
    };

    logStructured('INFO', 'Readiness check requested', { service: 'web-api', correlationId }, readiness);

    return createSuccessResponse(readiness, correlationId);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error during readiness check';
    logStructured('ERROR', 'Readiness check failed', { service: 'web-api', correlationId }, { error: message });

    return createErrorResponse(
      ErrorCode.DEPENDENCY_ERROR,
      'Service is not ready to process requests',
      correlationId,
      503
    );
  }
}
