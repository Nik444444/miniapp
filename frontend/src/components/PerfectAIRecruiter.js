import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Bot, Brain, MessageCircle, Star, Sparkles,
    Languages, FileText, Send, ArrowRight,
    CheckCircle, Clock, Target, Zap, Briefcase,
    User, Globe, Award, TrendingUp, Heart,
    ThumbsUp, MessageSquare, Bell, Settings,
    RotateCcw, Plus, Minus, Eye, X, AlertCircle,
    Rocket, Trophy, ChevronRight, ArrowLeft
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    hapticFeedback, 
    telegramWebApp,
    showBackButton,
    hideBackButton 
} from '../utils/telegramWebApp';

const PerfectAIRecruiter = ({ onBack, initialJob = null }) => {
    const { user, backendUrl } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('chat');
    const [loading, setLoading] = useState(false);
    
    // Perfect AI Recruiter Chat State
    const [aiProfile, setAiProfile] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');
    const [conversationStarted, setConversationStarted] = useState(false);
    const [progress, setProgress] = useState(0);
    const [stage, setStage] = useState('greeting');
    
    // Job Analysis State
    const [selectedJob, setSelectedJob] = useState(initialJob);
    const [compatibilityScore, setCompatibilityScore] = useState(null);
    const [translatedJob, setTranslatedJob] = useState(null);
    const [coverLetter, setCoverLetter] = useState(null);
    const [jobRecommendations, setJobRecommendations] = useState([]);
    
    // UI State
    const [isTyping, setIsTyping] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [selectedLanguage, setSelectedLanguage] = useState('ru');
    
    const languages = [
        { code: 'ru', name: 'Русский', flag: '🇷🇺' },
        { code: 'en', name: 'English', flag: '🇺🇸' },
        { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
        { code: 'uk', name: 'Українська', flag: '🇺🇦' }
    ];

    useEffect(() => {
        console.log('🎯 Perfect AI Recruiter mounted');
        if (isTelegramWebApp()) {
            showBackButton();
            telegramWebApp.BackButton.onClick(() => {
                hapticFeedback('impact', 'light');
                onBack();
            });
        }
        
        loadAIProfile();
        
        return () => {
            if (isTelegramWebApp()) {
                hideBackButton();
            }
        };
    }, []);

    const loadAIProfile = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/ai-recruiter/profile`, {
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    setAiProfile(data.profile);
                    setConversationStarted(true);
                    setProgress(data.profile.progress || 0);
                    setStage(data.profile.stage || 'greeting');
                    
                    // Конвертируем историю разговора в нужный формат
                    const messages = [];
                    const conversation = data.profile.conversation || [];
                    
                    conversation.forEach(conv => {
                        if (conv.user_message) {
                            messages.push({
                                type: 'user',
                                message: conv.user_message,
                                timestamp: conv.timestamp
                            });
                        }
                        if (conv.ai_message) {
                            messages.push({
                                type: 'ai',
                                message: conv.ai_message,
                                timestamp: conv.timestamp
                            });
                        }
                    });
                    
                    setChatMessages(messages);
                }
            }
        } catch (error) {
            console.error('Failed to load AI profile:', error);
        }
    };

    const startAIRecruiter = async () => {
        setLoading(true);
        setError(null);
        
        try {
            hapticFeedback('impact', 'medium');
            
            const response = await fetch(`${backendUrl}/api/ai-recruiter/start`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_language: selectedLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setAiProfile(data.profile);
                setConversationStarted(true);
                setProgress(data.progress || 0);
                setStage(data.stage || 'greeting');
                
                // Добавляем первое сообщение AI
                setChatMessages([{
                    type: 'ai',
                    message: data.ai_message,
                    timestamp: new Date().toISOString()
                }]);
                
                if (data.is_complete && data.recommendations) {
                    setJobRecommendations(data.recommendations);
                }
                
                hapticFeedback('notification', 'success');
            } else {
                setError(data.message || 'Ошибка запуска AI-рекрутера');
            }
        } catch (error) {
            console.error('Failed to start AI recruiter:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setLoading(false);
        }
    };

    const sendMessage = async () => {
        if (!userMessage.trim() || loading || isTyping) return;
        
        const messageToSend = userMessage.trim();
        setUserMessage('');
        setIsTyping(true);
        setError(null);
        
        // Добавляем сообщение пользователя
        const newUserMessage = {
            type: 'user',
            message: messageToSend,
            timestamp: new Date().toISOString()
        };
        setChatMessages(prev => [...prev, newUserMessage]);
        
        try {
            hapticFeedback('impact', 'light');
            
            const response = await fetch(`${backendUrl}/api/ai-recruiter/continue`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_message: messageToSend
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Добавляем ответ AI
                const newAiMessage = {
                    type: 'ai',
                    message: data.ai_message,
                    timestamp: new Date().toISOString()
                };
                setChatMessages(prev => [...prev, newAiMessage]);
                
                setAiProfile(data.profile);
                setProgress(data.progress || 0);
                setStage(data.stage || 'greeting');
                
                if (data.is_complete) {
                    setSuccess('🎉 Профиль завершен! Вот ваши персональные рекомендации:');
                    if (data.recommendations) {
                        setJobRecommendations(data.recommendations);
                        setCurrentView('recommendations');
                    }
                }
                
                hapticFeedback('notification', 'success');
            } else {
                setError(data.message || 'Ошибка обработки сообщения');
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setIsTyping(false);
        }
    };

    const analyzeJobCompatibility = async (job) => {
        if (!aiProfile) {
            setError('Сначала завершите анкетирование с AI-рекрутером');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${backendUrl}/api/job-compatibility`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: job.id || 'temp_id',
                    job_data: job
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setCompatibilityScore(data.analysis);
                setSelectedJob(job);
                setCurrentView('analysis');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
            } else {
                setError(data.message || 'Ошибка анализа совместимости');
            }
        } catch (error) {
            console.error('Failed to analyze compatibility:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setLoading(false);
        }
    };

    const translateJob = async (job, targetLanguage) => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${backendUrl}/api/translate-job`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: job.id || 'temp_id',
                    job_data: job,
                    target_language: targetLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setTranslatedJob(data.translated_job);
                setCurrentView('translation');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
            } else {
                setError(data.message || 'Ошибка перевода вакансии');
            }
        } catch (error) {
            console.error('Failed to translate job:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setLoading(false);
        }
    };

    const generateCoverLetter = async (job, style = 'professional') => {
        if (!aiProfile) {
            setError('Сначала завершите анкетирование с AI-рекрутером');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${backendUrl}/api/generate-cover-letter`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_id: job.id || 'temp_id',
                    job_data: job,
                    style: style
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setCoverLetter(data.cover_letter);
                setCurrentView('cover-letter');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
            } else {
                setError(data.message || 'Ошибка генерации сопроводительного письма');
            }
        } catch (error) {
            console.error('Failed to generate cover letter:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setLoading(false);
        }
    };

    const getJobRecommendations = async () => {
        if (!aiProfile) {
            setError('Сначала завершите анкетирование с AI-рекрутером');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${backendUrl}/api/ai-job-recommendations`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_profile_id: user.id,
                    max_jobs: 5
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setJobRecommendations(data.recommendations);
                setCurrentView('recommendations');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
            } else {
                setError(data.message || 'Ошибка получения рекомендаций');
            }
        } catch (error) {
            console.error('Failed to get recommendations:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setLoading(false);
        }
    };

    const renderChat = () => (
        <div className="flex flex-col h-full bg-gradient-to-br from-blue-50 to-indigo-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                        <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h2 className="font-bold text-lg text-gray-900 flex items-center">
                            🎯 Идеальный AI-Рекрутер
                            {stage === 'complete' && <Trophy className="w-5 h-5 text-yellow-500 ml-2" />}
                        </h2>
                        <p className="text-sm text-gray-600">
                            {conversationStarted ? 
                                `${stage === 'greeting' ? 'Знакомство' : stage === 'skills' ? 'Навыки и опыт' : 'Готов к поиску'} • ${progress}% завершено` 
                                : 'Персональный помощник по поиску работы'
                            }
                        </p>
                    </div>
                </div>
                
                {progress > 0 && (
                    <div className="mt-3">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>Прогресс анкетирования</span>
                            <span>{progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {!conversationStarted ? (
                    <div className="text-center py-8">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Rocket className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">🎯 Добро пожаловать!</h3>
                        <p className="text-gray-600 mb-6">
                            Я ваш идеальный AI-рекрутер. Найду идеальную работу в Германии всего за 3 простых вопроса!
                        </p>
                        
                        {/* Language Selection */}
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">Выберите язык общения:</label>
                            <select 
                                value={selectedLanguage}
                                onChange={(e) => setSelectedLanguage(e.target.value)}
                                className="block w-full max-w-xs mx-auto p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                                {languages.map(lang => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.flag} {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        
                        <button
                            onClick={startAIRecruiter}
                            disabled={loading}
                            className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center gap-2 mx-auto"
                        >
                            {loading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    Запуск...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    Начать с идеальным AI-рекрутером
                                </>
                            )}
                        </button>
                    </div>
                ) : (
                    chatMessages.map((msg, index) => (
                        <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                msg.type === 'user' 
                                    ? 'bg-blue-500 text-white rounded-br-sm' 
                                    : 'bg-white text-gray-900 border rounded-bl-sm shadow-sm'
                            }`}>
                                <div className="whitespace-pre-wrap">{msg.message}</div>
                                <div className={`text-xs mt-1 ${msg.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))
                )}
                
                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-white text-gray-900 border rounded-lg px-4 py-2 shadow-sm">
                            <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Message Input */}
            {conversationStarted && (
                <div className="bg-white border-t border-gray-200 p-4">
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={userMessage}
                            onChange={(e) => setUserMessage(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Введите ваш ответ..."
                            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                            disabled={loading || isTyping}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!userMessage.trim() || loading || isTyping}
                            className="bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );

    const renderRecommendations = () => (
        <div className="bg-white min-h-screen">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6">
                <h2 className="text-xl font-bold flex items-center">
                    <Star className="w-6 h-6 mr-2" />
                    🎯 Идеальные рекомендации
                </h2>
                <p className="text-emerald-100 mt-2">Персональные рекомендации на основе вашего профиля</p>
            </div>

            {/* Job Recommendations */}
            <div className="p-6 space-y-4">
                {jobRecommendations.length === 0 ? (
                    <div className="text-center py-8">
                        <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">Нет рекомендаций</h3>
                        <p className="text-gray-600">Завершите анкетирование, чтобы получить персональные рекомендации</p>
                        <button
                            onClick={getJobRecommendations}
                            disabled={loading}
                            className="mt-4 bg-emerald-500 text-white px-6 py-2 rounded-lg font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50"
                        >
                            🔄 Обновить рекомендации
                        </button>
                    </div>
                ) : (
                    jobRecommendations.map((rec, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <h3 className="font-bold text-lg text-gray-900">{rec.job?.title}</h3>
                                    <p className="text-gray-600">{rec.job?.company_name}</p>
                                    <p className="text-gray-500 text-sm">{rec.job?.location}</p>
                                </div>
                                
                                <div className="text-right">
                                    <div className="text-2xl font-bold text-emerald-600">
                                        {rec.compatibility_score}%
                                    </div>
                                    <div className="text-xs text-gray-500">совместимость</div>
                                </div>
                            </div>

                            {rec.job?.description && (
                                <p className="text-gray-700 text-sm line-clamp-3">{rec.job.description}</p>
                            )}

                            {rec.match_reasons && rec.match_reasons.length > 0 && (
                                <div className="bg-green-50 p-3 rounded-lg">
                                    <p className="text-sm font-medium text-green-800 mb-1">✅ Ваши преимущества:</p>
                                    <ul className="text-sm text-green-700 list-disc list-inside">
                                        {rec.match_reasons.slice(0, 2).map((reason, idx) => (
                                            <li key={idx}>{reason}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-2 pt-2">
                                <button
                                    onClick={() => analyzeJobCompatibility(rec.job)}
                                    className="flex-1 bg-blue-500 text-white py-2 px-3 rounded text-sm font-medium hover:bg-blue-600 transition-colors"
                                >
                                    📊 Анализ
                                </button>
                                
                                <button
                                    onClick={() => generateCoverLetter(rec.job)}
                                    className="flex-1 bg-indigo-500 text-white py-2 px-3 rounded text-sm font-medium hover:bg-indigo-600 transition-colors"
                                >
                                    📝 Письмо
                                </button>
                                
                                <button
                                    onClick={() => {
                                        setSelectedJob(rec.job);
                                        translateJob(rec.job, selectedLanguage);
                                    }}
                                    className="flex-1 bg-purple-500 text-white py-2 px-3 rounded text-sm font-medium hover:bg-purple-600 transition-colors"
                                >
                                    🌍 Перевод
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Actions */}
            <div className="p-6 border-t border-gray-200 space-y-3">
                <button
                    onClick={() => setCurrentView('chat')}
                    className="w-full bg-gray-500 text-white py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors flex items-center justify-center"
                >
                    <ArrowLeft className="w-4 w-4 mr-2" />
                    Вернуться к чату
                </button>
            </div>
        </div>
    );

    const renderNavigation = () => (
        <div className="bg-white border-t border-gray-200 px-4 py-2">
            <div className="flex space-x-1">
                <button
                    onClick={() => setCurrentView('chat')}
                    className={`flex-1 py-3 px-2 rounded-lg text-sm font-medium transition-colors ${
                        currentView === 'chat' 
                            ? 'bg-blue-500 text-white' 
                            : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                    <MessageCircle className="w-5 h-5 mx-auto mb-1" />
                    Чат
                </button>
                
                <button
                    onClick={() => setCurrentView('recommendations')}
                    className={`flex-1 py-3 px-2 rounded-lg text-sm font-medium transition-colors ${
                        currentView === 'recommendations' 
                            ? 'bg-emerald-500 text-white' 
                            : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                    <Star className="w-5 h-5 mx-auto mb-1" />
                    Рекомендации
                </button>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Error & Success Messages */}
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mx-4 mt-4 rounded relative">
                    <div className="flex justify-between items-center">
                        <span>{error}</span>
                        <button onClick={() => setError(null)} className="text-red-700 hover:text-red-900">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}
            
            {success && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 mx-4 mt-4 rounded relative">
                    <div className="flex justify-between items-center">
                        <span>{success}</span>
                        <button onClick={() => setSuccess(null)} className="text-green-700 hover:text-green-900">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="flex-1">
                {currentView === 'chat' && renderChat()}
                {currentView === 'recommendations' && renderRecommendations()}
            </div>

            {/* Navigation */}
            {renderNavigation()}
        </div>
    );
};

export default PerfectAIRecruiter;