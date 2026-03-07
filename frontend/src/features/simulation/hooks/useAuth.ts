import { useState, useEffect, useCallback } from 'react'
import { getMe, login as apiLogin, logout as apiLogout, type User } from '@/api/auth'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const u = await getMe()
    setUser(u)
    setLoading(false)
    return u
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = useCallback(async (username: string, password: string) => {
    const u = await apiLogin(username, password)
    setUser(u)
    return u
  }, [])

  const logout = useCallback(async () => {
    await apiLogout()
    setUser(null)
  }, [])

  return { user, loading, login, logout, refresh }
}
