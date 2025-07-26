import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import {
    Brain, Zap, TrendingUp, Target, Rocket, User, 
    BarChart3, PieChart, Award, Trophy, ChevronRight,
    CheckCircle, Clock, AlertTriangle, Sparkles,
    FileText, MessageSquare, BookOpen, Settings,
    ArrowLeft, Plus, RotateCcw, Eye, X, Download,
    Cpu, Search, Loader
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    hapticFeedback, 
    telegramWebApp,
    showBackButton,
    hideBackButton 
} from '../utils/telegramWebApp';

const RevolutionaryAIRecruiter = ({ onBack, aiProfile = null }) => {
    const { user, backendUrl } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('overview');
    const [loading, setLoading] = useState(false);
    
    // Revolutionary Analysis State
    const [revolutionaryStatus, setRevolutionaryStatus] = useState(null);
    const [revolutionaryAnalysis, setRevolutionaryAnalysis] = useState(null);
    const [analysisProgress, setAnalysisProgress] = useState(0);
    
    // Features State
    const [selectedJob, setSelectedJob] = useState(null);
    const [instantAnalysis, setInstantAnalysis] = useState(null);
    const [coverLetter, setCoverLetter] = useState(null);
    const [coverLetterStyle, setCoverLetterStyle] = useState('professional');
    
    // UI State
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [showDetails, setShowDetails] = useState({});

    const coverLetterStyles = [
        { value: 'professional', label: 'Профессиональный', icon: '👔', description: 'Строгий деловой стиль' },
        { value: 'creative', label: 'Креативный', icon: '🎨', description: 'Живой и оригинальный подход' },
        { value: 'technical', label: 'Технический', icon: '⚙️', description: 'Фокус на технических навыках' },
        { value: 'friendly', label: 'Дружелюбный', icon: '😊', description: 'Теплый личностный подход' }
    ];

    useEffect(() => {
        console.log('🚀 Revolutionary AI Recruiter mounted');
        if (isTelegramWebApp()) {
            showBackButton();
            telegramWebApp.BackButton.onClick(() => {
                hapticFeedback('impact', 'light');
                onBack();
            });
        }
        
        loadRevolutionaryStatus();
        
        return () => {
            if (isTelegramWebApp()) {
                hideBackButton();
            }
        };
    }, []);

    const loadRevolutionaryStatus = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/revolutionary-status`, {
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setRevolutionaryStatus(data);
                
                if (data.revolutionary_analysis?.completed) {
                    // Если анализ уже есть, загружаем его из профиля
                    if (aiProfile?.revolutionary_analysis) {
                        setRevolutionaryAnalysis(aiProfile.revolutionary_analysis);
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load revolutionary status:', error);
            setError('Ошибка загрузки статуса');
        }
    };

    const conductRevolutionaryAnalysis = async () => {
        if (!revolutionaryStatus?.features_available?.revolutionary_analysis) {
            setError('🔑 Для проведения революционного анализа необходимо добавить AI ключи в настройках!');
            return;
        }

        setLoading(true);
        setError(null);
        setAnalysisProgress(0);
        
        // Анимация прогресса
        const progressInterval = setInterval(() => {
            setAnalysisProgress(prev => {
                if (prev >= 90) {
                    clearInterval(progressInterval);
                    return 90;
                }
                return prev + Math.random() * 15;
            });
        }, 800);

        try {
            hapticFeedback('impact', 'medium');
            
            const response = await fetch(`${backendUrl}/api/revolutionary-analysis`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    analysis_depth: 'comprehensive',
                    focus_areas: ['skills', 'market', 'strategy', 'salary']
                })
            });
            
            const data = await response.json();
            clearInterval(progressInterval);
            setAnalysisProgress(100);
            
            if (response.ok && data.status === 'success') {
                setRevolutionaryAnalysis(data.analysis);
                setSuccess('🚀 Революционный анализ завершен! Теперь у вас есть супер-сила для поиска работы!');
                hapticFeedback('notification', 'success');
                setCurrentView('analysis');
            } else {
                throw new Error(data.message || 'Ошибка проведения анализа');
            }
        } catch (error) {
            console.error('Revolutionary analysis failed:', error);
            setError(`Ошибка анализа: ${error.message}`);
            clearInterval(progressInterval);
            setAnalysisProgress(0);
        } finally {
            setLoading(false);
        }
    };

    const analyzeJobInstantly = async (jobData, analysisType = 'compatibility') => {
        if (!revolutionaryStatus?.features_available?.instant_job_analysis) {
            setError('🔑 Для мгновенного анализа необходимо добавить AI ключи!');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            hapticFeedback('impact', 'light');
            
            const response = await fetch(`${backendUrl}/api/instant-job-analysis`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_data: jobData,
                    analysis_type: analysisType
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                setInstantAnalysis(data.analysis);
                setSelectedJob(jobData);
                setCurrentView('job-analysis');
                hapticFeedback('notification', 'success');
            } else {
                throw new Error(data.message || 'Ошибка анализа вакансии');
            }
        } catch (error) {
            console.error('Instant job analysis failed:', error);
            setError(`Ошибка анализа: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const generatePerfectCoverLetter = async (jobData, style = 'professional') => {
        if (!revolutionaryStatus?.features_available?.perfect_cover_letters) {
            setError('🔑 Для генерации идеальных писем необходимо добавить AI ключи!');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            hapticFeedback('impact', 'medium');
            
            const response = await fetch(`${backendUrl}/api/perfect-cover-letter`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${user.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_data: jobData,
                    style: style,
                    custom_points: []
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                setCoverLetter(data.cover_letter);
                setSelectedJob(jobData);
                setCurrentView('cover-letter');
                setSuccess('📝 Идеальное сопроводительное письмо готово!');
                hapticFeedback('notification', 'success');
            } else {
                throw new Error(data.message || 'Ошибка генерации письма');
            }
        } catch (error) {
            console.error('Cover letter generation failed:', error);
            setError(`Ошибка генерации: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const toggleDetails = (section) => {
        setShowDetails(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const renderOverview = () => (
        <div className="max-w-4xl mx-auto p-4 space-y-6">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 text-white p-8 rounded-3xl shadow-2xl">
                <div className="flex items-center justify-between">
                    <div className="flex-1">
                        <h1 className="text-3xl font-bold mb-3 flex items-center">
                            <Zap className="h-10 w-10 mr-3 text-yellow-300" />
                            🚀 Революционный AI Рекрутер
                        </h1>
                        <p className="text-lg text-purple-100 mb-6">
                            Новое поколение AI для мгновенного анализа вакансий и создания идеальных сопроводительных писем
                        </p>
                        <div className="flex flex-wrap gap-2">
                            <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                                ⚡ Мгновенный анализ
                            </span>
                            <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                                🧠 AI совместимость
                            </span>
                            <span className="bg-white/20 text-white px-3 py-1 rounded-full text-sm font-medium">
                                💌 Идеальные письма
                            </span>
                        </div>
                    </div>
                    <div className="ml-6">
                        <div className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center">
                            <Brain className="h-10 w-10 text-white" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Revolutionary Analysis Status */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                    <div className="flex items-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
                            <Rocket className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-800">Революционный анализ</h3>
                            <p className="text-sm text-gray-600">
                                {revolutionaryStatus?.system_status === 'revolutionary' ? 
                                    'Активен и готов к работе' : 
                                    'Требуется настройка AI ключей'
                                }
                            </p>
                        </div>
                    </div>
                    
                    {!revolutionaryAnalysis ? (
                        <button
                            onClick={conductRevolutionaryAnalysis}
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader className="h-5 w-5 animate-spin" />
                                    Анализ... {Math.round(analysisProgress)}%
                                </>
                            ) : (
                                <>
                                    <Zap className="h-5 w-5" />
                                    Запустить анализ
                                </>
                            )}
                        </button>
                    ) : (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-gray-700">Статус анализа</span>
                                <span className="text-sm font-semibold text-green-600 flex items-center gap-1">
                                    <CheckCircle className="h-4 w-4" />
                                    Завершен
                                </span>
                            </div>
                            <button
                                onClick={() => setCurrentView('analysis')}
                                className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-200 flex items-center justify-center gap-2"
                            >
                                <Trophy className="h-5 w-5" />
                                Посмотреть результаты
                            </button>
                        </div>
                    )}
                </div>

                {/* AI Features Status */}
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                    <div className="flex items-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mr-4">
                            <Settings className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-800">AI Возможности</h3>
                            <p className="text-sm text-gray-600">Доступные функции</p>
                        </div>
                    </div>
                    
                    <div className="space-y-3">
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${revolutionaryStatus?.features_available?.instant_job_analysis ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <span className="text-sm font-medium text-gray-700">Мгновенный анализ вакансий</span>
                            </div>
                            {revolutionaryStatus?.features_available?.instant_job_analysis ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                                <X className="h-4 w-4 text-red-500" />
                            )}
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${revolutionaryStatus?.features_available?.perfect_cover_letters ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <span className="text-sm font-medium text-gray-700">Идеальные письма</span>
                            </div>
                            {revolutionaryStatus?.features_available?.perfect_cover_letters ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                                <X className="h-4 w-4 text-red-500" />
                            )}
                        </div>
                        
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${revolutionaryStatus?.features_available?.batch_analysis ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <span className="text-sm font-medium text-gray-700">Пакетный анализ</span>
                            </div>
                            {revolutionaryStatus?.features_available?.batch_analysis ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                                <X className="h-4 w-4 text-red-500" />
                            )}
                        </div>
                    </div>
                    
                    {revolutionaryStatus?.system_status !== 'revolutionary' && (
                        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-sm text-yellow-700 flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                🔑 Добавьте AI ключи в настройках для доступа ко всем возможностям
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* AI Providers */}
            {revolutionaryStatus?.ai_providers && (
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
                    <div className="flex items-center mb-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center mr-3">
                            <Cpu className="h-5 w-5 text-white" />
                        </div>
                        <h3 className="font-semibold text-gray-800">Подключенные AI провайдеры</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {revolutionaryStatus.ai_providers.map((provider, index) => (
                            <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                                <div>
                                    <p className="font-medium text-gray-800 capitalize">{provider.name}</p>
                                    <p className="text-sm text-gray-500">{provider.model}</p>
                                </div>
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <CheckCircle className="h-4 w-4 text-white" />
                                </div>
                            </div>
                        ))}
                    </div>
                    
                    {revolutionaryStatus.ai_providers.length === 0 && (
                        <div className="text-center py-8">
                            <Cpu className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-500 mb-4">Нет подключенных AI провайдеров</p>
                            <p className="text-sm text-gray-400">Добавьте ключи в настройках для активации возможностей</p>
                        </div>
                    )}
                </div>
            )}

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                            <Search className="h-6 w-6" />
                        </div>
                        <ChevronRight className="h-6 w-6" />
                    </div>
                    <h4 className="font-semibold text-lg mb-2">Протестировать анализ</h4>
                    <p className="text-blue-100 text-sm mb-4">Попробуйте мгновенный анализ совместимости с любой вакансией</p>
                    <button
                        onClick={() => setCurrentView('job-test')}
                        className="w-full bg-white/20 text-white py-2 px-4 rounded-lg font-medium hover:bg-white/30 transition-colors"
                    >
                        Начать тестирование
                    </button>
                </div>

                <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                            <FileText className="h-6 w-6" />
                        </div>
                        <ChevronRight className="h-6 w-6" />
                    </div>
                    <h4 className="font-semibold text-lg mb-2">Создать письмо</h4>
                    <p className="text-green-100 text-sm mb-4">Сгенерируйте идеальное сопроводительное письмо с AI</p>
                    <button
                        onClick={() => setCurrentView('cover-letter-test')}
                        className="w-full bg-white/20 text-white py-2 px-4 rounded-lg font-medium hover:bg-white/30 transition-colors"
                    >
                        Создать письмо
                    </button>
                </div>
            </div>

            {/* Error/Success Messages */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-2xl flex items-start shadow-lg">
                    <AlertTriangle className="h-5 w-5 mr-3 mt-0.5 flex-shrink-0" />
                    <div>
                        <p className="font-medium">Ошибка</p>
                        <p className="text-sm">{error}</p>
                    </div>
                </div>
            )}

            {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-4 rounded-2xl flex items-start shadow-lg">
                    <CheckCircle className="h-5 w-5 mr-3 mt-0.5 flex-shrink-0" />
                    <div>
                        <p className="font-medium">Успех</p>
                        <p className="text-sm">{success}</p>
                    </div>
                </div>
            )}
        </div>
    );

    const renderAnalysis = () => {
        if (!revolutionaryAnalysis) {
            return (
                <div className="max-w-4xl mx-auto p-4">
                    <div className="text-center py-8">
                        <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-600 mb-2">Революционный анализ не найден</h3>
                        <p className="text-sm text-gray-500 mb-4">Проведите анализ для получения детальной информации</p>
                        <button
                            onClick={() => setCurrentView('overview')}
                            className="bg-purple-600 text-white px-4 py-2 rounded-lg"
                        >
                            Вернуться к обзору
                        </button>
                    </div>
                </div>
            );
        }

        return (
            <div className="max-w-4xl mx-auto p-4 space-y-6">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-2xl">
                    <h1 className="text-2xl font-bold mb-2 flex items-center">
                        <Trophy className="h-8 w-8 mr-3" />
                        Ваш революционный анализ
                    </h1>
                    <p className="text-purple-100 text-sm">
                        Полный разбор вашего профиля и стратегия поиска работы
                    </p>
                </div>

                {/* Career Strategy */}
                {revolutionaryAnalysis.career_strategy && (
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold flex items-center">
                                <Target className="h-6 w-6 text-blue-600 mr-2" />
                                Карьерная стратегия
                            </h3>
                            <button
                                onClick={() => toggleDetails('strategy')}
                                className="text-blue-600 hover:text-blue-700"
                            >
                                <Eye className="h-5 w-5" />
                            </button>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-lg mb-4">
                            <p className="font-medium text-blue-800">
                                {revolutionaryAnalysis.career_strategy.strategy_type || 'Персональная стратегия развития'}
                            </p>
                        </div>

                        {showDetails.strategy && (
                            <div className="space-y-4">
                                {revolutionaryAnalysis.career_strategy.short_term_goals && (
                                    <div>
                                        <h4 className="font-medium text-gray-800 mb-2">Краткосрочные цели (3-6 мес.)</h4>
                                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                                            {revolutionaryAnalysis.career_strategy.short_term_goals.actions?.map((action, index) => (
                                                <li key={index}>{action}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {revolutionaryAnalysis.career_strategy.long_term_perspective && (
                                    <div>
                                        <h4 className="font-medium text-gray-800 mb-2">Долгосрочная перспектива</h4>
                                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                                            {revolutionaryAnalysis.career_strategy.long_term_perspective.career_growth?.map((growth, index) => (
                                                <li key={index}>{growth}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Success Predictions */}
                {revolutionaryAnalysis.success_predictions && (
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <BarChart3 className="h-6 w-6 text-green-600 mr-2" />
                            Предсказания успешности
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {revolutionaryAnalysis.success_predictions.overall_success && (
                                <>
                                    <div className="text-center p-4 bg-green-50 rounded-lg">
                                        <div className="text-2xl font-bold text-green-600">
                                            {revolutionaryAnalysis.success_predictions.overall_success.interview_probability || 75}%
                                        </div>
                                        <div className="text-sm text-green-700">Шанс интервью</div>
                                    </div>
                                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                                        <div className="text-2xl font-bold text-blue-600">
                                            {revolutionaryAnalysis.success_predictions.overall_success.offer_probability || 60}%
                                        </div>
                                        <div className="text-sm text-blue-700">Шанс оффера</div>
                                    </div>
                                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                                        <div className="text-lg font-bold text-purple-600">
                                            {revolutionaryAnalysis.success_predictions.overall_success.time_to_employment || '2-4 мес.'}
                                        </div>
                                        <div className="text-sm text-purple-700">Время до работы</div>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* Job Recommendations */}
                {revolutionaryAnalysis.job_recommendations && revolutionaryAnalysis.job_recommendations.length > 0 && (
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <Star className="h-6 w-6 text-yellow-600 mr-2" />
                            Революционные рекомендации ({revolutionaryAnalysis.job_recommendations.length})
                        </h3>

                        <div className="space-y-4">
                            {revolutionaryAnalysis.job_recommendations.slice(0, 3).map((rec, index) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-start justify-between mb-3">
                                        <div>
                                            <h4 className="font-medium text-gray-800">{rec.job?.title || 'Позиция'}</h4>
                                            <p className="text-sm text-gray-600">{rec.job?.company_name || 'Компания'}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-lg font-bold text-green-600">
                                                {rec.revolutionary_analysis?.compatibility_score || 75}%
                                            </div>
                                            <div className="text-xs text-gray-500">совместимость</div>
                                        </div>
                                    </div>

                                    {rec.ai_insights?.hidden_opportunities && (
                                        <div className="bg-yellow-50 p-3 rounded-lg">
                                            <p className="text-sm text-yellow-800">
                                                💡 <strong>AI Инсайт:</strong> {rec.ai_insights.hidden_opportunities}
                                            </p>
                                        </div>
                                    )}

                                    <div className="flex gap-2 mt-3">
                                        <button
                                            onClick={() => analyzeJobInstantly(rec.job, 'compatibility')}
                                            className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded"
                                        >
                                            Детальный анализ
                                        </button>
                                        <button
                                            onClick={() => generatePerfectCoverLetter(rec.job)}
                                            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded"
                                        >
                                            Создать письмо
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {revolutionaryAnalysis.job_recommendations.length > 3 && (
                            <div className="text-center mt-4">
                                <button
                                    onClick={() => toggleDetails('recommendations')}
                                    className="text-blue-600 hover:text-blue-700 flex items-center mx-auto"
                                >
                                    {showDetails.recommendations ? 'Скрыть' : `Показать еще ${revolutionaryAnalysis.job_recommendations.length - 3}`}
                                    <ChevronRight className={`h-4 w-4 ml-1 transition-transform ${showDetails.recommendations ? 'rotate-90' : ''}`} />
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Back Button */}
                <button
                    onClick={() => setCurrentView('overview')}
                    className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg flex items-center justify-center"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Вернуться к обзору
                </button>
            </div>
        );
    };

    const renderJobTest = () => (
        <div className="max-w-4xl mx-auto p-4 space-y-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Тест анализа вакансии</h2>
            
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="text-sm text-yellow-800">
                    🚧 В реальном приложении здесь будет возможность выбрать вакансию из поиска и провести мгновенный анализ.
                </p>
            </div>

            <button
                onClick={() => setCurrentView('overview')}
                className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg flex items-center justify-center"
            >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Назад
            </button>
        </div>
    );

    const renderCoverLetterTest = () => (
        <div className="max-w-4xl mx-auto p-4 space-y-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Создание сопроводительного письма</h2>
            
            {/* Style Selection */}
            <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Выберите стиль письма</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {coverLetterStyles.map((style) => (
                        <button
                            key={style.value}
                            onClick={() => setCoverLetterStyle(style.value)}
                            className={`p-3 rounded-lg border-2 text-left transition-colors ${
                                coverLetterStyle === style.value
                                    ? 'border-purple-500 bg-purple-50'
                                    : 'border-gray-200 hover:border-gray-300'
                            }`}
                        >
                            <div className="flex items-center mb-2">
                                <span className="text-lg mr-2">{style.icon}</span>
                                <span className="font-medium">{style.label}</span>
                            </div>
                            <p className="text-sm text-gray-600">{style.description}</p>
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                <p className="text-sm text-yellow-800">
                    🚧 В реальном приложении здесь будет возможность выбрать вакансию и сгенерировать персонализированное письмо.
                </p>
            </div>

            <button
                onClick={() => setCurrentView('overview')}
                className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg flex items-center justify-center"
            >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Назад
            </button>
        </div>
    );

    // Clear messages after 5 seconds
    useEffect(() => {
        if (error || success) {
            const timer = setTimeout(() => {
                setError(null);
                setSuccess(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [error, success]);

    // Main render logic
    switch (currentView) {
        case 'analysis':
            return renderAnalysis();
        case 'job-test':
            return renderJobTest();
        case 'cover-letter-test':
            return renderCoverLetterTest();
        default:
            return renderOverview();
    }
};

export default RevolutionaryAIRecruiter;