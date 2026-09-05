import { useState } from 'react'
import { api } from '../../services/api'
import { navigate } from '../../hooks/useHashRoute'

export function ActivityControls({ item, user }) {
  const [message, setMessage] = useState('')
  const actionByMediaType = { movie: 'watched', series: 'completed', game: 'played', book: 'read' }
  const action = actionByMediaType[item.media_type] || 'completed'

  const log = async () => {
    if (!user) { navigate('/login'); return }
    try { await api.addLog(item.id, action); setMessage('Activity logged') }
    catch (error) { setMessage(error.message) }
  }

  return <div className="activity-controls">
    <button className="secondary" onClick={log}>Mark as {action}</button>{message && <small>{message}</small>}
  </div>
}
