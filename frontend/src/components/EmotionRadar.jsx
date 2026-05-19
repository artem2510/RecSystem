import { useEffect, useState } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const EmotionRadar = ({ emotionData }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (emotionData && emotionData.emotions) {
      // Перетворюємо дані для радар-чарту
      const data = [
        { emotion: 'Оптимізм', value: emotionData.emotions['оптимістичний'] * 100, fullMark: 100 },
        { emotion: 'Драма', value: emotionData.emotions['драматичний'] * 100, fullMark: 100 },
        { emotion: 'Напруга', value: emotionData.emotions['напружений'] * 100, fullMark: 100 },
        { emotion: 'Романтика', value: emotionData.emotions['романтичний'] * 100, fullMark: 100 },
        { emotion: 'Жахи', value: emotionData.emotions['жахливий'] * 100, fullMark: 100 },
        { emotion: 'Пригоди', value: emotionData.emotions['пригодницький'] * 100, fullMark: 100 }
      ];
      setChartData(data);
    }
  }, [emotionData]);

  if (!emotionData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <p>Недостатньо даних для аналізу</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-white mb-2">
          {emotionData.emotion_type}
        </h3>
        <p className="text-gray-400 text-sm">
          {emotionData.description}
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis 
            dataKey="emotion" 
            tick={{ fill: '#9CA3AF', fontSize: 12 }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]}
            tick={{ fill: '#9CA3AF', fontSize: 10 }}
          />
          <Radar
            name="Емоційний профіль"
            dataKey="value"
            stroke="#8B5CF6"
            fill="#8B5CF6"
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#F3F4F6'
            }}
            formatter={(value) => `${value.toFixed(1)}%`}
          />
          <Legend 
            wrapperStyle={{ color: '#9CA3AF' }}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Домінуючі емоції */}
      {emotionData.dominant_emotions && emotionData.dominant_emotions.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-gray-400 mb-3">Ваші домінуючі емоції:</h4>
          <div className="flex flex-wrap gap-2">
            {emotionData.dominant_emotions.map((emotion, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm border border-primary-500/30"
              >
                {emotion}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Статистика */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
          <div className="text-2xl font-bold text-white">
            {emotionData.total_movies_analyzed}
          </div>
          <div className="text-xs text-gray-400">Проаналізовано фільмів</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
          <div className="text-2xl font-bold text-white">
            {(emotionData.diversity_score * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-400">Різноманітність смаків</div>
        </div>
      </div>
    </div>
  );
};

export default EmotionRadar;
