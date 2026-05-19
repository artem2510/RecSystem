import { useState, useEffect } from 'react';
import { Play, Clock, TrendingUp, Sparkles, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function MoodPlaylist() {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [journey, setJourney] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/emotions/journey/templates');
      setTemplates(response.data.templates);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const createJourney = async (templateKey) => {
    try {
      setCreating(true);
      const response = await api.post(`/emotions/journey/create?template_key=${templateKey}`);
      setJourney(response.data);
      setSelectedTemplate(templateKey);
    } catch (err) {
      console.error('Failed to create journey:', err);
    } finally {
      setCreating(false);
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}г ${mins}хв` : `${mins}хв`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Sparkles className="w-8 h-8 text-purple-500" />
        <h1 className="text-3xl font-bold text-white">Емоційні подорожі</h1>
      </div>

      <p className="text-gray-400 mb-8 text-lg">
        Створіть ідеальний плейлист фільмів для вашого вечора. Як Spotify, але для кіно! 🎬
      </p>

      {/* Шаблони */}
      {!journey && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-6">Оберіть свою подорож:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.key}
                className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-primary-500 transition-all cursor-pointer group"
                onClick={() => createJourney(template.key)}
              >
                <div className="text-5xl mb-4">{template.emoji}</div>
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-400 transition-colors">
                  {template.name}
                </h3>
                <p className="text-gray-400 text-sm mb-4">{template.description}</p>
                
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
                  <Clock className="w-4 h-4" />
                  <span>~{formatDuration(template.estimated_duration)}</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {template.emotions.map((emotion, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-gray-700 text-gray-300 rounded-full text-xs"
                    >
                      {emotion}
                    </span>
                  ))}
                </div>

                <button
                  disabled={creating}
                  className="mt-4 w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  {creating ? 'Створюємо...' : 'Створити подорож'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Створена подорож */}
      {journey && (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-4 sm:p-6 border-2 border-purple-500">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
              <div className="flex items-center gap-3">
                <div className="text-5xl">{journey.emoji}</div>
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold text-white">{journey.name}</h2>
                  <p className="text-sm sm:text-base text-gray-300">{journey.description}</p>
                </div>
              </div>
              <button
                onClick={() => setJourney(null)}
                className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2 w-full sm:w-auto justify-center"
              >
                <RefreshCw className="w-4 h-4" />
                Нова подорож
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-gray-900/50 rounded-lg p-3">
                <div className="text-2xl font-bold text-white">{journey.total_movies}</div>
                <div className="text-xs text-gray-400">Фільмів</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3">
                <div className="text-2xl font-bold text-white">{formatDuration(journey.total_duration)}</div>
                <div className="text-xs text-gray-400">Загальний час</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 col-span-2">
                <div className="text-sm font-semibold text-white mb-2">Рекомендації:</div>
                {journey.recommendations && journey.recommendations.slice(0, 2).map((rec, idx) => (
                  <div key={idx} className="text-xs text-gray-300">{rec}</div>
                ))}
              </div>
            </div>
          </div>

          {/* Плейлист */}
          <div>
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Play className="w-5 h-5 text-primary-400" />
              Ваш плейлист:
            </h3>
            <div className="space-y-4">
              {journey.playlist && journey.playlist.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-all cursor-pointer"
                  onClick={() => navigate(`/movies/${item.movie.id}`)}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {item.position}
                    </div>
                    
                    <div className="flex-shrink-0 w-20 h-28">
                      {item.movie.poster_url ? (
                        <img
                          src={item.movie.poster_url}
                          alt={item.movie.title}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-700 rounded-lg"></div>
                      )}
                    </div>

                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-white mb-1">{item.movie.title}</h4>
                      {item.movie.original_title && item.movie.original_title !== item.movie.title && (
                        <p className="text-sm text-gray-400 mb-2">{item.movie.original_title}</p>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        {item.movie.year && <span>{item.movie.year}</span>}
                        {item.movie.duration && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {item.movie.duration} хв
                          </span>
                        )}
                        {item.movie.average_rating && (
                          <span className="flex items-center gap-1">
                            <TrendingUp className="w-4 h-4" />
                            {item.movie.average_rating.toFixed(1)}
                          </span>
                        )}
                      </div>

                      <div className="mt-2">
                        <span className="px-3 py-1 bg-purple-600/30 text-purple-300 rounded-full text-xs border border-purple-500/30">
                          {item.emotion}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Емоційна крива */}
          {journey.emotion_curve && journey.emotion_curve.length > 0 && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Емоційна крива подорожі:</h3>
              <div className="space-y-3">
                {journey.emotion_curve.map((point, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-8 text-gray-400 text-sm">{point.position}.</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white text-sm font-medium">{point.movie_title}</span>
                        <span className="text-xs text-gray-500">({point.emotion})</span>
                      </div>
                      <div className="bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                          style={{ width: `${point.intensity * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="w-12 text-right text-sm text-gray-400">
                      {(point.intensity * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
