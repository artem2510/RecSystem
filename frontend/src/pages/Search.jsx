import { useState, useEffect, useRef } from 'react';
import { Search as SearchIcon, Filter, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import MovieCard from '../components/MovieCard';
import api from '../services/api';

export default function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef(null);
  const navigate = useNavigate();

  // Debounce для autocomplete
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim().length > 0) {
        fetchSuggestions(query);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Закриття випадаючого списку при кліку поза ним
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchSuggestions = async (searchQuery) => {
    try {
      const response = await api.get(`/search/autocomplete?q=${encodeURIComponent(searchQuery)}&limit=10`);
      setSuggestions(response.data);
      setShowSuggestions(true);
    } catch (err) {
      console.error('Autocomplete failed:', err);
      setSuggestions([]);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setShowSuggestions(false);
      const response = await api.get(`/search?q=${encodeURIComponent(query)}`);
      setResults(response.data);
      setSearched(true);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (movie) => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    navigate(`/movies/${movie.id}`);
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        if (selectedIndex >= 0) {
          e.preventDefault();
          handleSuggestionClick(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const clearSearch = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    setResults([]);
    setSearched(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-6">Пошук фільмів</h1>
        
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative" ref={searchRef}>
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => query.trim() && suggestions.length > 0 && setShowSuggestions(true)}
              placeholder="Почніть вводити назву фільму..."
              className="w-full pl-10 pr-10 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            {query && (
              <button
                type="button"
                onClick={clearSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white z-10"
              >
                <X className="w-5 h-5" />
              </button>
            )}

            {/* Випадаючий список підказок */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-50 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-2xl max-h-96 overflow-y-auto custom-scrollbar">
                {suggestions.map((movie, index) => (
                  <div
                    key={movie.id}
                    onClick={() => handleSuggestionClick(movie)}
                    className={`flex items-center gap-3 p-3 cursor-pointer transition-colors ${
                      index === selectedIndex 
                        ? 'bg-gray-700' 
                        : 'hover:bg-gray-700'
                    } ${index !== suggestions.length - 1 ? 'border-b border-gray-700' : ''}`}
                  >
                    {movie.poster_url ? (
                      <img 
                        src={movie.poster_url} 
                        alt={movie.title}
                        className="w-12 h-16 object-cover rounded"
                      />
                    ) : (
                      <div className="w-12 h-16 bg-gray-700 rounded flex items-center justify-center">
                        <SearchIcon className="w-6 h-6 text-gray-500" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium truncate">{movie.title}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        {movie.year && <span>{movie.year}</span>}
                        {movie.genres && movie.genres.length > 0 && (
                          <>
                            <span>•</span>
                            <span className="truncate">{movie.genres.slice(0, 2).join(', ')}</span>
                          </>
                        )}
                      </div>
                    </div>
                    {movie.average_rating > 0 && (
                      <div className="flex items-center gap-1 text-yellow-500">
                        <span className="text-sm font-semibold">{movie.average_rating.toFixed(1)}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Пошук...' : 'Знайти'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      )}

      {!loading && searched && (
        <div>
          <p className="text-gray-400 mb-6">
            Знайдено результатів: {results.length}
          </p>
          
          {results.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400">Нічого не знайдено. Спробуйте інший запит.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {results.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          )}
        </div>
      )}

      {!searched && !loading && (
        <div className="text-center py-12">
          <SearchIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">
            Введіть запит для пошуку фільмів
          </p>
        </div>
      )}
    </div>
  );
}
