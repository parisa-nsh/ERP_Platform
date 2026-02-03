import { mlApi, type MLExportRow } from '../api/client';

const BATCH_SIZE = 10000;
const MAX_ROWS = 100000;

function escapeCsvCell(value: unknown): string {
  if (value == null) return '';
  const s = String(value);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function rowsToCsv(rows: MLExportRow[]): string {
  if (rows.length === 0) return '';
  const headers = Object.keys(rows[0]) as (keyof MLExportRow)[];
  const headerLine = headers.map(escapeCsvCell).join(',');
  const dataLines = rows.map((row) =>
    headers.map((h) => escapeCsvCell((row as unknown as Record<string, unknown>)[h])).join(',')
  );
  return [headerLine, ...dataLines].join('\r\n');
}

/**
 * Fetch ML export (paginated) and trigger CSV download.
 * Stops after MAX_ROWS or when no more pages.
 */
export async function downloadMlExportAsCsv(): Promise<{ rows: number; error?: string }> {
  const rows: MLExportRow[] = [];
  let offset = 0;
  let hasMore = true;

  while (hasMore && rows.length < MAX_ROWS) {
    const limit = Math.min(BATCH_SIZE, MAX_ROWS - rows.length);
    const { data } = await mlApi.export({ offset, limit });
    rows.push(...data.rows);
    hasMore = data.has_more;
    offset += data.rows.length;
    if (data.rows.length === 0) break;
  }

  const csv = rowsToCsv(rows);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `erp_ml_export_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  return { rows: rows.length };
}
