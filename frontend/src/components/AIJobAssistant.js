import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Bot, Brain, MessageCircle, Star, Sparkles,
    Languages, FileText, Send, ArrowRight,
    CheckCircle, Clock, Target, Zap, Briefcase,
    User, Globe, Award, TrendingUp, Heart,
    ThumbsUp, MessageSquare, Bell, Settings,
    RotateCcw, Plus, Minus, Eye, X, AlertCircle
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    hapticFeedback, 
    telegramWebApp,
    showBackButton,
    hideBackButton 
} from '../utils/telegramWebApp';

const AIJobAssistant = ({ onBack, initialJob = null }) => {
    const { user, backendUrl } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('chat');
    const [loading, setLoading] = useState(false);
    
    // AI Recruiter Chat State
    const [aiProfile, setAiProfile] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');
    const [conversationStarted, setConversationStarted] = useState(false);
    const [progress, setProgress] = useState(0);
    const [stage, setStage] = useState('initial');
    
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
        { code: 'uk', name: 'Українська', flag: '🇺🇦' },
        { code: 'es', name: 'Español', flag: '🇪🇸' },
        { code: 'fr', name: 'Français', flag: '🇫🇷' }
    ];

    useEffect(() => {
        console.log('🤖 AI Job Assistant mounted');
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
            const response = await fetch(`${backendUrl}/ai-recruiter/profile`, {
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
                    setStage(data.profile.stage || 'initial');
                    setChatMessages(data.profile.conversation_history || []);
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
            const response = await fetch(`${backendUrl}/ai-recruiter/start`, {
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
                setProgress(data.progress);
                setStage(data.stage);
                
                // Add AI message to chat
                const aiMessage = {
                    type: 'ai',
                    message: data.ai_message,
                    timestamp: new Date().toISOString(),
                    stage: data.stage
                };
                
                setChatMessages([aiMessage]);
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
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
        if (!userMessage.trim() || loading) return;
        
        const messageToSend = userMessage;
        setUserMessage('');
        setIsTyping(true);
        setError(null);
        
        // Add user message to chat
        const newUserMessage = {
            type: 'user',
            message: messageToSend,
            timestamp: new Date().toISOString()
        };
        
        setChatMessages(prev => [...prev, newUserMessage]);
        
        try {
            const response = await fetch(`${backendUrl}/ai-recruiter/continue`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_message: messageToSend,
                    conversation_data: aiProfile
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setAiProfile(data.profile);
                setProgress(data.progress);
                setStage(data.stage);
                
                // Add AI response to chat
                const aiMessage = {
                    type: 'ai',
                    message: data.ai_message,
                    timestamp: new Date().toISOString(),
                    stage: data.stage
                };
                
                setChatMessages(prev => [...prev, aiMessage]);
                
                if (data.is_complete) {
                    setSuccess('Профиль завершен! Теперь вы можете получать персональные рекомендации.');
                    getJobRecommendations();
                }
                
                if (isTelegramWebApp()) {
                    hapticFeedback('impact', 'light');
                }
            } else {
                setError(data.message || 'Ошибка отправки сообщения');
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
            const response = await fetch(`${backendUrl}/job-compatibility`, {
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
                setCompatibilityScore(data.compatibility);
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
            const response = await fetch(`${backendUrl}/translate-job`, {
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

    const generateCoverLetter = async (job) => {
        if (!aiProfile) {
            setError('Сначала завершите анкетирование с AI-рекрутером');
            return;
        }
        
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(`${backendUrl}/generate-cover-letter`, {
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
            const response = await fetch(`${backendUrl}/ai-job-recommendations`, {
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

    const sendTelegramNotification = async (notificationType, jobData = null, additionalData = null) => {
        if (!user.telegram_id) {
            setError('Telegram ID не найден. Войдите через Telegram Mini App.');
            return;
        }
        
        setLoading(true);
        
        try {
            const response = await fetch(`${backendUrl}/telegram-notifications/send`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_telegram_id: user.telegram_id,
                    notification_type: notificationType,
                    job_data: jobData,
                    additional_data: additionalData,
                    user_language: selectedLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                setSuccess('Уведомление отправлено в Telegram!');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('notification', 'success');
                }
            } else {
                setError(data.message || 'Ошибка отправки уведомления');
            }
        } catch (error) {
            console.error('Failed to send notification:', error);
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
                        <h2 className="font-bold text-lg text-gray-900">AI-Рекрутер</h2>
                        <p className="text-sm text-gray-600">
                            {conversationStarted ? `${stage} • ${progress}% завершено` : 'Персональный помощник по поиску работы'}
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
                            <Sparkles className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Добро пожаловать!</h3>
                        <p className="text-gray-600 mb-6">Я ваш персональный AI-рекрутер. Помогу найти идеальную работу в Германии!</p>
                        
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
                            className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                        >
                            {loading ? 'Запуск...' : 'Начать беседу с AI-рекрутером'}
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

    const renderAnalysis = () => (
        <div className="bg-white min-h-screen">
            {/* Header */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-6">
                <div className="flex items-center space-x-3 mb-4">
                    <Target className="w-8 h-8" />
                    <div>
                        <h2 className="text-xl font-bold">Анализ совместимости</h2>
                        <p className="text-green-100">AI-оценка вашего соответствия вакансии</p>
                    </div>
                </div>
                
                {compatibilityScore && (
                    <div className="bg-white/20 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">Общий балл совместимости</span>
                            <span className="text-2xl font-bold">{compatibilityScore.overall_score}%</span>
                        </div>
                        <div className="w-full bg-white/30 rounded-full h-3">
                            <div 
                                className="bg-white h-3 rounded-full transition-all duration-500"
                                style={{ width: `${compatibilityScore.overall_score}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Job Info */}
            {selectedJob && (
                <div className="p-6 border-b border-gray-200">
                    <h3 className="font-bold text-lg text-gray-900 mb-2">{selectedJob.title}</h3>
                    <p className="text-gray-600 mb-1">{selectedJob.company_name}</p>
                    <p className="text-gray-500 text-sm">{selectedJob.location?.city || selectedJob.location}</p>
                </div>
            )}

            {/* Analysis Details */}
            {compatibilityScore && (
                <div className="p-6 space-y-6">
                    {/* Strengths */}
                    {compatibilityScore.strengths && compatibilityScore.strengths.length > 0 && (
                        <div>
                            <h4 className="font-bold text-green-600 mb-3 flex items-center">
                                <ThumbsUp className="w-5 h-5 mr-2" />
                                Ваши преимущества
                            </h4>
                            <ul className="space-y-2">
                                {compatibilityScore.strengths.map((strength, index) => (
                                    <li key={index} className="flex items-start space-x-2">
                                        <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span className="text-gray-700">{strength}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Weaknesses */}
                    {compatibilityScore.weaknesses && compatibilityScore.weaknesses.length > 0 && (
                        <div>
                            <h4 className="font-bold text-amber-600 mb-3 flex items-center">
                                <AlertCircle className="w-5 h-5 mr-2" />
                                Области для развития
                            </h4>
                            <ul className="space-y-2">
                                {compatibilityScore.weaknesses.map((weakness, index) => (
                                    <li key={index} className="flex items-start space-x-2">
                                        <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                                        <span className="text-gray-700">{weakness}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Recommendations */}
                    {compatibilityScore.recommendations && compatibilityScore.recommendations.length > 0 && (
                        <div>
                            <h4 className="font-bold text-blue-600 mb-3 flex items-center">
                                <Sparkles className="w-5 h-5 mr-2" />
                                Рекомендации
                            </h4>
                            <ul className="space-y-2">
                                {compatibilityScore.recommendations.map((rec, index) => (
                                    <li key={index} className="flex items-start space-x-2">
                                        <ArrowRight className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                                        <span className="text-gray-700">{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Actions */}
            <div className="p-6 border-t border-gray-200 space-y-3">
                <button
                    onClick={() => generateCoverLetter(selectedJob)}
                    disabled={loading}
                    className="w-full bg-blue-500 text-white py-3 rounded-lg font-medium hover:bg-blue-600 transition-colors disabled:opacity-50"
                >
                    📝 Сгенерировать сопроводительное письмо
                </button>
                
                <button
                    onClick={() => sendTelegramNotification('compatibility_alert', selectedJob, { compatibility_analysis: compatibilityScore })}
                    disabled={loading}
                    className="w-full bg-green-500 text-white py-3 rounded-lg font-medium hover:bg-green-600 transition-colors disabled:opacity-50"
                >
                    📱 Отправить в Telegram
                </button>
                
                <button
                    onClick={() => setCurrentView('chat')}
                    className="w-full bg-gray-500 text-white py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors"
                >
                    ← Вернуться к чату
                </button>
            </div>
        </div>
    );

    const renderTranslation = () => (
        <div className="bg-white min-h-screen">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-6">
                <h2 className="text-xl font-bold flex items-center">
                    <Globe className="w-6 h-6 mr-2" />
                    Перевод вакансии
                </h2>
                <p className="text-purple-100 mt-2">Перевод на выбранный язык</p>
            </div>

            {/* Language Selection */}
            <div className="p-6 border-b border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">Язык перевода:</label>
                <select 
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    className="block w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                >
                    {languages.map(lang => (
                        <option key={lang.code} value={lang.code}>
                            {lang.flag} {lang.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Translation Content */}
            {translatedJob && (
                <div className="p-6 space-y-6">
                    <div>
                        <h3 className="font-bold text-lg text-gray-900 mb-2">
                            {translatedJob.title || 'Переведенная вакансия'}
                        </h3>
                        <p className="text-gray-600 mb-1">{translatedJob.company_name}</p>
                        <p className="text-gray-500 text-sm">{translatedJob.location}</p>
                    </div>

                    {translatedJob.description && (
                        <div>
                            <h4 className="font-medium text-gray-900 mb-2">Описание:</h4>
                            <p className="text-gray-700 whitespace-pre-wrap">{translatedJob.description}</p>
                        </div>
                    )}

                    {translatedJob.full_translation && (
                        <div>
                            <h4 className="font-medium text-gray-900 mb-2">Полный перевод:</h4>
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-gray-700 whitespace-pre-wrap">{translatedJob.full_translation}</p>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Actions */}
            <div className="p-6 border-t border-gray-200 space-y-3">
                {selectedJob && (
                    <button
                        onClick={() => translateJob(selectedJob, selectedLanguage)}
                        disabled={loading}
                        className="w-full bg-purple-500 text-white py-3 rounded-lg font-medium hover:bg-purple-600 transition-colors disabled:opacity-50"
                    >
                        🌍 Перевести на {languages.find(l => l.code === selectedLanguage)?.name}
                    </button>
                )}
                
                <button
                    onClick={() => setCurrentView('chat')}
                    className="w-full bg-gray-500 text-white py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors"
                >
                    ← Вернуться к чату
                </button>
            </div>
        </div>
    );

    const renderCoverLetter = () => (
        <div className="bg-white min-h-screen">
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-500 to-blue-600 text-white p-6">
                <h2 className="text-xl font-bold flex items-center">
                    <FileText className="w-6 h-6 mr-2" />
                    Сопроводительное письмо
                </h2>
                <p className="text-indigo-100 mt-2">Персонализированное письмо для вакансии</p>
            </div>

            {/* Cover Letter Content */}
            {coverLetter && (
                <div className="p-6 space-y-6">
                    <div className="bg-gray-50 p-6 rounded-lg">
                        <div className="mb-4">
                            <h4 className="font-medium text-gray-900 mb-2">Тема письма:</h4>
                            <p className="text-gray-700">{coverLetter.subject || 'Заявка на позицию'}</p>
                        </div>
                        
                        <div className="mb-4">
                            <h4 className="font-medium text-gray-900 mb-2">Приветствие:</h4>
                            <p className="text-gray-700">{coverLetter.greeting}</p>
                        </div>
                        
                        <div className="mb-4">
                            <h4 className="font-medium text-gray-900 mb-2">Основной текст:</h4>
                            <div className="text-gray-700 whitespace-pre-wrap">{coverLetter.body}</div>
                        </div>
                        
                        <div>
                            <h4 className="font-medium text-gray-900 mb-2">Заключение:</h4>
                            <p className="text-gray-700">{coverLetter.closing}</p>
                        </div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">📊 Статистика:</h4>
                        <p className="text-blue-700">
                            Количество слов: {coverLetter.word_count || 0}
                        </p>
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="p-6 border-t border-gray-200 space-y-3">
                <button
                    onClick={() => {
                        navigator.clipboard.writeText(coverLetter?.full_text || '');
                        setSuccess('Письмо скопировано в буфер обмена!');
                    }}
                    className="w-full bg-blue-500 text-white py-3 rounded-lg font-medium hover:bg-blue-600 transition-colors"
                >
                    📋 Скопировать письмо
                </button>
                
                <button
                    onClick={() => sendTelegramNotification('custom', null, { 
                        title: 'Сопроводительное письмо готово!', 
                        message: coverLetter?.full_text || '' 
                    })}
                    disabled={loading}
                    className="w-full bg-green-500 text-white py-3 rounded-lg font-medium hover:bg-green-600 transition-colors disabled:opacity-50"
                >
                    📱 Отправить в Telegram
                </button>
                
                <button
                    onClick={() => setCurrentView('chat')}
                    className="w-full bg-gray-500 text-white py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors"
                >
                    ← Вернуться к чату
                </button>
            </div>
        </div>
    );

    const renderRecommendations = () => (
        <div className="bg-white min-h-screen">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6">
                <h2 className="text-xl font-bold flex items-center">
                    <Star className="w-6 h-6 mr-2" />
                    AI-Рекомендации вакансий
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
                    jobRecommendations.map((job, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <h3 className="font-bold text-lg text-gray-900">{job.title}</h3>
                                    <p className="text-gray-600">{job.company_name}</p>
                                    <p className="text-gray-500 text-sm">{job.location?.city || job.location}</p>
                                </div>
                                
                                {job.compatibility_score && (
                                    <div className="text-right">
                                        <div className="text-2xl font-bold text-emerald-600">
                                            {job.compatibility_score}%
                                        </div>
                                        <div className="text-xs text-gray-500">совместимость</div>
                                    </div>
                                )}
                            </div>

                            {job.description && (
                                <p className="text-gray-700 text-sm line-clamp-3">{job.description}</p>
                            )}

                            <div className="flex flex-wrap gap-2 pt-2">
                                <button
                                    onClick={() => analyzeJobCompatibility(job)}
                                    className="flex-1 bg-blue-500 text-white py-2 px-3 rounded text-sm font-medium hover:bg-blue-600 transition-colors"
                                >
                                    📊 Анализ
                                </button>
                                
                                <button
                                    onClick={() => generateCoverLetter(job)}
                                    className="flex-1 bg-indigo-500 text-white py-2 px-3 rounded text-sm font-medium hover:bg-indigo-600 transition-colors"
                                >
                                    📝 Письмо
                                </button>
                                
                                <button
                                    onClick={() => {
                                        setSelectedJob(job);
                                        translateJob(job, selectedLanguage);
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
                    onClick={() => sendTelegramNotification('ai_recommendation', null, { 
                        jobs_list: jobRecommendations,
                        ai_analysis: 'Персональные рекомендации на основе вашего профиля' 
                    })}
                    disabled={loading || jobRecommendations.length === 0}
                    className="w-full bg-emerald-500 text-white py-3 rounded-lg font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50"
                >
                    📱 Отправить рекомендации в Telegram
                </button>
                
                <button
                    onClick={() => setCurrentView('chat')}
                    className="w-full bg-gray-500 text-white py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors"
                >
                    ← Вернуться к чату
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
                
                <button
                    onClick={() => setCurrentView('analysis')}
                    disabled={!compatibilityScore}
                    className={`flex-1 py-3 px-2 rounded-lg text-sm font-medium transition-colors ${
                        currentView === 'analysis' 
                            ? 'bg-green-500 text-white' 
                            : compatibilityScore ? 'text-gray-600 hover:bg-gray-100' : 'text-gray-400'
                    }`}
                >
                    <Target className="w-5 h-5 mx-auto mb-1" />
                    Анализ
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
                {currentView === 'analysis' && renderAnalysis()}
                {currentView === 'translation' && renderTranslation()}
                {currentView === 'cover-letter' && renderCoverLetter()}
                {currentView === 'recommendations' && renderRecommendations()}
            </div>

            {/* Navigation */}
            {renderNavigation()}
        </div>
    );
};

export default AIJobAssistant;