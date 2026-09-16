/**
 * Structured Logging Foundation
 */

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

export interface LogContext {
  service: string;
  environment: string;
  correlationId?: string;
  eventType?: string;
  [key: string]: unknown;
}

const REDACT_KEYS = ['password', 'secret', 'token', 'authorization', 'api_key', 'apikey', 'key'];

function sanitizeMetadata(data: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  for (const [key, val] of Object.entries(data)) {
    if (REDACT_KEYS.some((k) => key.toLowerCase().includes(k))) {
      sanitized[key] = '[REDACTED]';
    } else if (typeof val === 'object' && val !== null) {
      sanitized[key] = sanitizeMetadata(val as Record<string, unknown>);
    } else {
      sanitized[key] = val;
    }
  }
  return sanitized;
}

export function logStructured(
  level: LogLevel,
  message: string,
  context: Partial<LogContext> = {},
  metadata: Record<string, unknown> = {}
): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    service: context.service || 'web',
    environment: context.environment || process.env.NODE_ENV || 'development',
    correlationId: context.correlationId || 'N/A',
    eventType: context.eventType || 'GENERAL',
    meta: sanitizeMetadata(metadata),
  };

  const formatted = JSON.stringify(logEntry);

  switch (level) {
    case 'ERROR':
      console.error(formatted);
      break;
    case 'WARN':
      console.warn(formatted);
      break;
    case 'INFO':
    default:
      console.log(formatted);
      break;
  }
}
