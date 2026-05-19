import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { Star, Clock, Calendar, Play, Heart, ArrowLeft } from 'lucide-react'
import ExplainableAI from '../components/ExplainableAI'

const MovieDetail = () => {
  const { id } = useParams()
  const { user } = useAuth()
  const [movie, setMovie] = useState(null)
  const [userRating, setUserRating] = useState(0)
  const [hoverRating, setHoverRating] = useState(0)
  const [loading, setLoading] = useState(true)
  const [similarMovies, setSimilarMovies] = useState([])
  const [isWatched, setIsWatched] = useState(false)
  const [watchAnimation, setWatchAnimation] = useState(false)

  useEffect(() => {
    window.scrollTo(0, 0)
    fetchMovie()
    fetchSimilarMovies()
  }, [id])

  const fetchMovie = async () => {
    try {
      const response = await api.get(`/movies/${id}`)
      setMovie(response.data)
      // Отримати оцінку користувача якщо є
      if (user) {
        try {
          const ratingResponse = await api.get(`/movies/${id}/user-rating`)
          if (ratingResponse.data.rating) {
            setUserRating(ratingResponse.data.rating)
          }
        } catch (err) {
          // Оцінки немає - це нормально
        }
      }
    } catch (error) {
      console.error('Failed to fetch movie:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSimilarMovies = async () => {
    try {
      const response = await api.get(`/recommendations/similar/${id}`)
      setSimilarMovies(response.data)
    } catch (error) {
      console.error('Failed to fetch similar movies:', error)
    }
  }

  const handleRate = async (rating) => {
    if (!user) return
    
    try {
      await api.post(`/movies/${id}/rate`, { movie_id: parseInt(id), rating })
      setUserRating(rating)
      fetchMovie() // Оновити середній рейтинг
    } catch (error) {
      console.error('Failed to rate movie:', error)
    }
  }

  const handleWatch = async () => {
    if (!user) return
    
    try {
      await api.post(`/movies/${id}/watch`)
      setIsWatched(true)
      setWatchAnimation(true)
      setTimeout(() => setWatchAnimation(false), 600)
    } catch (error) {
      console.error('Failed to mark as watched:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!movie) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-center text-gray-400">Фільм не знайдено</p>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link to="/movies" className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-6">
        <ArrowLeft className="w-5 h-5" />
        <span>Назад до фільмів</span>
      </Link>

      <div className="grid md:grid-cols-3 gap-8 mb-12">
        {/* Poster */}
        <div>
          {movie.poster_url ? (
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="w-full rounded-lg shadow-lg"
            />
          ) : (
            <div className="w-full h-96 bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-gray-400">Немає постера</span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="md:col-span-2">
          <h1 className="text-4xl font-bold text-white mb-2">{movie.title}</h1>
          {movie.original_title && movie.original_title !== movie.title && (
            <p className="text-xl text-gray-400 mb-4">{movie.original_title}</p>
          )}

          <div className="flex flex-wrap items-center gap-4 mb-6">
            {movie.average_rating > 0 && (
              <div className="flex items-center space-x-2">
                <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
                <span className="text-2xl font-bold text-white">{movie.average_rating.toFixed(1)}</span>
                <span className="text-gray-400">({movie.ratings_count} оцінок)</span>
              </div>
            )}
            
            {movie.year && (
              <div className="flex items-center space-x-2 text-gray-400">
                <Calendar className="w-5 h-5" />
                <span>{movie.year}</span>
              </div>
            )}
            
            {movie.duration && (
              <div className="flex items-center space-x-2 text-gray-400">
                <Clock className="w-5 h-5" />
                <span>{movie.duration} хв</span>
              </div>
            )}
          </div>

          {/* Genres */}
          <div className="flex flex-wrap gap-2 mb-6">
            {movie.genres?.map((genre, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full font-medium"
              >
                {genre}
              </span>
            ))}
          </div>

          {/* Description */}
          <p className="text-gray-300 text-lg mb-6 leading-relaxed">{movie.description}</p>

          {/* Emotions */}
          <div className="mb-6">
            <h3 className="font-semibold text-lg mb-3 text-white">Емоційні характеристики</h3>
            {movie.emotions && Object.keys(movie.emotions).length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(movie.emotions)
                  .filter(([_, score]) => score > 0.1)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 8)
                  .map(([emotion, score]) => (
                    <div key={emotion} className="flex items-center justify-between">
                      <span className="text-gray-300 capitalize">{emotion}</span>
                      <div className="flex-1 mx-3 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${score * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-400">{(score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm italic">Емоційні характеристики для цього фільму ще не визначені</p>
            )}
          </div>

          {/* Actions */}
          {user && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2 text-white">Ваша оцінка</h3>
                <div className="flex space-x-2">
                  {[...Array(10)].map((_, i) => {
                    const rating = i + 1
                    return (
                      <button
                        key={i}
                        onClick={() => handleRate(rating)}
                        onMouseEnter={() => setHoverRating(rating)}
                        onMouseLeave={() => setHoverRating(0)}
                        className="transition-all duration-200 hover:scale-110"
                      >
                        <Star
                          className={`w-8 h-8 transition-all duration-200 ${
                            rating <= (hoverRating || userRating)
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="flex space-x-4">
                {movie.trailer_url && (
                  <a
                    href={movie.trailer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Play className="w-5 h-5" />
                    <span>Дивитись трейлер</span>
                  </a>
                )}
                
                <button
                  onClick={handleWatch}
                  disabled={isWatched}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                    isWatched
                      ? 'bg-red-100 text-red-600 border-2 border-red-500 cursor-default'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600'
                  } ${watchAnimation ? 'animate-bounce' : ''}`}
                >
                  <Heart className={`w-5 h-5 transition-all duration-300 ${
                    isWatched ? 'fill-red-500 text-red-500' : ''
                  }`} />
                  <span>{isWatched ? 'Переглянуто ✓' : 'Позначити як переглянутий'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Explainable AI */}
      {user && (
        <div className="mb-12">
          <ExplainableAI movieId={parseInt(id)} />
        </div>
      )}

      {/* Similar Movies */}
      {similarMovies.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Схожі фільми</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {similarMovies.map((movie) => (
              <Link
                key={movie.id}
                to={`/movies/${movie.id}`}
                className="card hover:shadow-lg transition-shadow"
              >
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.title}
                    className="w-full h-48 object-cover rounded-lg mb-3"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 rounded-lg mb-3"></div>
                )}
                <h3 className="font-semibold line-clamp-2">{movie.title}</h3>
                <div className="flex items-center space-x-1 mt-2">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm">{movie.average_rating.toFixed(1)}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default MovieDetail
