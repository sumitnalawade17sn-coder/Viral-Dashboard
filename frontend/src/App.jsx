import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { fetchAnalysis, fetchContent, fetchRecommendations, fetchSearches, fetchSummary, saveSearch } from './api'

function App() {
  const [summary, setSummary] = useState(null)
  const [content, setContent] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [saved, setSaved] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({ hashtag: '', creator: '', format: '', min_views: '' })
  const [form, setForm] = useState({ name: '', hashtags: '', competitors: '', niche: '' })

  async function loadData() {
    try {
      setLoading(true)
      setError('')
      const [s, c, a, r, searches] = await Promise.all([
        fetchSummary(),
        fetchContent({}),
        fetchAnalysis(),
        fetchRecommendations(),
        fetchSearches()
      ])
      setSummary(s)
      setContent(c)
      setAnalysis(a)
      setRecommendations(r)
      setSaved(searches)
    } catch (e) {
      setError('Could not load dashboard data. Make sure backend is running on http://localhost:8000.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const filteredPayload = useMemo(() => ({
    ...filters,
    min_views: filters.min_views ? Number(filters.min_views) : undefined
  }), [filters])

  const applyFilters = async () => {
    try {
      setContent(await fetchContent(filteredPayload))
    } catch {
      setError('Failed to fetch filtered content.')
    }
  }

  const handleSaveSearch = async (e) => {
    e.preventDefault()
    try {
      await saveSearch({
        name: form.name,
        hashtags: form.hashtags.split(',').map(s => s.trim()).filter(Boolean),
        competitors: form.competitors.split(',').map(s => s.trim()).filter(Boolean),
        niche: form.niche
      })
      setForm({ name: '', hashtags: '', competitors: '', niche: '' })
      setSaved(await fetchSearches())
    } catch {
      setError('Could not save search. Try a unique search name.')
    }
  }

  return <div className="page">
    <header className="hero">
      <div>
        <h1>Viral Dashboard</h1>
        <p>Agency-grade Instagram trend intelligence (mock-data first, API-ready).</p>
      </div>
      <button onClick={loadData}>Refresh Data</button>
    </header>

    {error && <section className="alert">{error}</section>}
    {loading && <section className="panel">Loading dashboard...</section>}

    {!loading && summary && <section className="kpi-grid">
      <Card title="Total Posts" value={summary.total_posts} />
      <Card title="Avg Engagement" value={`${summary.average_engagement_rate}%`} />
      <Card title="Top Format" value={summary.top_format} />
      <Card title="Best Posting Time" value={summary.best_posting_time} />
      <Card title="Top Viral Hooks" value={summary.top_viral_hooks.slice(0, 2).join(' • ')} />
    </section>}

    <section className="panel glass">
      <h2>Research Input</h2>
      <form className="form-grid" onSubmit={handleSaveSearch}>
        <input placeholder="Search name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Hashtags (comma separated)" value={form.hashtags} onChange={e => setForm({ ...form, hashtags: e.target.value })} />
        <input placeholder="Competitor usernames" value={form.competitors} onChange={e => setForm({ ...form, competitors: e.target.value })} />
        <input placeholder="Niche/category" value={form.niche} onChange={e => setForm({ ...form, niche: e.target.value })} required />
        <button type="submit">Save Search</button>
      </form>
      <div className="chips">{saved.map(s => <span key={s.id}>{s.name} · {s.niche}</span>)}</div>
    </section>

    <section className="panel glass">
      <h2>Filters</h2>
      <div className="filter-row">
        <input placeholder="Hashtag" value={filters.hashtag} onChange={e => setFilters({ ...filters, hashtag: e.target.value })} />
        <input placeholder="Creator" value={filters.creator} onChange={e => setFilters({ ...filters, creator: e.target.value })} />
        <select value={filters.format} onChange={e => setFilters({ ...filters, format: e.target.value })}>
          <option value="">All Formats</option>
          <option>Reel</option>
          <option>Carousel</option>
          <option>Static</option>
        </select>
        <input type="number" placeholder="Minimum views" value={filters.min_views} onChange={e => setFilters({ ...filters, min_views: e.target.value })} />
        <button onClick={applyFilters}>Apply</button>
      </div>
    </section>

    <section className="panel glass">
      <h2>Viral Content Table</h2>
      <div className="table-wrap"><table><thead><tr>
        <th>Creator</th><th>Type</th><th>Hook</th><th>Views</th><th>Likes</th><th>Comments</th><th>ER%</th><th>Posted</th><th>Link</th>
      </tr></thead><tbody>
        {content.map(r => <tr key={r.id}><td>{r.creator}</td><td>{r.content_type}</td><td>{r.hook}</td><td>{r.views.toLocaleString()}</td><td>{r.likes.toLocaleString()}</td><td>{r.comments.toLocaleString()}</td><td>{r.engagement_rate}</td><td>{new Date(r.posted_at).toLocaleString()}</td><td><a href={r.link} target="_blank" rel="noreferrer">Open</a></td></tr>)}
      </tbody></table></div>
    </section>

    {analysis && <section className="panel two-col glass">
      <div><h2>Analysis</h2>
        <h3>Top Hooks Used</h3><ul>{analysis.top_hooks.map(x => <li key={x.name}>{x.name} ({x.count})</li>)}</ul>
        <h3>Common Caption Patterns</h3><ul>{analysis.caption_patterns.map(x => <li key={x.name}>{x.name} ({x.count})</li>)}</ul>
        <h3>Best Content Formats</h3><ul>{analysis.best_formats.map(x => <li key={x.name}>{x.name}: {x.engagement}%</li>)}</ul>
        <h3>Best Posting Days/Times</h3><ul>{analysis.best_posting_days.slice(0, 3).map(x => <li key={x.name}>{x.name} ({x.engagement}%)</li>)}</ul>
        <ul>{analysis.best_posting_times.slice(0, 3).map(x => <li key={x.name}>{x.name} ({x.engagement}%)</li>)}</ul>
        <h3>Topic Clusters</h3><ul>{analysis.topic_clusters.map(x => <li key={x.name}>{x.name} ({x.count})</li>)}</ul>
      </div>
      <div className="chart-box"><h3>Top Hooks Distribution</h3><ResponsiveContainer width="100%" height={300}><BarChart data={analysis.top_hooks}><CartesianGrid strokeDasharray="3 3" stroke="#314167" /><XAxis dataKey="name" hide /><YAxis /><Tooltip /><Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div>
    </section>}

    <section className="panel glass">
      <h2>Recommendation Engine (10 Ideas)</h2>
      <div className="cards">{recommendations.map((r, i) => <article key={i}><h3>{r.title}</h3><p><strong>Hook:</strong> {r.hook_line}</p><p><strong>Caption angle:</strong> {r.caption_angle}</p><p><strong>Reel structure:</strong> {r.reel_structure}</p></article>)}</div>
    </section>
  </div>
}

const Card = ({ title, value }) => <div className="kpi"><span>{title}</span><strong>{value}</strong></div>

export default App
