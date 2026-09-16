import { NextResponse } from 'next/server';
import { ErrorCode, StructuredErrorResponse, StructuredSuccessResponse } from '@football-ai/contracts';

export function createSuccessResponse<T>(
  data: T,
  correlationId: string = 'N/A',
  status: number = 200
): NextResponse<StructuredSuccessResponse<T>> {
  return NextResponse.json(
    {
      success: true,
      data,
      timestampUtc: new Date().toISOString(),
      correlationId,
    },
    {
      status,
      headers: {
        'x-correlation-id': correlationId,
        'Content-Type': 'application/json',
      },
    }
  );
}

export function createErrorResponse(
  code: ErrorCode,
  message: string,
  correlationId: string = 'N/A',
  status: number = 400,
  details?: Array<{ field?: string; message: string; location?: string }>
): NextResponse<StructuredErrorResponse> {
  return NextResponse.json(
    {
      success: false,
      error: {
        code,
        message,
        details,
      },
      timestampUtc: new Date().toISOString(),
      correlationId,
    },
    {
      status,
      headers: {
        'x-correlation-id': correlationId,
        'Content-Type': 'application/json',
      },
    }
  );
}
