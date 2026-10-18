'use client';
import { useEffect, useRef } from 'react';
import { ExternalLink, X, FileText } from 'lucide-react';
import type { Source } from '../types';

export default function SourceDialog({ source, close }: { source: Source; close: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { const dialog = ref.current; dialog?.showModal(); return () => dialog?.close(); }, []);
  return <dialog ref={ref} className="source-dialog" onCancel={close} onClick={e => { if (e.target === ref.current) close(); }} aria-labelledby="source-title">
    <div className="dialog-header"><div><span className="eyebrow"><FileText size={15} /> Reviewed primary source</span><h2 id="source-title">{source.title}</h2></div><button autoFocus className="icon-button" aria-label="Close source viewer" onClick={close}><X /></button></div>
    <p className="muted">{source.publisher} · Released {source.release_date} · Page {source.page}</p>
    <p className="small">{source.table}</p>
    <div className="source-links"><a className="button secondary" href={`${source.pdf_url}#page=${source.page}`} target="_blank" rel="noreferrer">Open archived PDF <ExternalLink size={15} /></a><a href={source.url} target="_blank" rel="noreferrer">Original publication <ExternalLink size={14} /></a></div>
    <iframe title="Original DCS CCPI PDF, page 4" src={`${source.pdf_url}#page=${source.page}`} />
    <details><summary>Review and file integrity</summary><p className="small">Visually checked on {source.reviewed_on}. Original PDF preserved with SHA-256:</p><code className="hash">{source.sha256}</code></details>
  </dialog>;
}
