import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { TrendingUp, Star, Clock } from 'lucide-react'
import MovieCard from '../components/MovieCard'

const Home = () => {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMovies()
  }, [])

  const fetchMovies = async () => {
    try {
      const response = await api.get('/movies?limit=15')
      setMovies(response.data)
    } catch (error) {
      console.error('Failed to fetch movies:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 min-h-screen">
      {/* Hero Section - Netflix Style */}
      <div className="relative min-h-[60vh] md:h-[70vh] bg-gradient-to-b from-black via-gray-900 to-gray-900">
        <div className="absolute inset-0 bg-gradient-to-r from-black via-transparent to-black opacity-80"></div>
        <div className="absolute inset-0 flex items-center">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-12 md:py-0">
            <div className="max-w-2xl">
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-4 md:mb-6 leading-tight">
                Знайдіть ваш наступний
                <span className="block bg-gradient-to-r from-red-500 to-primary-500 bg-clip-text text-transparent">
                  улюблений фільм
                </span>
              </h1>
              <p className="text-lg sm:text-xl md:text-2xl text-gray-300 mb-6 md:mb-8">
                Персоналізовані рекомендації на основі ваших вподобань та емоційних характеристик
              </p>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                <Link 
                  to="/movies" 
                  className="px-6 sm:px-8 py-3 sm:py-4 bg-white text-black rounded-lg font-bold text-base sm:text-lg hover:bg-gray-200 transition-all transform hover:scale-105 shadow-lg text-center"
                >
                  Переглянути фільми
                </Link>
                <Link 
                  to="/search" 
                  className="px-6 sm:px-8 py-3 sm:py-4 bg-gray-800/80 backdrop-blur-sm text-white rounded-lg font-bold text-base sm:text-lg hover:bg-gray-700 transition-all border border-gray-600 text-center"
                >
                  Розширений пошук
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="bg-gray-800 rounded-xl p-6 text-center hover:bg-gray-750 transition-colors border border-gray-700">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gradient-to-r from-red-600 to-primary-600 rounded-full">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-white">Розумні рекомендації</h3>
            <p className="text-gray-400">
              Гібридна система фільтрації для точних персоналізованих рекомендацій
            </p>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 text-center hover:bg-gray-750 transition-colors border border-gray-700">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full">
                <Star className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-white">Аналіз емоцій</h3>
            <p className="text-gray-400">
              Пошук фільмів за емоційними характеристиками та настроєм
            </p>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 text-center hover:bg-gray-750 transition-colors border border-gray-700">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full">
                <Clock className="w-8 h-8 text-white" />
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-white">Історія переглядів</h3>
            <p className="text-gray-400">
              Відстежуйте свої вподобання та отримуйте статистику
            </p>
          </div>
        </div>

        {/* Popular Movies */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-white">Популярні фільми</h2>
            <Link 
              to="/movies" 
              className="text-primary-400 hover:text-primary-300 font-medium flex items-center space-x-2 group"
            >
              <span>Дивитись всі</span>
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {[...Array(15)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-800 aspect-[2/3] rounded-lg mb-2"></div>
                  <div className="bg-gray-800 h-4 rounded mb-2"></div>
                  <div className="bg-gray-800 h-3 rounded w-2/3"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Home
