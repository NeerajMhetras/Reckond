import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, SkeletonGrid } from '../components/common/Feedback'
import { MediaCard } from '../components/media/MediaCard'

export function WatchlistPage({ user }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(Boolean(user))
  useEffect(() => { if (user) api.watchlist().then(setItems).finally(() => setLoading(false)) }, [user])
  if (!user) return <div className="page-content page-top"><EmptyState message="Sign in to build your watchlist." action="Sign in" href="#/login" /></div>
  return <div className="page-content page-top"><p className="eyebrow">YOUR LIBRARY</p><h1 className="page-title">Saved for later.</h1>{loading ? <SkeletonGrid /> : items.length ? <div className="media-grid">{items.map((entry) => <MediaCard key={entry.id} item={entry.media} />)}</div> : <EmptyState message="Nothing saved yet." action="Explore Reckond" href="#/" />}</div>
}
