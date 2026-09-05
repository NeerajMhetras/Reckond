import { useState } from 'react'
import { api } from '../../services/api'
import { navigate } from '../../hooks/useHashRoute'

export function SearchResultCard({ item }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const openMedia = async () => {
    setLoading(true)
    setError('')
    try {
      const media = await api.importMedia(item.external_id, item.media_type)
      navigate(`/media/${media.id}`)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return <article className="media-card search-result-card">
    <div className="poster">{item.poster_url ? <img src={item.poster_url} alt={`${item.title} poster`} loading="lazy" /> : <span>{item.title?.slice(0, 1)}</span>}</div>
    <p className="card-title">{item.title}</p>
    <p className="card-meta">{item.media_type} {item.release_date && ` / ${item.release_date.slice(0, 4)}`}</p>
    <button className="save-button" onClick={openMedia} disabled={loading}>{loading ? 'Adding...' : 'Add to Reckond'}</button>
    {error && <small className="card-error">{error}</small>}
  </article>
}
