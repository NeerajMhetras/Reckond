import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { navigate } from '../hooks/useHashRoute'
import { SectionTitle } from '../components/common/SectionTitle'
import { EmptyState, Notice, SkeletonRow } from '../components/common/Feedback'
import { MediaRow } from '../components/media/MediaRow'

export function HomePage({ user, mediaType = '' }) {
  const [popular, setPopular] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.media(mediaType, 24), !mediaType && user ? api.recommendations() : Promise.resolve([])])
      .then(([media, picks]) => { setPopular(media.items || []); setRecommendations(picks.map((item) => item.media)) })
      .catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [user, mediaType])

  const featured = recommendations[0] || popular[0]
  return <>
    <section className="hero-panel" style={{ backgroundImage: featured?.backdrop_url ? `url(${featured.backdrop_url})` : featured?.poster_url ? `url(${featured.poster_url})` : undefined }}>
      <div className="hero-copy"><p className="eyebrow">YOUR ENTERTAINMENT UNIVERSE</p><h1>{featured?.title || 'Find your next favorite.'}</h1><p>{featured?.description || 'Discover films, series, books, and games that stay with you.'}</p><button className="primary" onClick={() => featured && navigate(`/media/${featured.id}`)}>Explore the pick <span>→</span></button></div><div className="hero-badge">FEATURED PICK</div>
    </section>
    <div className="page-content">{error && <Notice message={error} />}
      {!mediaType && <section className="section-block"><SectionTitle label="For you" note={user ? 'Picked from your taste' : 'Sign in to unlock your picks'} />{loading ? <SkeletonRow /> : recommendations.length ? <MediaRow items={recommendations} /> : <EmptyState message="Your personal shelf is waiting." action="Sign in to get recommendations" href="#/login" />}</section>}
      <section className="section-block"><SectionTitle label={mediaType || 'Popular now'} note={mediaType ? `Explore ${mediaType} on Reckond` : 'What the Reckond community is exploring'} />{loading ? <SkeletonRow /> : popular.length ? <MediaRow items={popular} /> : <EmptyState message={`No ${mediaType || 'media'} found yet.`} action="Explore everything" href="#/" />}</section>
    </div>
  </>
}
