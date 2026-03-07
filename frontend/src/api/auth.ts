import { api } from './client'

export interface User {
  id: string
  username: string
  email: string
}

export async function getMe(): Promise<User | null> {
  try {
    return await api.get<User>('/me/')
  } catch {
    return null
  }
}

export async function login(username: string, password: string): Promise<User> {
  return api.post<User>('/auth/login/', { username, password })
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout/', {})
}
