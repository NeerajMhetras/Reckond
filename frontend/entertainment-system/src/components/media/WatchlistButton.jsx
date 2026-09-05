import { useState } from 'react'
import { api, getStoredUser } from '../../services/api'
import { navigate } from '../../hooks/useHashRoute'

export function WatchlistButton({ item, compact = false }) {
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  const save = async (event) => {
    event.stopPropagation()
    if (!getStoredUser()) { navigate('/login'); return }
    setBusy(true)
    try {
      if (saved) await api.removeFromWatchlist(item.id)
      else await api.addToWatchlist(item.id)
      setSaved(!saved)
    } catch (error) { window.alert(error.message) } finally { setBusy(false) }
  }

  return <button className={compact ? 'save-button compact' : 'primary'} onClick={save} disabled={busy}>
    {busy ? 'Saving...' : saved ? '✓ Saved' : '+ Save to watchlist'}
  </button>
}
