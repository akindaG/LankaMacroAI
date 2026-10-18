export type SeriesKey = 'headline' | 'food' | 'non_food' | 'index';
export type Row = { period: string; headline: number; food: number; non_food: number; index: number };
export type Source = {
  id: string; title: string; publisher: string; url: string; release_date: string;
  reviewed_on: string; page: number; table: string; sha256: string; pdf_url: string;
};
export type SeriesData = { rows: Row[]; source: Source; units: Record<SeriesKey, string> };
export type Evidence = { id: string; title: string; text: string; page: number };
export type Answer = {
  status: 'answered' | 'insufficient_evidence'; answer: string; citations: Source[];
  chart: { rows: Row[]; series: SeriesKey[]; unit: string } | null; mode: string;
};
export type SavedItem = { id: string; title: string; savedAt: string; answer?: Answer; chart?: Answer['chart'] };
export const LABELS: Record<SeriesKey, string> = { headline: 'Headline', food: 'Food', non_food: 'Non-food', index: 'CCPI index' };
export const COLORS: Record<SeriesKey, string> = { headline: '#087d77', food: '#c98b25', non_food: '#6476bc', index: '#087d77' };
export function month(period: string) {
  return new Date(`${period}-01T00:00:00Z`).toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
}
export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(20000) } : { signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(response.status === 422 ? 'Please check your inputs and the available period.' : `Request failed (${response.status}). Check that the evidence API is running.`);
  return response.json() as Promise<T>;
}
