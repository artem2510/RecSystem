import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    return userData
  }

  const register = async (email, username, password, full_name) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
      full_name
    })
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    delete api.defaults.headers.common['Authorization']
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
