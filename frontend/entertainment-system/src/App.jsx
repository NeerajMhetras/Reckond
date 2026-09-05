import { useState } from 'react'
import { clearSession, getStoredUser } from './services/api'
import { useHashRoute, navigate } from './hooks/useHashRoute'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { HomePage } from './pages/HomePage'
import { SearchPage } from './pages/SearchPage'
import { MediaDetailsPage } from './pages/MediaDetailsPage'
import { WatchlistPage } from './pages/WatchlistPage'
import { AuthPage } from './pages/AuthPage'
import { ProfilePage } from './pages/ProfilePage'
import './App.css'

function App() {
  const route = useHashRoute()
  const [routePath, queryString = ''] = route.split('?')
  const mediaType = new URLSearchParams(queryString).get('type') || ''
  const [user, setUser] = useState(getStoredUser())
  const [searchValue, setSearchValue] = useState('')
  const logout = () => { clearSession(); setUser(null); navigate('/') }

  return <div className="app-shell">
    <Header user={user} onLogout={logout} searchValue={searchValue} setSearchValue={setSearchValue} />
    <main>
      {routePath === '/' && <HomePage user={user} mediaType={mediaType} />}
      {routePath === '/search' && <SearchPage initialQuery={searchValue} />}
      {routePath.startsWith('/media/') && <MediaDetailsPage id={routePath.split('/')[2]} user={user} />}
      {routePath === '/watchlist' && <WatchlistPage user={user} />}
      {routePath === '/profile' && <ProfilePage user={user} />}
      {routePath === '/login' && <AuthPage mode="login" onUser={setUser} />}
      {routePath === '/register' && <AuthPage mode="register" onUser={setUser} />}
    </main>
    <Footer />
  </div>
}

export default App
