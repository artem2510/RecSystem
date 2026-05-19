import { Link } from 'react-router-dom'
import { Star, Clock, Play } from 'lucide-react'
import { useState } from 'react'

const MovieCard = ({ movie }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Link 
      to={`/movies/${movie.id}`} 
      className="group relative block h-full"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative overflow-hidden rounded-lg bg-gray-800 transition-all duration-300 group-hover:scale-105 group-hover:shadow-2xl h-full flex flex-col">
        {/* Poster */}
        <div className="relative aspect-[2/3] flex-shrink-0">
          {movie.poster_url ? (
            <img
              src={movie.poster_url}
              alt={movie.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
              <span className="text-gray-500 text-sm">Немає постера</span>
            </div>
          )}
          
          {/* Overlay on hover */}
          <div className={`absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent transition-opacity duration-300 ${
            isHovered ? 'opacity-100' : 'opacity-0'
          }`}>
            <div className="absolute bottom-0 left-0 right-0 p-4">
              <div className="flex items-center justify-center mb-2">
                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <Play className="w-6 h-6 text-white fill-white" />
                </div>
              </div>
            </div>
          </div>

          {/* Rating Badge */}
          {movie.average_rating > 0 && (
            <div className="absolute top-2 right-2 bg-black/80 backdrop-blur-sm text-white px-2 py-1 rounded-lg flex items-center space-x-1">
              <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
              <span className="font-bold text-sm">{movie.average_rating.toFixed(1)}</span>
            </div>
          )}
        </div>

        {/* Info - Fixed height */}
        <div className="p-3 bg-gray-800 flex-1 flex flex-col">
          <h3 className="font-semibold text-white text-sm mb-2 line-clamp-2 group-hover:text-primary-400 transition-colors min-h-[2.5rem]">
            {movie.title}
          </h3>
          
          <div className="flex items-center space-x-3 text-xs text-gray-400 mb-2">
            {movie.year && <span>{movie.year}</span>}
            {movie.duration && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{movie.duration} хв</span>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-1 mt-auto">
            {movie.genres?.slice(0, 2).map((genre, index) => (
              <span
                key={index}
                className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs rounded-full"
              >
                {genre}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Link>
  )
}

export default MovieCard
