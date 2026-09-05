import { useEffect, useState } from 'react'

export function navigate(path) {
  window.location.hash = path
}

export function useHashRoute() {
  const [route, setRoute] = useState(window.location.hash.slice(1) || '/')

  useEffect(() => {
    const updateRoute = () => setRoute(window.location.hash.slice(1) || '/')
    window.addEventListener('hashchange', updateRoute)
    return () => window.removeEventListener('hashchange', updateRoute)
  }, [])

  return route
}
