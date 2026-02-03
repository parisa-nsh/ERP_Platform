/**
 * Normalize API error detail to a string.
 * FastAPI can return detail as string or array of { type, loc, msg, ... }.
 * Check response.data.detail first (Axios errors are also instanceof Error).
 */
export function getApiErrorMessage(err: unknown, fallback = 'Request failed'): string {
  const axErr = err as { response?: { data?: { detail?: unknown }; status?: number } };
  const detail = axErr.response?.data?.detail;
  if (detail != null) {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      return first.msg ?? JSON.stringify(first);
    }
    if (typeof detail === 'object' && 'msg' in detail) {
      return String((detail as { msg: string }).msg);
    }
  }
  if (err instanceof Error) return err.message;
  return fallback;
}
