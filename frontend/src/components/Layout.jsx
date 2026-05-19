import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Film, Home, Search, TrendingUp, LayoutDashboard, LogOut, User, Menu, X, Github, Mail, Sparkles } from 'lucide-react'
import { useState } from 'react'

const Layout = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMobileMenuOpen(false)
  }

  const isActive = (path) => location.pathname === path

  const NavLink = ({ to, icon: Icon, children }) => (
    <Link
      to={to}
      onClick={() => setMobileMenuOpen(false)}
      className={`flex items-center space-x-2.5 px-4 py-2.5 rounded-lg transition-all ${
        isActive(to)
          ? 'bg-primary-600 text-white shadow-lg'
          : 'text-gray-300 hover:bg-gray-800 hover:text-white'
      }`}
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      <span className="font-medium whitespace-nowrap">{children}</span>
    </Link>
  )

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Navigation - Netflix Style */}
      <nav className="bg-black bg-opacity-95 backdrop-blur-sm sticky top-0 z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="bg-gradient-to-r from-red-600 to-primary-600 p-2 rounded-lg group-hover:scale-110 transition-transform">
                <Film className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-red-500 to-primary-500 bg-clip-text text-transparent">
                ArtFilm
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-3">
              <NavLink to="/" icon={Home}>Головна</NavLink>
              <NavLink to="/movies" icon={Film}>Фільми</NavLink>
              <NavLink to="/search" icon={Search}>Пошук</NavLink>
              
              {user && (
                <>
                  <NavLink to="/recommendations" icon={TrendingUp}>Рекомендації</NavLink>
                  <NavLink to="/mood-playlist" icon={Sparkles}>Плейлист</NavLink>
                  <NavLink to="/dashboard" icon={LayoutDashboard}>Дашборд</NavLink>
                </>
              )}
            </div>

            {/* User Menu */}
            <div className="hidden md:flex items-center space-x-3">
              {user ? (
                <>
                  <div className="flex items-center space-x-2 px-3 py-2 bg-gray-800 rounded-lg">
                    <div className="w-7 h-7 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-white font-medium text-sm">{user.username}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm">Вийти</span>
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                  >
                    Вхід
                  </Link>
                  <Link
                    to="/register"
                    className="px-6 py-2 bg-gradient-to-r from-red-600 to-primary-600 text-white rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all"
                  >
                    Реєстрація
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-300 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-2 border-t border-gray-800">
              <NavLink to="/" icon={Home}>Головна</NavLink>
              <NavLink to="/movies" icon={Film}>Фільми</NavLink>
              <NavLink to="/search" icon={Search}>Пошук</NavLink>
              
              {user && (
                <>
                  <NavLink to="/recommendations" icon={TrendingUp}>Рекомендації</NavLink>
                  <NavLink to="/mood-playlist" icon={Sparkles}>Плейлист</NavLink>
                  <NavLink to="/dashboard" icon={LayoutDashboard}>Дашборд</NavLink>
                </>
              )}

              <div className="pt-4 border-t border-gray-800">
                {user ? (
                  <>
                    <div className="flex items-center space-x-2 px-4 py-2 text-white">
                      <User className="w-5 h-5" />
                      <span>{user.username}</span>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-4 py-2 mt-2 bg-red-600 text-white rounded-lg"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Вийти</span>
                    </button>
                  </>
                ) : (
                  <div className="space-y-2">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="block px-4 py-2 text-center text-gray-300 hover:text-white"
                    >
                      Вхід
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="block px-4 py-2 text-center bg-gradient-to-r from-red-600 to-primary-600 text-white rounded-lg"
                    >
                      Реєстрація
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer - Enhanced */}
      <footer className="bg-black border-t border-gray-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* About */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-gradient-to-r from-red-600 to-primary-600 p-2 rounded-lg">
                  <Film className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">ArtFilm</span>
              </div>
              <p className="text-gray-400 mb-4">
                Інтелектуальна рекомендаційна система для фільмів з використанням гібридної фільтрації, 
                NLP-аналізу емоцій та Explainable AI.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Features */}
            <div>
              <h3 className="text-white font-semibold mb-4">Можливості</h3>
              <ul className="space-y-2 text-gray-400">
                <li className="hover:text-white transition-colors cursor-pointer">Гібридні рекомендації</li>
                <li className="hover:text-white transition-colors cursor-pointer">Аналіз емоцій</li>
                <li className="hover:text-white transition-colors cursor-pointer">Explainable AI</li>
                <li className="hover:text-white transition-colors cursor-pointer">Персональний дашборд</li>
              </ul>
            </div>

            {/* Tech Stack */}
            <div>
              <h3 className="text-white font-semibold mb-4">Технології</h3>
              <ul className="space-y-2 text-gray-400">
                <li>React + Vite</li>
                <li>FastAPI + Python</li>
                <li>PostgreSQL</li>
                <li>NLP & ML</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-500">
              © 2025 ArtFilm. Рекомендаційна система фільмів. Всі права захищені.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
