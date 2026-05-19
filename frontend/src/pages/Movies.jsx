import { useState, useEffect } from 'react'
import api from '../services/api'
import MovieCard from '../components/MovieCard'
import { Filter } from 'lucide-react'

const Movies = () => {
  const [movies, setMovies] = useState([])
  const [genres, setGenres] = useState([])
  const [selectedGenre, setSelectedGenre] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchGenres()
    fetchMovies()
  }, [selectedGenre])

  const fetchGenres = async () => {
    try {
      const response = await api.get('/search/genres')
      setGenres(response.data)
    } catch (error) {
      console.error('Failed to fetch genres:', error)
    }
  }

  const fetchMovies = async () => {
    setLoading(true)
    try {
      const params = selectedGenre ? `?genre=${selectedGenre}` : ''
      const response = await api.get(`/movies${params}`)
      setMovies(response.data)
    } catch (error) {
      console.error('Failed to fetch movies:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-4">Всі фільми</h1>
        
        {/* Genre Filter */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center space-x-2 mb-3">
            <Filter className="w-5 h-5 text-gray-400" />
            <h3 className="font-semibold text-white">Фільтр за жанром</h3>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedGenre('')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedGenre === ''
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Всі
            </button>
            
            {genres.map((genre) => (
              <button
                key={genre}
                onClick={() => setSelectedGenre(genre)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedGenre === genre
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="bg-gray-800 rounded-xl p-4 animate-pulse border border-gray-700">
              <div className="bg-gray-700 h-64 rounded-lg mb-4"></div>
              <div className="bg-gray-700 h-4 rounded mb-2"></div>
              <div className="bg-gray-700 h-4 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : movies.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">Фільми не знайдено</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Movies
