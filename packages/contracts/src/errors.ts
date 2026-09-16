import { ErrorCode } from './enums.js';

export interface StructuredErrorDetail {
  field?: string;
  message: string;
  location?: string;
}

export interface StructuredErrorResponse {
  success: false;
  error: {
    code: ErrorCode;
    message: string;
    details?: StructuredErrorDetail[];
  };
  timestampUtc: string;
  correlationId: string;
}

export interface StructuredSuccessResponse<T> {
  success: true;
  data: T;
  timestampUtc: string;
  correlationId: string;
}
