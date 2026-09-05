import { MediaCard } from './MediaCard'

export function MediaRow({ items }) {
  return <div className="media-row">{items.map((item) => <MediaCard key={item.id || item.external_id} item={item} />)}</div>
}
