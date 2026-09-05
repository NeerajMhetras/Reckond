import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { Notice, SkeletonGrid } from '../components/common/Feedback'
import { WatchlistButton } from '../components/media/WatchlistButton'
import { ActivityControls } from '../components/interactions/ActivityControls'
import { InteractionPanel } from '../components/interactions/InteractionPanel'

export function MediaDetailsPage({ id, user }) {
  const [item, setItem] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api.details(id).then(setItem).catch((err) => setError(err.message)) }, [id])
  if (error) return <div className="page-content page-top"><Notice message={error} /></div>
  if (!item) return <div className="page-content page-top"><SkeletonGrid /></div>
  return <div className="details"><div className="detail-backdrop" style={{ backgroundImage: item.backdrop_url ? `url(${item.backdrop_url})` : item.poster_url ? `url(${item.poster_url})` : undefined }} /><div className="detail-content"><p className="eyebrow">{item.media_type} {item.release_date ? ` / ${item.release_date.slice(0, 4)}` : ''}</p><h1>{item.title}</h1><p className="detail-description">{item.description || 'No description available yet.'}</p><div className="detail-actions"><WatchlistButton item={item} /><ActivityControls item={item} user={user} /></div><p className="muted">{item.language || 'Original language unavailable'} {item.external_source ? ` / ${item.external_source}` : ''}</p><InteractionPanel item={item} user={user} /></div></div>
}
