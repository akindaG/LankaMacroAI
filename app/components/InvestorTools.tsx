'use client';
import { useState, type FormEvent } from 'react';
import { ArrowRight, Calculator, Info } from 'lucide-react';
import { api } from '../types';

type Result = { nominal_value: string; real_value: string; real_annual_rate: string; real_gain: string; assumptions: string[]; formula: string };
const money = (value: string) => new Intl.NumberFormat('en-LK', { style: 'currency', currency: 'LKR', maximumFractionDigits: 2 }).format(Number(value));
export default function InvestorTools() {
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function calculate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null);
    const form = new FormData(event.currentTarget);
    try { setResult(await api<Result>('/scenarios/real-return', { principal: form.get('principal'), nominal_rate: form.get('nominal'), inflation_rate: form.get('inflation'), years: Number(form.get('years')) })); }
    catch (e) { setError(e instanceof Error ? e.message : 'Calculation failed.'); }
    finally { setBusy(false); }
  }
  return <><div className="page-heading"><span className="eyebrow">Make assumptions visible</span><h1>What could your savings buy?</h1><p className="muted">Compare a nominal return with its purchasing power after inflation.</p></div>
    <div className="calculator-layout"><section className="panel"><div className="panel-title"><h2><Calculator size={20} /> Real return calculator</h2><span className="badge">LKR</span></div>
      <form className="calculator-form" onSubmit={calculate}>
        <label>Starting amount (LKR)<input name="principal" type="number" min="1" max="1000000000000" step="0.01" required defaultValue="100000" /></label>
        <div className="field-grid"><label>Nominal annual return (%)<input name="nominal" type="number" min="-99" max="100" step="0.0001" required defaultValue="10" /></label><label>Annual inflation assumption (%)<input name="inflation" type="number" min="-99" max="100" step="0.0001" required defaultValue="8" /></label></div>
        <label>Time horizon (years)<input name="years" type="number" min="1" max="30" step="1" required defaultValue="1" /></label>
        <p className="note"><Info size={17} /> Rates are your assumptions. The inflation field is not a forecast.</p>
        <button className="button primary" disabled={busy}>{busy ? 'Calculating…' : 'Calculate purchasing power'} <ArrowRight size={17} /></button>
        {error && <p role="alert" className="error">{error}</p>}
      </form></section>
      <section className="panel result-panel" aria-live="polite"><span className="eyebrow">Your scenario</span>{result ? <><h2>Return in real terms</h2><div className="result-value">{Number(result.real_annual_rate).toFixed(2)}<span>%</span></div><p>Real annual return</p><div className="result-row"><span>Nominal final value</span><strong>{money(result.nominal_value)}</strong></div><div className="result-row"><span>Value in today’s purchasing power</span><strong>{money(result.real_value)}</strong></div><div className="result-row"><span>Real gain / loss</span><strong>{money(result.real_gain)}</strong></div><p className="small formula">{result.formula}</p>{result.assumptions.map(a => <p className="small muted" key={a}>• {a}</p>)}</> : <div className="empty-inline"><Calculator size={36} /><h2>See beyond the nominal return</h2><p>Enter an amount and two annual rate assumptions to compare the outcomes.</p></div>}</section></div>
  </>;
}
