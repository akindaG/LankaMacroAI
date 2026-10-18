'use client';
import { useState } from 'react';
import { CartesianGrid, Line, LineChart, Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Table2, ChartNoAxesCombined } from 'lucide-react';
import { COLORS, LABELS, month, type Row, type SeriesKey } from '../types';

export default function EvidenceChart({ rows, series = ['headline', 'food', 'non_food'], compact = false }: { rows: Row[]; series?: SeriesKey[]; compact?: boolean }) {
  const [table, setTable] = useState(false);
  const [style, setStyle] = useState('line');
  const index = series.includes('index');
  const unit = index ? 'Index points · 2021=100' : 'Inflation · % year-on-year';
  const chartProps = { data: rows, margin: { top: 12, right: 12, bottom: 8, left: -14 } };
  const axes = <><CartesianGrid stroke="#e6edec" strokeDasharray="3 4" vertical={false} /><XAxis dataKey="period" tickFormatter={v => month(v)} tickLine={false} axisLine={false} fontSize={11} minTickGap={35} /><YAxis tickLine={false} axisLine={false} fontSize={11} width={54} domain={index ? ['auto', 'auto'] : ['auto', 'auto']} /><Tooltip labelFormatter={label => month(String(label))} contentStyle={{ borderRadius: 12, borderColor: '#dce8e5', fontSize: 13 }} /></>;
  return <div className="evidence-chart">
    <div className="chart-controls"><span className="muted small">{unit}</span><div className="segmented">
      {!compact && <select aria-label="Chart type" value={style} onChange={e => setStyle(e.target.value)}><option value="line">Line</option><option value="bar">Bars</option></select>}
      <button className={!table ? 'selected' : ''} aria-label="Show chart" aria-pressed={!table} onClick={() => setTable(false)}><ChartNoAxesCombined size={15} /></button>
      <button className={table ? 'selected' : ''} aria-label="Show data table" aria-pressed={table} onClick={() => setTable(true)}><Table2 size={15} /></button>
    </div></div>
    {table ? <div className="table-scroll"><table><caption className="sr-only">CCPI observations. {unit}.</caption><thead><tr><th scope="col">Month</th>{series.map(key => <th key={key} scope="col">{LABELS[key]} {index ? '(index)' : '(%)'}</th>)}</tr></thead><tbody>{rows.map(row => <tr key={row.period}><th scope="row">{month(row.period)}</th>{series.map(key => <td key={key}>{row[key].toFixed(1)}</td>)}</tr>)}</tbody></table></div>
    : <div className={compact ? 'chart-canvas compact' : 'chart-canvas'} role="img" aria-label={`${series.map(key => LABELS[key]).join(', ')} chart, ${rows.length} monthly observations. Use the data table for exact values.`}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        {style === 'bar' ? <BarChart {...chartProps}>{axes}{series.map(key => <Bar key={key} dataKey={key} name={LABELS[key]} fill={COLORS[key]} radius={[3, 3, 0, 0]} isAnimationActive={false} />)}</BarChart>
        : <LineChart {...chartProps}>{axes}{series.map(key => <Line key={key} dataKey={key} name={LABELS[key]} stroke={COLORS[key]} strokeWidth={key === 'headline' || key === 'index' ? 3 : 2} dot={rows.length < 3} activeDot={{ r: 5 }} type="linear" isAnimationActive={false} />)}</LineChart>}
      </ResponsiveContainer>
    </div>}
    <div className="legend">{series.map(key => <span key={key}><i style={{ background: COLORS[key] }} />{LABELS[key]}</span>)}</div>
  </div>;
}
