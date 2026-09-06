import { useEffect, useState } from 'react'
import { api, getStoredUser } from '../../services/api'
import { navigate } from '../../hooks/useHashRoute'

export function WatchlistButton({ item, compact = false }) {
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!getStoredUser() || !item.id) return
    api.watchlist()
      .then((entries) => setSaved(entries.some((entry) => entry.entertainment_id === item.id)))
      .catch(() => {})
  }, [item.id])

  const save = async (event) => {
    event.stopPropagation()
    if (!getStoredUser()) { navigate('/login'); return }
    setBusy(true)
    try {
      if (saved) await api.removeFromWatchlist(item.id)
      else await api.addToWatchlist(item.id)
      setSaved((currentSaved) => !currentSaved)
    } catch (error) { window.alert(error.message) } finally { setBusy(false) }
  }

  return <button className={compact ? 'save-button compact' : 'primary'} onClick={save} disabled={busy}>
    {busy ? 'Saving...' : saved ? 'Added to watchlist' : '+ Save to watchlist'}
  </button>
}
