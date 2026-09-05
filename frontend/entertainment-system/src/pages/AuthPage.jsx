import { useState } from 'react'
import { api } from '../services/api'
import { navigate } from '../hooks/useHashRoute'
import { Notice } from '../components/common/Feedback'

export function AuthPage({ mode, onUser }) {
  const login = mode === 'login'
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError('')
    try { if (login) onUser(await api.login(form.email, form.password)); else { await api.register(form); onUser(await api.login(form.email, form.password)) }; navigate('/') }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  return <div className="auth-page"><div className="auth-intro"><p className="eyebrow">WELCOME TO RECKOND</p><h1>{login ? 'Come back to your favorites.' : 'Make your taste count.'}</h1><p>One place for every film, series, book, and game you want to remember.</p></div><form className="auth-form" onSubmit={submit}><h2>{login ? 'Sign in' : 'Create account'}</h2>{login ? <label>Email<input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label> : <><label>Username<input required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label><label>Email<input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label></>}<label>Password<input required type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>{error && <Notice message={error} />}<button className="primary" disabled={loading}>{loading ? 'Working...' : login ? 'Enter Reckond' : 'Start exploring'}</button><p className="form-switch">{login ? 'New here?' : 'Already a member?'} <a href={login ? '#/register' : '#/login'}>{login ? 'Create an account' : 'Sign in'}</a></p></form></div>
}
