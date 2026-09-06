import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { mediaTypes } from '../config/media'
import { EmptyState, Notice, SkeletonGrid } from '../components/common/Feedback'
import { SearchResultCard } from '../components/media/SearchResultCard'

export function SearchPage({ initialQuery }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(Boolean(initialQuery?.trim()))
  const [query, setQuery] = useState(initialQuery)
  const [error, setError] = useState('')
  const [selectedType, setSelectedType] = useState('all')

  useEffect(() => {
    if (!initialQuery?.trim()) return

    let cancelled = false
    api.searchAll(initialQuery, mediaTypes)
      .then((results) => { if (!cancelled) setItems(results) })
      .catch((err) => { if (!cancelled) setError(err.message) })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [initialQuery])

  const search = async (event) => {
    event?.preventDefault()
    if (!query.trim()) return
    setLoading(true); setError('')
    try { setItems(await api.searchAll(query, mediaTypes)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const visibleItems = selectedType === 'all'
    ? items
    : items.filter((item) => item.media_type === selectedType)

  const countFor = (type) => type === 'all'
    ? items.length
    : items.filter((item) => item.media_type === type).length

  return <div className="page-content page-top"><p className="eyebrow">DISCOVER</p><h1 className="page-title">Search the universe.</h1>
    <form className="large-search" onSubmit={search}><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Titles, creators, worlds..." /><button className="primary">Search all media</button></form>
    {items.length > 0 && <div className="media-filter" role="group" aria-label="Filter search results">
      {['all', ...mediaTypes].map((type) => <button key={type} className={selectedType === type ? 'media-filter-option active' : 'media-filter-option'} onClick={() => setSelectedType(type)} aria-pressed={selectedType === type}>
        {type === 'all' ? 'All' : type} <span>{countFor(type)}</span>
      </button>)}
    </div>}
    {error && <Notice message={error} />}{loading ? <SkeletonGrid /> : visibleItems.length ? <div className="media-grid">{visibleItems.map((item) => <SearchResultCard key={`${item.external_id}-${item.media_type}`} item={item} />)}</div> : <EmptyState message={query ? `No ${selectedType === 'all' ? 'media' : selectedType} matched that search.` : 'Start with a title, creator, or world.'} />}
  </div>
}
