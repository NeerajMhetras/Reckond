import { navigate } from '../../hooks/useHashRoute'
import { WatchlistButton } from './WatchlistButton'

export function MediaCard({ item }) {
  const year = item.release_date?.slice(0, 4)
  return <article className="media-card" onClick={() => item.id && navigate(`/media/${item.id}`)}>
    <div className="poster">{item.poster_url ? <img src={item.poster_url} alt={`${item.title} poster`} loading="lazy" /> : <span>{item.title?.slice(0, 1)}</span>}<div className="card-overlay">View details <span>→</span></div></div>
    <p className="card-title">{item.title}</p><p className="card-meta">{item.media_type} {year && ` / ${year}`}</p>
    {item.id && <WatchlistButton item={item} compact />}
  </article>
}
