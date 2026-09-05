export function Notice({ message }) {
  return <div className="notice">{message}</div>
}

export function EmptyState({ message, action, href }) {
  return <div className="empty-state">
    <span className="empty-mark">+</span>
    <h2>{message}</h2>
    {action && <a className="secondary" href={href}>{action}</a>}
  </div>
}

export function SkeletonRow() {
  return <div className="media-row">{[1, 2, 3, 4, 5].map((item) => <div className="skeleton-card" key={item} />)}</div>
}

export function SkeletonGrid() {
  return <div className="media-grid">{[1, 2, 3, 4, 5, 6].map((item) => <div className="skeleton-card" key={item} />)}</div>
}
