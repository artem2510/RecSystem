import { useState } from 'react';
import { HelpCircle, AlertCircle, Lightbulb, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import MovieCard from './MovieCard';

const ExplainableAI = ({ movieId }) => {
  const [whyNotData, setWhyNotData] = useState(null);
  const [counterfactual, setCounterfactual] = useState(null);
  const [alternativesData, setAlternativesData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(null);
  const [selectedAlternativeType, setSelectedAlternativeType] = useState('different_genre');

  const fetchWhyNot = async () => {
    setLoading(true);
    setActiveTab('why-not');
    try {
      const response = await api.get(`/recommendations/explain-why-not/${movieId}`);
      setWhyNotData(response.data);
    } catch (err) {
      console.error('Failed to fetch why-not explanation:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCounterfactual = async () => {
    setLoading(true);
    setActiveTab('counterfactual');
    try {
      const response = await api.get(`/recommendations/counterfactual/${movieId}`);
      // Backend повертає {counterfactual: {...}}, розпаковуємо
      setCounterfactual(response.data.counterfactual);
    } catch (err) {
      console.error('Failed to fetch counterfactual:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlternatives = async (reason = 'different_genre') => {
    setLoading(true);
    setActiveTab('alternatives');
    setSelectedAlternativeType(reason);
    try {
      const response = await api.get(`/recommendations/alternatives/${movieId}?reason=${reason}`);
      // Backend повертає масив [{movie, reason, alternative_type}]
      const alternatives = response.data;
      // Формуємо об'єкт для frontend
      setAlternativesData({
        alternatives: alternatives,
        explanation: alternatives.length > 0 ? alternatives[0].reason : ''
      });
    } catch (err) {
      console.error('Failed to fetch alternatives:', err);
      setAlternativesData(null);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-400 bg-red-900/30 border-red-500/30';
      case 'medium':
        return 'text-yellow-400 bg-yellow-900/30 border-yellow-500/30';
      default:
        return 'text-blue-400 bg-blue-900/30 border-blue-500/30';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'text-green-400';
      case 'medium':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <Lightbulb className="w-6 h-6 text-yellow-400" />
        Explainable AI - Зрозумійте рекомендації
      </h3>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <button
          onClick={fetchWhyNot}
          disabled={loading}
          className="px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 border border-gray-600"
        >
          <HelpCircle className="w-5 h-5" />
          Чому не це?
        </button>

        <button
          onClick={fetchCounterfactual}
          disabled={loading}
          className="px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 border border-gray-600"
        >
          <AlertCircle className="w-5 h-5" />
          Що якби?
        </button>

        <button
          onClick={() => fetchAlternatives('different_genre')}
          disabled={loading}
          className="px-4 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 border border-gray-600"
        >
          <RefreshCw className="w-5 h-5" />
          Альтернативи
        </button>
      </div>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      )}

      {/* Why Not Results - Детальний аналіз */}
      {activeTab === 'why-not' && whyNotData && !loading && (
        <div className="space-y-6">
          {/* Загальний збіг */}
          <div className="bg-gradient-to-r from-primary-900/30 to-purple-900/30 rounded-xl p-6 border border-primary-500/30">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-2xl font-bold text-white">Збіг з вашими вподобаннями</h4>
              <div className="text-4xl font-bold text-primary-400">
                {whyNotData.total_match}%
              </div>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-4">
              <div
                className="bg-gradient-to-r from-primary-500 to-purple-500 h-4 rounded-full transition-all duration-500"
                style={{ width: `${whyNotData.total_match}%` }}
              ></div>
            </div>
          </div>

          {/* Фактори збігу */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Жанри */}
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h5 className="text-lg font-semibold text-white flex items-center gap-2">
                  🎬 Жанри
                </h5>
                <span className="text-2xl font-bold text-blue-400">
                  {whyNotData.factors.genres.match_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
                <div
                  className="bg-blue-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${whyNotData.factors.genres.match_percentage}%` }}
                ></div>
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-400 mb-1">Ваші улюблені:</p>
                  <div className="flex flex-wrap gap-1">
                    {whyNotData.factors.genres.your_favorites.slice(0, 3).map((g, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded text-xs">
                        {g.genre} ({g.percentage}%)
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 mb-1">Жанри фільму:</p>
                  <div className="flex flex-wrap gap-1">
                    {whyNotData.factors.genres.movie_genres.map((g, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded text-xs ${
                          whyNotData.factors.genres.common_genres.includes(g)
                            ? 'bg-green-900/30 text-green-300 border border-green-500/30'
                            : 'bg-gray-700 text-gray-300'
                        }`}
                      >
                        {g} {whyNotData.factors.genres.common_genres.includes(g) && '✓'}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Емоції */}
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h5 className="text-lg font-semibold text-white flex items-center gap-2">
                  😊 Емоції
                </h5>
                <span className="text-2xl font-bold text-purple-400">
                  {whyNotData.factors.emotions.match_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
                <div
                  className="bg-purple-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${whyNotData.factors.emotions.match_percentage}%` }}
                ></div>
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-400 mb-1">Ваші улюблені:</p>
                  <div className="flex flex-wrap gap-1">
                    {whyNotData.factors.emotions.your_favorites.slice(0, 3).map((e, idx) => (
                      <span key={idx} className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded text-xs">
                        {e.emotion} ({e.score}%)
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 mb-1">Емоції фільму:</p>
                  <div className="flex flex-wrap gap-1">
                    {whyNotData.factors.emotions.movie_emotions.slice(0, 3).map((e, idx) => (
                      <span
                        key={idx}
                        className={`px-2 py-1 rounded text-xs ${
                          whyNotData.factors.emotions.common_emotions.includes(e.emotion)
                            ? 'bg-green-900/30 text-green-300 border border-green-500/30'
                            : 'bg-gray-700 text-gray-300'
                        }`}
                      >
                        {e.emotion} ({e.score}%) {whyNotData.factors.emotions.common_emotions.includes(e.emotion) && '✓'}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Схожі користувачі */}
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h5 className="text-lg font-semibold text-white flex items-center gap-2">
                  👥 Схожі користувачі
                </h5>
                <span className="text-2xl font-bold text-green-400">
                  {whyNotData.factors.similar_users.match_percentage.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
                <div
                  className="bg-green-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${whyNotData.factors.similar_users.match_percentage}%` }}
                ></div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="text-center p-2 bg-green-900/20 rounded">
                  <div className="text-2xl font-bold text-green-400">
                    {whyNotData.factors.similar_users.positive_ratings}
                  </div>
                  <div className="text-xs text-gray-400">Оцінили 7+</div>
                </div>
                <div className="text-center p-2 bg-red-900/20 rounded">
                  <div className="text-2xl font-bold text-red-400">
                    {whyNotData.factors.similar_users.negative_ratings}
                  </div>
                  <div className="text-xs text-gray-400">Оцінили {'<'}7</div>
                </div>
              </div>
            </div>

            {/* Рейтинг */}
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <h5 className="text-lg font-semibold text-white flex items-center gap-2">
                  ⭐ Рейтинг
                </h5>
                <span className="text-2xl font-bold text-yellow-400">
                  {whyNotData.factors.rating.average.toFixed(1)}/10
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
                <div
                  className="bg-yellow-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(whyNotData.factors.rating.average / 10) * 100}%` }}
                ></div>
              </div>
              <div className="text-sm space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Якість:</span>
                  <span className="text-white font-medium">{whyNotData.factors.rating.quality}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Оцінок:</span>
                  <span className="text-white font-medium">{whyNotData.factors.rating.count}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Персональні інсайти */}
          {whyNotData.insights && whyNotData.insights.length > 0 && (
            <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-xl p-5 border border-blue-500/30">
              <h5 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                🎯 Персональні інсайти
              </h5>
              <div className="space-y-2">
                {whyNotData.insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-gray-300">
                    <span className="text-blue-400 mt-0.5">•</span>
                    <span>{insight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {whyNotData.already_watched && (
            <div className="bg-yellow-900/20 rounded-xl p-4 border border-yellow-500/30">
              <p className="text-yellow-300 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Ви вже переглянули цей фільм
              </p>
            </div>
          )}
        </div>
      )}

      {/* Counterfactual Results - Інтерактивні симуляції */}
      {activeTab === 'counterfactual' && counterfactual && !loading && (
        <div className="space-y-6">
          {/* Порівняння скорів */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
              <div className="text-sm text-gray-400 mb-2">Поточний скор</div>
              <div className="text-4xl font-bold text-white">
                {(counterfactual.current_score * 100).toFixed(0)}%
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mt-3">
                <div
                  className="bg-gray-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${counterfactual.current_score * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-xl p-5 border border-green-500/30">
              <div className="text-sm text-gray-400 mb-2">Потенційний скор</div>
              <div className="text-4xl font-bold text-green-400">
                {(counterfactual.potential_score * 100).toFixed(0)}%
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3 mt-3">
                <div
                  className="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${counterfactual.potential_score * 100}%` }}
                ></div>
              </div>
              {counterfactual.max_improvement > 0 && (
                <div className="text-sm text-green-300 mt-2">
                  ⬆️ +{counterfactual.max_improvement}% покращення
                </div>
              )}
            </div>
          </div>

          {/* Інтерактивні фактори */}
          <div className="space-y-4">
            <h5 className="text-lg font-semibold text-white flex items-center gap-2">
              🎮 Інтерактивні симуляції
            </h5>
            {counterfactual.factors && counterfactual.factors.map((factor, idx) => (
              <div key={idx} className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{factor.icon}</span>
                    <div>
                      <h6 className="text-white font-semibold">{factor.label}</h6>
                      <p className="text-xs text-gray-400">{factor.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">Вплив</div>
                    <div className={`text-xl font-bold ${
                      factor.impact > 0 ? 'text-green-400' : factor.impact < 0 ? 'text-red-400' : 'text-gray-400'
                    }`}>
                      {factor.impact > 0 ? '+' : ''}{factor.impact}%
                    </div>
                  </div>
                </div>
                
                {/* Візуальне порівняння */}
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <div className="text-xs text-gray-400 mb-2">Зараз</div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${factor.current_value}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-white mt-1">{factor.current_value}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-2">Потенціал</div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${factor.potential_value}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-green-400 mt-1">{factor.potential_value}%</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Топ рекомендації */}
          {counterfactual.top_changes && counterfactual.top_changes.length > 0 && (
            <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-xl p-5 border border-purple-500/30">
              <h5 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                🎯 Топ-3 найбільш впливових змін
              </h5>
              <div className="space-y-2">
                {counterfactual.top_changes.map((change, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-gray-300">
                    <span className="text-2xl">{change.icon}</span>
                    <span className="flex-1">{change.description}</span>
                    <span className={`font-bold ${
                      change.impact > 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {change.impact > 0 ? '+' : ''}{change.impact}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Текстові поради */}
          {counterfactual.suggestions && counterfactual.suggestions.length > 0 && (
            <div className="bg-blue-900/20 rounded-xl p-5 border border-blue-500/30">
              <h5 className="text-lg font-semibold text-white mb-3">💡 Поради</h5>
              <div className="space-y-2">
                {counterfactual.suggestions.map((suggestion, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-gray-300">
                    <span className="text-blue-400 mt-1">•</span>
                    <span>{suggestion}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Alternatives Results - Порівняльна таблиця */}
      {activeTab === 'alternatives' && alternativesData && !loading && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-blue-400" />
              <h4 className="text-lg font-semibold text-white">
                Альтернативні рекомендації
              </h4>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => fetchAlternatives('different_genre')}
                className={`px-4 py-2 text-sm rounded-lg transition-all ${
                  selectedAlternativeType === 'different_genre'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Інші жанри
              </button>
              <button
                onClick={() => fetchAlternatives('different_emotion')}
                className={`px-4 py-2 text-sm rounded-lg transition-all ${
                  selectedAlternativeType === 'different_emotion'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Інші емоції
              </button>
            </div>
          </div>

          {/* Пояснення */}
          {alternativesData.explanation && (
            <div className="p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
              <p className="text-blue-300 text-sm">{alternativesData.explanation}</p>
            </div>
          )}

          {alternativesData.alternatives && alternativesData.alternatives.length > 0 ? (
            <>
              {/* Порівняльна таблиця (desktop) */}
              <div className="hidden lg:block overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="text-left p-3 text-gray-400 font-semibold">Параметр</th>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => (
                        <th key={idx} className="p-3 text-center">
                          <Link to={`/movies/${item.movie.id}`} className="block hover:opacity-80 transition-opacity">
                            {item.movie.poster_url ? (
                              <img
                                src={item.movie.poster_url}
                                alt={item.movie.title}
                                className="w-20 h-28 object-cover rounded mx-auto mb-2"
                              />
                            ) : (
                              <div className="w-20 h-28 bg-gray-700 rounded mx-auto mb-2"></div>
                            )}
                            <div className="text-sm text-white font-medium line-clamp-2">{item.movie.title}</div>
                          </Link>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {/* Рейтинг */}
                    <tr className="border-b border-gray-700/50">
                      <td className="p-3 text-gray-400">⭐ Рейтинг</td>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => (
                        <td key={idx} className="p-3 text-center">
                          <div className="text-yellow-400 font-bold">
                            {item.movie.average_rating ? item.movie.average_rating.toFixed(1) : 'N/A'}
                          </div>
                        </td>
                      ))}
                    </tr>
                    {/* Жанри */}
                    <tr className="border-b border-gray-700/50">
                      <td className="p-3 text-gray-400">🎬 Жанри</td>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => (
                        <td key={idx} className="p-3">
                          <div className="flex flex-wrap gap-1 justify-center">
                            {item.movie.genres && item.movie.genres.slice(0, 2).map((genre, gIdx) => (
                              <span key={gIdx} className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded text-xs">
                                {genre}
                              </span>
                            ))}
                          </div>
                        </td>
                      ))}
                    </tr>
                    {/* Тривалість */}
                    <tr className="border-b border-gray-700/50">
                      <td className="p-3 text-gray-400">⏱️ Тривалість</td>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => (
                        <td key={idx} className="p-3 text-center text-gray-300">
                          {item.movie.duration ? `${item.movie.duration} хв` : 'N/A'}
                        </td>
                      ))}
                    </tr>
                    {/* Рік */}
                    <tr className="border-b border-gray-700/50">
                      <td className="p-3 text-gray-400">📅 Рік</td>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => (
                        <td key={idx} className="p-3 text-center text-gray-300">
                          {item.movie.year || 'N/A'}
                        </td>
                      ))}
                    </tr>
                    {/* Емоції */}
                    <tr>
                      <td className="p-3 text-gray-400">😊 Топ емоція</td>
                      {alternativesData.alternatives.slice(0, 4).map((item, idx) => {
                        const topEmotion = item.movie.emotions 
                          ? Object.entries(item.movie.emotions).sort((a, b) => b[1] - a[1])[0]
                          : null;
                        return (
                          <td key={idx} className="p-3 text-center">
                            {topEmotion ? (
                              <span className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded text-xs">
                                {topEmotion[0]} ({Math.round(topEmotion[1] * 100)}%)
                              </span>
                            ) : (
                              <span className="text-gray-500">N/A</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Картки (mobile) */}
              <div className="lg:hidden grid grid-cols-2 sm:grid-cols-3 gap-4">
                {alternativesData.alternatives.map((item) => (
                  <div key={item.movie.id} className="relative">
                    <MovieCard movie={item.movie} />
                    <div className="mt-2 space-y-1 text-xs">
                      <div className="flex justify-between text-gray-400">
                        <span>⭐</span>
                        <span className="text-yellow-400 font-bold">
                          {item.movie.average_rating ? item.movie.average_rating.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                      {item.movie.duration && (
                        <div className="flex justify-between text-gray-400">
                          <span>⏱️</span>
                          <span>{item.movie.duration} хв</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-center py-8">Немає альтернатив для відображення</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ExplainableAI;
