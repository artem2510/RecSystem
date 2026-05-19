import { useState, useEffect } from 'react';
import { BarChart3, Heart, Eye, TrendingUp, Sparkles, Trophy, Target, Award, Clock } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import EmotionRadar from '../components/EmotionRadar';
import api from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [emotionProfile, setEmotionProfile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingEmotions, setLoadingEmotions] = useState(true);
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchEmotionProfile();
    fetchAnalytics();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmotionProfile = async () => {
    try {
      const response = await api.get('/emotions/profile');
      setEmotionProfile(response.data);
    } catch (err) {
      console.error('Failed to fetch emotion profile:', err);
    } finally {
      setLoadingEmotions(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/dashboard/analytics');
      setAnalytics(response.data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <BarChart3 className="w-8 h-8 text-primary-500" />
        <h1 className="text-3xl font-bold text-white">Ваша статистика</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Heart className="w-8 h-8" />}
          title="Оцінено фільмів"
          value={stats?.ratings_count || 0}
          color="text-red-500"
        />
        <StatCard
          icon={<Eye className="w-8 h-8" />}
          title="Переглянуто"
          value={stats?.views_count || 0}
          color="text-blue-500"
        />
        <StatCard
          icon={<TrendingUp className="w-8 h-8" />}
          title="Середня оцінка"
          value={stats?.average_rating?.toFixed(1) || '0.0'}
          color="text-green-500"
        />
        <StatCard
          icon={<BarChart3 className="w-8 h-8" />}
          title="Улюблений жанр"
          value={stats?.favorite_genre || 'Немає'}
          color="text-purple-500"
        />
      </div>

      {/* Емоційний профіль */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-6">
            <Sparkles className="w-6 h-6 text-purple-500" />
            <h2 className="text-2xl font-bold text-white">Ваш емоційний профіль</h2>
          </div>
          {loadingEmotions ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <EmotionRadar emotionData={emotionProfile} />
          )}
        </div>

        <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-4">Ваші вподобання</h2>
          <p className="text-gray-400 mb-6">
            Продовжуйте оцінювати фільми, щоб отримувати кращі рекомендації!
          </p>
          
          {/* Додаткова інформація */}
          {emotionProfile && emotionProfile.total_movies_analyzed > 0 && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <h3 className="text-sm font-semibold text-gray-400 mb-2">Ваш тип глядача</h3>
                <p className="text-lg font-bold text-primary-400">{emotionProfile.emotion_type}</p>
              </div>
              
              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <h3 className="text-sm font-semibold text-gray-400 mb-2">Рівень різноманітності</h3>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-primary-500 to-purple-500 h-2 rounded-full transition-all"
                      style={{ width: `${emotionProfile.diversity_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-white font-semibold">
                    {(emotionProfile.diversity_score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {emotionProfile.diversity_score > 0.7 
                    ? "Ви любите різноманітні фільми!" 
                    : emotionProfile.diversity_score > 0.4
                    ? "У вас збалансовані вподобання"
                    : "Ви знаєте, що любите!"}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Досягнення */}
      {analytics && analytics.achievements && analytics.achievements.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Trophy className="w-6 h-6 text-yellow-500" />
            <h2 className="text-2xl font-bold text-white">Досягнення</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analytics.achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-xl border ${
                  achievement.unlocked
                    ? 'bg-gradient-to-br from-yellow-900/30 to-orange-900/30 border-yellow-500/50'
                    : 'bg-gray-800 border-gray-700 opacity-60'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="text-4xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-white mb-1">{achievement.title}</h3>
                    <p className="text-sm text-gray-400 mb-2">{achievement.description}</p>
                    {!achievement.unlocked && (
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-yellow-500 h-2 rounded-full transition-all"
                          style={{ width: `${achievement.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Цілі */}
      {analytics && analytics.goals_progress && analytics.goals_progress.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Target className="w-6 h-6 text-blue-500" />
            <h2 className="text-2xl font-bold text-white">Ваші цілі</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {analytics.goals_progress.map((goal) => (
              <div key={goal.id} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div className="flex items-center gap-3 mb-4">
                  <div className="text-3xl">{goal.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-bold text-white">{goal.title}</h3>
                    <p className="text-sm text-gray-400">
                      {goal.current} / {goal.target}
                    </p>
                  </div>
                  <div className="text-2xl font-bold text-primary-400">
                    {goal.progress.toFixed(0)}%
                  </div>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-primary-500 to-purple-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min(goal.progress, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Графіки */}
      {analytics && analytics.timeline_stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Активність в часі */}
          <div className="bg-gray-800 rounded-xl p-4 sm:p-6 border border-gray-700">
            <h3 className="text-lg sm:text-xl font-bold text-white mb-4">Активність за рік</h3>
            <div className="w-full overflow-x-auto">
              <ResponsiveContainer width="100%" height={250} minWidth={300}>
                <LineChart data={analytics.timeline_stats.timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="month" stroke="#9CA3AF" fontSize={10} angle={-45} textAnchor="end" height={60} />
                  <YAxis stroke="#9CA3AF" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1F2937',
                      border: '1px solid #374151',
                      borderRadius: '8px',
                      color: '#F3F4F6',
                      fontSize: '12px'
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Line
                    type="monotone"
                    dataKey="ratings_count"
                    stroke="#8B5CF6"
                    strokeWidth={2}
                    name="Оцінено фільмів"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Розподіл жанрів */}
          {analytics.genre_distribution && analytics.genre_distribution.genres && (
            <div className="bg-gray-800 rounded-xl p-4 sm:p-6 border border-gray-700">
              <h3 className="text-lg sm:text-xl font-bold text-white mb-4">Топ жанрів</h3>
              <div className="w-full overflow-x-auto">
                <ResponsiveContainer width="100%" height={250} minWidth={300}>
                  <BarChart data={analytics.genre_distribution.genres.slice(0, 6)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="genre" stroke="#9CA3AF" fontSize={10} angle={-45} textAnchor="end" height={60} />
                    <YAxis stroke="#9CA3AF" fontSize={10} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1F2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#F3F4F6',
                        fontSize: '12px'
                      }}
                    />
                    <Bar dataKey="count" fill="#8B5CF6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Соціальні метрики та прогнози */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Соціальні метрики */}
          {analytics.social_metrics && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Порівняння з іншими</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Ваша середня оцінка:</span>
                  <span className="text-2xl font-bold text-white">{analytics.social_metrics.user_average}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Середня всіх користувачів:</span>
                  <span className="text-2xl font-bold text-gray-500">{analytics.social_metrics.global_average}</span>
                </div>
                <div className="p-3 bg-primary-900/30 rounded-lg border border-primary-500/30">
                  <p className="text-primary-300 text-sm">{analytics.social_metrics.comparison}</p>
                </div>
                <div className="p-3 bg-purple-900/30 rounded-lg border border-purple-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-purple-300 text-sm">Унікальність смаків:</span>
                    <span className="text-purple-300 font-bold">{analytics.social_metrics.uniqueness_score}%</span>
                  </div>
                  <p className="text-purple-300 text-xs">{analytics.social_metrics.uniqueness_description}</p>
                </div>
              </div>
            </div>
          )}

          {/* Прогнози */}
          {analytics.predictions && (
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Прогнози</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-900/30 rounded-lg border border-blue-500/30">
                  <div className="flex items-center gap-3 mb-2">
                    <Clock className="w-5 h-5 text-blue-400" />
                    <span className="text-blue-300 font-semibold">Наступний місяць</span>
                  </div>
                  <p className="text-white text-2xl font-bold mb-1">
                    ~{analytics.predictions.predicted_monthly_views} фільмів
                  </p>
                  <p className="text-blue-300 text-sm">Очікувана кількість переглядів</p>
                </div>
                {analytics.predictions.trending_genre && (
                  <div className="p-4 bg-green-900/30 rounded-lg border border-green-500/30">
                    <div className="flex items-center gap-3 mb-2">
                      <TrendingUp className="w-5 h-5 text-green-400" />
                      <span className="text-green-300 font-semibold">Тренд</span>
                    </div>
                    <p className="text-white text-lg font-bold mb-1">{analytics.predictions.trending_genre}</p>
                    <p className="text-green-300 text-sm">{analytics.predictions.trend_description}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, title, value, color }) {
  return (
    <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
      <div className={`${color} mb-2`}>{icon}</div>
      <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
      <p className="text-3xl font-bold text-white mt-2">{value}</p>
    </div>
  );
}
