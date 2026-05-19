import { useState, useEffect } from 'react';
import { Film, Sparkles, Zap, RefreshCw } from 'lucide-react';
import MovieCard from '../components/MovieCard';
import api from '../services/api';

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quickPick, setQuickPick] = useState(null);
  const [loadingQuickPick, setLoadingQuickPick] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/recommendations');
      setRecommendations(response.data);
      setError(null);
    } catch (err) {
      setError('Не вдалося завантажити рекомендації');
      console.error('Помилка завантаження рекомендацій:', err);
    } finally {
      setLoading(false);
    }
  };


  const fetchQuickPick = async () => {
    try {
      setLoadingQuickPick(true);
      const response = await api.get('/recommendations/quick-pick');
      setQuickPick(response.data);
    } catch (err) {
      console.error('Помилка завантаження Quick Pick:', err);
    } finally {
      setLoadingQuickPick(false);
    }
  };

  if (error && !loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchRecommendations}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Спробувати знову
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Sparkles className="w-8 h-8 text-primary-500" />
        <h1 className="text-3xl font-bold text-white">Рекомендації для вас</h1>
      </div>

      <p className="text-gray-400 mb-8 text-lg">
        Персоналізовані рекомендації на основі ваших вподобань, рейтингів та історії переглядів
      </p>

      {/* Quick Pick Button */}
      <div className="mb-8">
        <button
          onClick={fetchQuickPick}
          disabled={loadingQuickPick}
          className="w-full md:w-auto px-8 py-4 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:from-primary-700 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          <Zap className="w-6 h-6" />
          {loadingQuickPick ? 'Підбираємо...' : 'Фільм на вечір 🎬'}
        </button>
      </div>

      {/* Quick Pick Result */}
      {quickPick && (
        <div className="mb-8 bg-gradient-to-r from-primary-900/50 to-purple-900/50 rounded-xl p-6 border-2 border-primary-500">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">Ваш ідеальний вибір на сьогодні!</h2>
          </div>
          <div className="grid md:grid-cols-[300px_1fr] gap-6 items-center">
            <div className="w-full max-w-[300px] mx-auto">
              <MovieCard movie={quickPick.movie} />
            </div>
            <div className="flex flex-col justify-center space-y-4">
              <div className="flex items-center gap-3">
                <div className="text-5xl font-bold text-primary-400">
                  {Math.round(quickPick.score * 100)}%
                </div>
                <div className="text-gray-400 text-lg">збіг з вашими вподобаннями</div>
              </div>
              {quickPick.explanations && quickPick.explanations.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-white mb-3">Чому саме цей фільм?</h3>
                  <ul className="space-y-2">
                    {quickPick.explanations.map((exp, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-gray-300">
                        <span className="text-primary-400 mt-1 text-lg">•</span>
                        <span className="text-base">{exp.reason_text}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Loading indicator for mood change */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-400">Завантаження рекомендацій...</p>
          </div>
        </div>
      )}

      {/* All Recommendations */}
      {!loading && recommendations.length === 0 ? (
        <div className="text-center py-12">
          <Film className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">
            Оцініть кілька фільмів, щоб отримати персоналізовані рекомендації
          </p>
        </div>
      ) : !loading && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Всі рекомендації</h2>
            <button
              onClick={fetchRecommendations}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors border border-gray-700"
            >
              <RefreshCw className="w-4 h-4" />
              Оновити
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {recommendations.map((rec) => (
              <div key={rec.movie.id} className="flex flex-col">
                <div className="relative group flex-shrink-0">
                  <MovieCard movie={rec.movie} />
                  {rec.score && (
                    <div className="absolute top-2 left-2 bg-primary-600 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-lg z-10">
                      {Math.round(rec.score * 100)}%
                    </div>
                  )}
                </div>
                {rec.explanations && rec.explanations.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="font-medium text-white text-sm mb-2">Чому рекомендуємо:</p>
                    <ul className="space-y-1">
                      {rec.explanations.slice(0, 2).map((exp, idx) => (
                        <li key={idx} className="text-xs text-gray-400 flex items-start gap-1">
                          <span className="text-primary-400">•</span>
                          <span>{exp.reason_text}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
