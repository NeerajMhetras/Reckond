import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, Notice, SkeletonGrid } from '../components/common/Feedback'
import { MediaCard } from '../components/media/MediaCard'

export function ProfilePage({ user }) {
  const [profile, setProfile] = useState(null)
  const [ratings, setRatings] = useState([])
  const [reviews, setReviews] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(Boolean(user))
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    Promise.allSettled([api.me(), api.ratings(), api.reviews(), api.logs()]).then((results) => {
      const [profileResult, ratingsResult, reviewsResult, logsResult] = results
      if (profileResult.status === 'fulfilled') setProfile(profileResult.value)
      if (ratingsResult.status === 'fulfilled') setRatings(ratingsResult.value)
      if (reviewsResult.status === 'fulfilled') setReviews(reviewsResult.value)
      if (logsResult.status === 'fulfilled') setLogs(logsResult.value)
      if (results.every((result) => result.status === 'rejected')) setError('Unable to load your profile')
    }).finally(() => setLoading(false))
  }, [user])

  if (!user) return <div className="page-content page-top"><EmptyState message="Sign in to view your profile." action="Sign in" href="#/login" /></div>
  if (loading) return <div className="page-content page-top"><SkeletonGrid /></div>

  const displayUser = profile || user
  return <div className="page-content page-top profile-page">
    {error && <Notice message={error} />}
    <section className="profile-header"><div><p className="eyebrow">YOUR RECKOND</p><h1 className="page-title">{displayUser.username}</h1><p className="muted">{displayUser.email}</p></div><div className="profile-stats"><span><strong>{ratings.length}</strong> ratings</span><span><strong>{reviews.length}</strong> reviews</span><span><strong>{logs.length}</strong> logged</span></div></section>
    <section className="profile-section"><div className="section-heading"><p className="eyebrow">RATED</p><h2>Your taste, in numbers.</h2></div>{ratings.length ? <div className="media-grid">{ratings.slice(0, 8).map((entry) => <MediaCard key={entry.id} item={entry.media} />)}</div> : <EmptyState message="Your ratings will appear here." />}</section>
    <section className="profile-section"><div className="section-heading"><p className="eyebrow">REVIEWS</p><h2>What you thought.</h2></div>{reviews.length ? <div className="review-list">{reviews.slice(0, 6).map((review) => <article className="review-item" key={review.id}><div><strong>{review.media.title}</strong><span>{review.media.media_type}</span></div><p>{review.content}</p></article>)}</div> : <EmptyState message="No reviews yet." />}</section>
    <section className="profile-section"><div className="section-heading"><p className="eyebrow">ACTIVITY</p><h2>Your entertainment trail.</h2></div>{logs.length ? <div className="activity-list">{logs.slice(0, 8).map((log) => <div className="activity-item" key={log.id}><span className="activity-action">{log.action}</span><strong>{log.media.title}</strong><time>{new Date(log.logged_at).toLocaleDateString()}</time></div>)}</div> : <EmptyState message="Log a film, series, book, or game to see it here." />}</section>
  </div>
}
