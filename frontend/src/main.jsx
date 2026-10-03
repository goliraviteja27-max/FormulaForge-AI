import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { BookOpen, Moon, Sparkles, Sun } from 'lucide-react'
import UploadBox from './components/UploadBox'
import FormulaCard from './components/FormulaCard'
import ChatPanel from './components/ChatPanel'
import DownloadButtons from './components/DownloadButtons'
import './styles.css'

const API = 'http://localhost:8000/api'

function App() {
  const [dark, setDark] = useState(false)
  const [health, setHealth] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    fetch(`${API}/health`).then((response) => response.json()).then(setHealth).catch(() => setHealth({ online: false }))
  }, [])

  async function analyze(files) {
    setLoading(true); setError(''); setResult(null)
    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    try {
      const response = await fetch(`${API}/analyze`, { method: 'POST', body: form })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Analysis failed.')
      setResult(data)
    } catch (caught) { setError(caught.message) } finally { setLoading(false) }
  }

  return <main className="min-h-screen text-slate-800 dark:text-slate-100">
    <div className="orb orb-one" /><div className="orb orb-two" />
    <header className="mx-auto flex max-w-[1700px] items-center justify-between px-5 py-6 lg:px-10">
      <div className="flex items-center gap-3"><div className="brand-mark"><Sparkles size={21} /></div><div><h1 className="font-display text-xl font-bold tracking-tight">FormulaForge <span>AI</span></h1><p className="text-xs text-slate-500 dark:text-slate-400">Notes into exam-ready formula sheets</p></div></div>
      <div className="flex items-center gap-3"><span className={`hidden rounded-full px-3 py-1 text-xs font-semibold sm:block ${health?.online ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'}`}>{health?.online ? `Ollama ready: ${health.model}` : 'Ollama offline'}</span><button aria-label="Toggle theme" onClick={() => setDark(!dark)} className="icon-button">{dark ? <Sun size={18} /> : <Moon size={18} />}</button></div>
    </header>
    <section className="mx-auto max-w-[1700px] px-5 pb-12 lg:px-10">
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4"><div><p className="eyebrow">STUDY SMARTER</p><h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Turn messy notes into <em>clarity.</em></h2></div>{result && <DownloadButtons sessionId={result.session_id} />}</div>
      {error && <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">{error}</div>}
      <div className="workspace-grid">
        <aside className="space-y-5"><UploadBox onAnalyze={analyze} loading={loading} /><div className="glass-card p-5 text-sm"><div className="mb-3 flex items-center gap-2 font-semibold"><BookOpen size={16} className="text-teal-600" /> How it works</div><ol className="space-y-2 text-slate-500 dark:text-slate-400"><li>1. Drop typed or handwritten notes.</li><li>2. OCR reads each supported file.</li><li>3. AI sorts your formulas by topic.</li></ol></div></aside>
        <section className="glass-panel min-h-[560px] p-5 sm:p-7">{loading ? <LoadingState /> : result ? <FormulaSheet sheet={result.sheet} /> : <EmptySheet />}</section>
        <aside><ChatPanel sessionId={result?.session_id} /></aside>
      </div>
    </section>
  </main>
}

function EmptySheet() { return <div className="flex min-h-[500px] flex-col items-center justify-center text-center"><div className="mb-5 rounded-3xl bg-teal-50 p-5 text-teal-600 dark:bg-teal-950"><Sparkles size={36} /></div><h3 className="font-display text-2xl font-bold">Your formula sheet awaits</h3><p className="mt-2 max-w-sm text-sm leading-6 text-slate-500 dark:text-slate-400">Upload your class notes, revision PDFs, or handwritten pages. We’ll extract only the formulas that matter.</p></div> }
function LoadingState() { return <div className="flex min-h-[500px] flex-col items-center justify-center text-center"><div className="loader" /><h3 className="mt-6 font-display text-xl font-bold">Forging your formula sheet</h3><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Reading notes, spotting formulas, grouping topics...</p></div> }
function FormulaSheet({ sheet }) { return <div><div className="mb-7 flex items-start justify-between gap-4"><div><p className="eyebrow">DETECTED SUBJECT</p><h3 className="font-display text-3xl font-bold">{sheet.subject}</h3></div><span className="rounded-full bg-teal-100 px-3 py-1.5 text-xs font-bold text-teal-700 dark:bg-teal-950 dark:text-teal-300">{sheet.topics.reduce((sum, topic) => sum + topic.formulas.length, 0)} formulas</span></div><div className="space-y-5">{sheet.topics.map((topic) => <Topic key={topic.topic_name} topic={topic} />)}</div>{sheet.important_formulas?.length > 0 && <section className="mt-9"><div className="mb-4"><p className="eyebrow">HIGH PRIORITY</p><h4 className="font-display text-2xl font-bold">Most Frequently Used Formulae</h4></div><div className="grid gap-3 xl:grid-cols-2">{sheet.important_formulas.map((formula, index) => <FormulaCard key={`${formula.formula}-${index}`} formula={formula} important />)}</div></section>}</div> }
function Topic({ topic }) { const [open, setOpen] = useState(true); return <section className="topic"><button onClick={() => setOpen(!open)} className="topic-header"><span>{topic.topic_name}</span><span className="text-lg">{open ? '−' : '+'}</span></button>{open && <div className="grid gap-3 pt-3 xl:grid-cols-2">{topic.formulas.map((formula, index) => <FormulaCard key={`${formula.formula}-${index}`} formula={formula} />)}</div>}</section> }
createRoot(document.getElementById('root')).render(<App />)
