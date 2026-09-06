import { mediaTypes } from '../../config/media'
import { navigate } from '../../hooks/useHashRoute'

export function Header({ user, onLogout, searchValue, setSearchValue }) {
  const submitSearch = (event) => {
    event.preventDefault()
    const query = searchValue.trim()
    if (query) navigate(`/search?query=${encodeURIComponent(query)}`)
  }

  return <header className="topbar">
    <button className="wordmark" onClick={() => navigate('/')} aria-label="Go to home">RECKOND<span>.</span></button>
    <nav><a href="#/">Home</a><a href="#/watchlist">Watchlist</a><div className="type-links">{mediaTypes.map((type) => <a key={type} href={`#/?type=${type}`}>{type}</a>)}</div></nav>
    <form className="search-box" onSubmit={submitSearch}><span aria-hidden="true">/</span><input value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Search your next obsession" aria-label="Search" /></form>
    {user ? <div className="profile-actions"><a className="profile-link" href="#/profile">{user.username} <small>Profile</small></a><button className="logout-link" onClick={onLogout}>Log out</button></div> : <a className="profile-link" href="#/login">Sign in</a>}
  </header>
}
