import { useState } from 'react'
import { api } from '../services/api'
import { mediaTypes } from '../config/media'
import { EmptyState, Notice, SkeletonGrid } from '../components/common/Feedback'
import { SearchResultCard } from '../components/media/SearchResultCard'

export function SearchPage({ initialQuery }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState(initialQuery)
  const [error, setError] = useState('')

  const search = async (event) => {
    event?.preventDefault()
    if (!query.trim()) return
    setLoading(true); setError('')
    try { setItems(await api.searchAll(query, mediaTypes)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  return <div className="page-content page-top"><p className="eyebrow">DISCOVER</p><h1 className="page-title">Search the universe.</h1>
    <form className="large-search" onSubmit={search}><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Titles, creators, worlds..." /><button className="primary">Search all media</button></form>
    {error && <Notice message={error} />}{loading ? <SkeletonGrid /> : items.length ? <div className="media-grid">{items.map((item) => <SearchResultCard key={`${item.external_id}-${item.media_type}`} item={item} />)}</div> : <EmptyState message={query ? 'Nothing matched that search.' : 'Start with a title, creator, or world.'} />}
  </div>
}
