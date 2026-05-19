import { useState, useEffect } from 'react';
import api from '../services/api';

const MoodSelector = ({ onMoodSelect, selectedMood }) => {
  const [moods, setMoods] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMoods();
  }, []);

  const fetchMoods = async () => {
    try {
      const response = await api.get('/recommendations/moods');
      setMoods(response.data.moods);
    } catch (error) {
      console.error('Failed to fetch moods:', error);
      // Fallback moods
      setMoods([
        { value: 'happy', label: 'Щасливий 😊', emoji: '😊' },
        { value: 'sad', label: 'Сумний 😢', emoji: '😢' },
        { value: 'stressed', label: 'Стресовий 😰', emoji: '😰' },
        { value: 'bored', label: 'Нудно 😑', emoji: '😑' },
        { value: 'romantic', label: 'Романтичний 💕', emoji: '💕' },
        { value: 'adventurous', label: 'Пригодницький 🗺️', emoji: '🗺️' },
        { value: 'thoughtful', label: 'Задумливий 🤔', emoji: '🤔' },
        { value: 'scared', label: 'Моторошно 👻', emoji: '👻' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-white">Який у вас зараз настрій?</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {moods.map((mood) => (
          <button
            key={mood.value}
            onClick={() => onMoodSelect(mood.value)}
            className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
              selectedMood === mood.value
                ? 'border-primary-500 bg-primary-500/20 shadow-lg shadow-primary-500/50'
                : 'border-gray-700 bg-gray-800 hover:border-primary-400'
            }`}
          >
            <div className="text-4xl mb-2">{mood.emoji}</div>
            <div className="text-sm font-medium text-white">
              {mood.label.replace(mood.emoji, '').trim()}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MoodSelector;
