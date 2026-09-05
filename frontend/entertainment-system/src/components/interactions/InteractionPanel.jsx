import { useEffect, useState } from 'react'
import { api } from '../../services/api'
import { navigate } from '../../hooks/useHashRoute'

export function InteractionPanel({ item, user }) {
  const [rating, setRating] = useState('')
  const [review, setReview] = useState('')
  const [hasReview, setHasReview] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!user) return
    Promise.allSettled([api.getRating(item.id), api.getReview(item.id)]).then(([ratingResult, reviewResult]) => {
      if (ratingResult.status === 'fulfilled') setRating(String(ratingResult.value.rating))
      if (reviewResult.status === 'fulfilled') { setReview(reviewResult.value.content); setHasReview(true) }
    })
  }, [item.id, user])

  const saveRating = async () => {
    if (!user) { navigate('/login'); return }
    try { await api.saveRating(item.id, Number(rating)); setMessage('Rating saved') }
    catch (error) { setMessage(error.message) }
  }

  const saveReview = async () => {
    if (!user) { navigate('/login'); return }
    try { await api.saveReview(item.id, review, hasReview); setHasReview(true); setMessage('Review saved') }
    catch (error) { setMessage(error.message) }
  }

  return <section className="interaction-panel"><p className="eyebrow">YOUR TAKE</p>
    <div className="interaction-row"><label>Rating (1–10)<select value={rating} onChange={(event) => setRating(event.target.value)}><option value="">Choose</option>{Array.from({ length: 10 }, (_, index) => <option key={index + 1} value={index + 1}>{index + 1}</option>)}</select></label><button className="secondary" onClick={saveRating}>Save rating</button></div>
    <label className="review-label">Review<textarea value={review} onChange={(event) => setReview(event.target.value)} maxLength="5000" placeholder="What did you think?" /></label>
    <button className="secondary" onClick={saveReview}>{hasReview ? 'Update review' : 'Publish review'}</button>{message && <small>{message}</small>}
  </section>
}
