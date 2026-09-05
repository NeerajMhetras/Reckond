export function SectionTitle({ label, note }) {
  return <div className="section-title">
    <div><p className="eyebrow">{label}</p><h2>{note}</h2></div>
    <span>View all →</span>
  </div>
}
