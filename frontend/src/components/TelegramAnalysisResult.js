import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { 
    CheckCircle, 
    AlertTriangle, 
    Clock, 
    Copy, 
    Star,
    Mail,
    Zap,
    Target,
    MessageSquare,
    Timer,
    Sparkles,
    FileText,
    X,
    ChevronDown,
    ChevronUp,
    Send,
    Eye,
    Globe,
    Bot,
    TrendingUp,
    ArrowLeft,
    Share2,
    Bookmark,
    Crown,
    Diamond,
    Gem,
    Wand2,
    Flame,
    Shield,
    Award,
    Activity,
    Layers,
    Rocket,
    Cpu,
    Heart,
    Waves
} from 'lucide-react';
import { hapticFeedback, showTelegramAlert, isTelegramWebApp } from '../utils/telegramWebApp';

const TelegramAnalysisResult = ({ analysisResult, onClose }) => {
    const { t } = useLanguage();
    const [showFullAnalysis, setShowFullAnalysis] = useState(false);
    const [showSuggestedResponse, setShowSuggestedResponse] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [animateIn, setAnimateIn] = useState(false);
    const [currentSection, setCurrentSection] = useState('summary');

    useEffect(() => {
        const timer = setTimeout(() => setAnimateIn(true), 100);
        return () => clearTimeout(timer);
    }, []);

    const copyToClipboard = async (text, section) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedSection(section);
            setTimeout(() => setCopiedSection(''), 2000);
            
            if (isTelegramWebApp()) {
                hapticFeedback('success');
                showTelegramAlert(t('copiedToClipboard'));
            }
        } catch (err) {
            console.error('Ошибка копирования:', err);
            if (isTelegramWebApp()) {
                hapticFeedback('error');
                showTelegramAlert(t('copyError'));
            }
        }
    };

    const getUrgencyConfig = (urgency) => {
        switch (urgency?.toUpperCase()) {
            case 'ВЫСОКИЙ':
            case 'HIGH':
                return {
                    color: 'text-red-600',
                    bg: 'bg-red-50 border-red-300',
                    icon: <Zap className="h-5 w-5 text-red-500" />,
                    gradient: 'from-red-500 to-red-600',
                    pulse: 'animate-pulse',
                    emoji: '🚨'
                };
            case 'СРЕДНИЙ':
            case 'MEDIUM':
                return {
                    color: 'text-amber-600',
                    bg: 'bg-amber-50 border-amber-300',
                    icon: <Target className="h-5 w-5 text-amber-500" />,
                    gradient: 'from-amber-500 to-orange-500',
                    pulse: '',
                    emoji: '⚡'
                };
            case 'НИЗКИЙ':
            case 'LOW':
                return {
                    color: 'text-green-600',
                    bg: 'bg-green-50 border-green-300',
                    icon: <CheckCircle className="h-5 w-5 text-green-500" />,
                    gradient: 'from-green-500 to-emerald-500',
                    pulse: '',
                    emoji: '✅'
                };
            default:
                return {
                    color: 'text-gray-600',
                    bg: 'bg-gray-50 border-gray-300',
                    icon: <Clock className="h-5 w-5 text-gray-500" />,
                    gradient: 'from-gray-500 to-gray-600',
                    pulse: '',
                    emoji: '📄'
                };
        }
    };

    const urgencyConfig = getUrgencyConfig(analysisResult?.urgency_level);

    // Генерируем предлагаемый ответ
    const generateSuggestedResponse = () => {
        const analysis = analysisResult?.analysis;
        if (!analysis) return null;

        const content = analysis.main_content?.toLowerCase() || '';
        
        let responseTemplate = '';
        let responseType = 'info';

        if (content.includes('счет') || content.includes('оплата') || content.includes('платеж')) {
            responseTemplate = `Уважаемые господа,

Благодарю за направленный счет. Подтверждаю получение документа и информирую, что оплата будет произведена в установленные сроки.

С уважением`;
            responseType = 'payment';
        } else if (content.includes('приглашение') || content.includes('встреча') || content.includes('собрание')) {
            responseTemplate = `Уважаемые коллеги,

Благодарю за приглашение. Подтверждаю свое участие в предложенном мероприятии.

С наилучшими пожеланиями`;
            responseType = 'meeting';
        } else if (urgencyConfig.color === 'text-red-600') {
            responseTemplate = `Уважаемые господа,

Благодарю за срочное уведомление. Принимаю к сведению важность данного сообщения и готов оперативно предоставить необходимую информацию.

С уважением`;
            responseType = 'urgent';
        } else {
            responseTemplate = `Уважаемые господа,

Благодарю за Ваше письмо. Информация принята к сведению.

При необходимости готов предоставить дополнительную информацию.

С уважением`;
            responseType = 'general';
        }

        return { template: responseTemplate, type: responseType };
    };

    const suggestedResponse = generateSuggestedResponse();

    // Функция для красивого форматирования текста
    const formatText = (text) => {
        if (!text) return '';
        
        let formatted = text.replace(/\*+/g, '').replace(/#+/g, '').trim();
        const paragraphs = formatted.split('\n').filter(p => p.trim());
        
        return paragraphs.map((paragraph, index) => {
            const trimmed = paragraph.trim();
            if (!trimmed) return null;
            
            const isHeader = trimmed === trimmed.toUpperCase() && trimmed.length > 3;
            
            if (isHeader) {
                return (
                    <div key={index} className="font-bold text-base text-gray-900 mt-3 mb-2 flex items-center space-x-2">
                        <span className="text-blue-500">📋</span>
                        <span>{trimmed}</span>
                    </div>
                );
            } else {
                return (
                    <p key={index} className="text-gray-700 leading-relaxed mb-2 text-sm">
                        {trimmed}
                    </p>
                );
            }
        });
    };

    const handleClose = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        onClose();
    };

    const handleSectionChange = (section) => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        setCurrentSection(section);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
            
            {/* СУПЕР ЭФФЕКТНЫЙ КОСМИЧЕСКИЙ ФОН ДЛЯ РЕЗУЛЬТАТОВ */}
            <div className="absolute inset-0">
                {/* Основные градиентные слои */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/50 via-purple-900/70 to-pink-900/50 animate-pulse"></div>
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-800/40 via-transparent to-rose-800/40"></div>
                
                {/* Анимированные космические орбы для результатов */}
                <div className="absolute top-16 left-10 w-80 h-80 bg-gradient-to-br from-emerald-500/40 to-cyan-500/40 rounded-full blur-3xl animate-pulse opacity-80"></div>
                <div className="absolute top-32 right-16 w-72 h-72 bg-gradient-to-br from-purple-500/35 to-pink-500/35 rounded-full blur-3xl animate-pulse delay-1000 opacity-70"></div>
                <div className="absolute bottom-24 left-20 w-96 h-96 bg-gradient-to-br from-blue-500/30 to-indigo-500/30 rounded-full blur-3xl animate-pulse delay-2000 opacity-75"></div>
                <div className="absolute bottom-40 right-8 w-64 h-64 bg-gradient-to-br from-orange-500/35 to-red-500/35 rounded-full blur-3xl animate-pulse delay-3000 opacity-80"></div>
                
                {/* Движущиеся световые полосы */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-400/15 to-transparent transform -skew-x-12 animate-pulse"></div>
                <div className="absolute inset-0 bg-gradient-to-l from-transparent via-purple-400/15 to-transparent transform skew-x-12 animate-pulse delay-1500"></div>
                
                {/* Множественные анимированные частицы для результатов */}
                <div className="absolute inset-0 pointer-events-none">
                    {[...Array(80)].map((_, i) => (
                        <div
                            key={i}
                            className={`absolute animate-pulse opacity-70`}
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 5}s`,
                                animationDuration: `${3 + Math.random() * 4}s`
                            }}
                        >
                            {i % 12 === 0 && <Crown className="h-4 w-4 text-yellow-400/70" />}
                            {i % 12 === 1 && <Diamond className="h-3 w-3 text-cyan-400/70" />}
                            {i % 12 === 2 && <Gem className="h-4 w-4 text-purple-400/70" />}
                            {i % 12 === 3 && <Sparkles className="h-3 w-3 text-blue-400/70" />}
                            {i % 12 === 4 && <Star className="h-2 w-2 text-pink-400/70" />}
                            {i % 12 === 5 && <Wand2 className="h-4 w-4 text-emerald-400/70" />}
                            {i % 12 === 6 && <Flame className="h-3 w-3 text-red-400/70" />}
                            {i % 12 === 7 && <Shield className="h-4 w-4 text-teal-400/70" />}
                            {i % 12 === 8 && <Award className="h-3 w-3 text-orange-400/70" />}
                            {i % 12 === 9 && <Activity className="h-2 w-2 text-green-400/70" />}
                            {i % 12 === 10 && <Rocket className="h-4 w-4 text-indigo-400/70" />}
                            {i % 12 === 11 && <Heart className="h-3 w-3 text-rose-400/70" />}
                        </div>
                    ))}
                </div>

                {/* Дополнительные волновые эффекты */}
                <div className="absolute inset-0 opacity-30">
                    <div className="absolute top-0 left-0 w-full h-3 bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-500 animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 w-full h-3 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-pulse delay-1000"></div>
                    <div className="absolute left-0 top-0 w-3 h-full bg-gradient-to-b from-cyan-500 via-blue-500 to-purple-500 animate-pulse delay-2000"></div>
                    <div className="absolute right-0 top-0 w-3 h-full bg-gradient-to-b from-purple-500 via-pink-500 to-rose-500 animate-pulse delay-3000"></div>
                </div>
            </div>

            {/* СУПЕР ЭФФЕКТНЫЙ АНИМИРОВАННЫЙ HEADER */}
            <div className={`relative z-10 bg-gradient-to-r ${urgencyConfig.gradient} px-4 py-6 relative overflow-hidden transform transition-all duration-1000 shadow-2xl ${
                animateIn ? 'translate-y-0 opacity-100 scale-100' : '-translate-y-full opacity-0 scale-95'
            }`}>
                {/* Header Background Effects */}
                <div className="absolute inset-0 opacity-25">
                    {[...Array(20)].map((_, i) => (
                        <div key={i} 
                             className="absolute animate-bounce opacity-80"
                             style={{
                                 left: `${Math.random() * 100}%`,
                                 top: `${Math.random() * 100}%`,
                                 animationDelay: `${Math.random() * 2}s`,
                                 animationDuration: `${1.5 + Math.random()}s`
                             }}>
                            {i % 6 === 0 && <Sparkles className="h-4 w-4 text-white" />}
                            {i % 6 === 1 && <Star className="h-3 w-3 text-white" />}
                            {i % 6 === 2 && <Diamond className="h-4 w-4 text-white" />}
                            {i % 6 === 3 && <Crown className="h-3 w-3 text-white" />}
                            {i % 6 === 4 && <Gem className="h-4 w-4 text-white" />}
                            {i % 6 === 5 && <Award className="h-3 w-3 text-white" />}
                        </div>
                    ))}
                </div>
                
                <div className="relative flex items-center justify-between">
                    <button
                        onClick={handleClose}
                        className="flex items-center space-x-2 bg-white/25 backdrop-blur-xl border-2 border-white/40 rounded-2xl px-6 py-3 hover:bg-white/35 transition-all duration-300 transform hover:scale-110 hover:rotate-3 shadow-2xl"
                    >
                        <ArrowLeft className="w-5 h-5 text-white drop-shadow-lg" />
                        <span className="text-white font-bold drop-shadow-lg">Назад</span>
                    </button>
                    
                    <div className="text-center">
                        <h2 className="text-3xl font-black mb-2 text-white drop-shadow-2xl flex items-center justify-center space-x-3">
                            <div className={`p-3 bg-white/30 rounded-2xl ${urgencyConfig.pulse} shadow-2xl`}>
                                {urgencyConfig.icon}
                            </div>
                            <span>🚀 АНАЛИЗ ГОТОВ</span>
                            <span className="text-4xl">{urgencyConfig.emoji}</span>
                        </h2>
                        <p className="text-lg text-white/90 drop-shadow-xl font-bold">
                            ✨ Магия искусственного интеллекта ✨
                        </p>
                    </div>
                    
                    <button
                        onClick={() => copyToClipboard(JSON.stringify(analysisResult, null, 2), 'export')}
                        className="flex items-center space-x-2 bg-white/25 backdrop-blur-xl border-2 border-white/40 rounded-2xl px-6 py-3 hover:bg-white/35 transition-all duration-300 transform hover:scale-110 hover:-rotate-3 shadow-2xl"
                    >
                        <Share2 className="w-5 h-5 text-white drop-shadow-lg" />
                        <span className="text-white font-bold drop-shadow-lg">Поделиться</span>
                    </button>
                </div>
            </div>

            {/* СУПЕР КРАСИВЫЕ НАВИГАЦИОННЫЕ ВКЛАДКИ */}
            <div className={`relative z-10 bg-white/15 backdrop-blur-xl px-4 py-4 transform transition-all duration-700 shadow-xl border-b-2 border-white/20 ${
                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
            }`} style={{transitionDelay: '0.2s'}}>
                <div className="flex space-x-2">
                    {[
                        { id: 'summary', label: 'Резюме', icon: <FileText className="h-5 w-5" />, emoji: '📋', color: 'from-blue-500 to-cyan-500' },
                        { id: 'details', label: 'Детали', icon: <Eye className="h-5 w-5" />, emoji: '🔍', color: 'from-purple-500 to-pink-500' },
                        { id: 'response', label: 'Ответ', icon: <Send className="h-5 w-5" />, emoji: '💬', color: 'from-emerald-500 to-green-500' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => handleSectionChange(tab.id)}
                            className={`flex-1 px-6 py-4 rounded-2xl text-sm font-black transition-all duration-500 transform shadow-2xl border-2 ${
                                currentSection === tab.id
                                    ? `bg-gradient-to-r ${tab.color} text-white border-white/50 scale-105 shadow-2xl animate-pulse`
                                    : 'bg-white/20 text-white/80 hover:bg-white/30 border-white/30 hover:scale-105'
                            }`}
                        >
                            <div className="flex items-center justify-center space-x-2">
                                {tab.icon}
                                <span>{tab.label}</span>
                                <span className="text-xl">{tab.emoji}</span>
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* ОСНОВНОЙ КОНТЕНТ С ЭФФЕКТАМИ */}
            <div className="relative z-10 flex-1 overflow-y-auto px-4 py-6 space-y-6">
                
                {/* СУПЕР КРАСИВАЯ СТАТИСТИКА */}
                <div className={`grid grid-cols-2 gap-4 transform transition-all duration-700 ${
                    animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
                }`} style={{transitionDelay: '0.4s'}}>
                    
                    <div className={`relative overflow-hidden p-6 rounded-3xl ${urgencyConfig.bg} border-4 border-white/40 transform hover:scale-110 transition-all duration-500 shadow-2xl`}>
                        {/* Background particles */}
                        <div className="absolute inset-0 opacity-30">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} 
                                     className="absolute animate-pulse"
                                     style={{
                                         left: `${Math.random() * 100}%`,
                                         top: `${Math.random() * 100}%`,
                                         animationDelay: `${Math.random() * 2}s`
                                     }}>
                                    <Star className="h-3 w-3 text-gray-400" />
                                </div>
                            ))}
                        </div>
                        
                        <div className="relative flex items-center space-x-3 mb-3">
                            <div className={`p-3 bg-white/30 rounded-2xl ${urgencyConfig.pulse}`}>
                                {urgencyConfig.icon}
                            </div>
                            <span className="font-black text-gray-900 text-lg">Важность</span>
                        </div>
                        <p className={`text-2xl font-black ${urgencyConfig.color} drop-shadow-lg`}>
                            {analysisResult?.urgency_level || 'Не определен'}
                        </p>
                    </div>

                    <div className="relative overflow-hidden p-6 rounded-3xl bg-gradient-to-br from-indigo-100 to-purple-100 border-4 border-indigo-300/40 transform hover:scale-110 transition-all duration-500 shadow-2xl">
                        {/* Background particles */}
                        <div className="absolute inset-0 opacity-30">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} 
                                     className="absolute animate-pulse"
                                     style={{
                                         left: `${Math.random() * 100}%`,
                                         top: `${Math.random() * 100}%`,
                                         animationDelay: `${Math.random() * 2}s`
                                     }}>
                                    <Sparkles className="h-3 w-3 text-indigo-400" />
                                </div>
                            ))}
                        </div>
                        
                        <div className="relative flex items-center space-x-3 mb-3">
                            <div className="p-3 bg-indigo-500/20 rounded-2xl animate-pulse">
                                <Bot className="h-6 w-6 text-indigo-600" />
                            </div>
                            <span className="font-black text-gray-900 text-lg">AI Статус</span>
                        </div>
                        <p className="text-2xl font-black text-indigo-600 drop-shadow-lg">
                            Анализ завершен
                        </p>
                    </div>
                </div>

                {/* СЕКЦИЯ РЕЗЮМЕ */}
                {currentSection === 'summary' && (
                    <div className={`space-y-6 transform transition-all duration-700 ${
                        animateIn ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.6s'}}>
                        
                        <div className="relative overflow-hidden bg-gradient-to-br from-white/90 via-blue-50/90 to-purple-50/90 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border-4 border-blue-200/50">
                            {/* Background effects */}
                            <div className="absolute inset-0 opacity-20">
                                {[...Array(15)].map((_, i) => (
                                    <div key={i} 
                                         className="absolute animate-bounce"
                                         style={{
                                             left: `${Math.random() * 100}%`,
                                             top: `${Math.random() * 100}%`,
                                             animationDelay: `${Math.random() * 3}s`,
                                             animationDuration: `${2 + Math.random()}s`
                                         }}>
                                        {i % 4 === 0 && <Sparkles className="h-4 w-4 text-blue-400" />}
                                        {i % 4 === 1 && <Star className="h-3 w-3 text-purple-400" />}
                                        {i % 4 === 2 && <Crown className="h-4 w-4 text-yellow-400" />}
                                        {i % 4 === 3 && <Diamond className="h-3 w-3 text-cyan-400" />}
                                    </div>
                                ))}
                            </div>
                            
                            <div className="relative flex items-center justify-between mb-6">
                                <h3 className="font-black text-2xl text-gray-900 flex items-center space-x-3">
                                    <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl animate-pulse shadow-2xl">
                                        <Sparkles className="h-8 w-8 text-white" />
                                    </div>
                                    <span>💡 КРАТКОЕ СОДЕРЖАНИЕ</span>
                                </h3>
                                <button
                                    onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'summary')}
                                    className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-2xl transition-all duration-300 transform hover:scale-110 shadow-2xl border-2 border-white/30"
                                >
                                    <Copy className="h-6 w-6 text-white" />
                                </button>
                            </div>
                            
                            <div className="relative bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl p-6 shadow-inner border-2 border-blue-200/30">
                                <div className="text-gray-800 leading-relaxed text-lg font-medium">
                                    {formatText(analysisResult?.analysis?.main_content)}
                                </div>
                            </div>
                        </div>

                        {/* ИНФОРМАЦИЯ О ФАЙЛЕ */}
                        <div className="relative overflow-hidden bg-gradient-to-br from-white/90 via-emerald-50/90 to-cyan-50/90 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border-4 border-emerald-200/50">
                            {/* Background effects */}
                            <div className="absolute inset-0 opacity-20">
                                {[...Array(12)].map((_, i) => (
                                    <div key={i} 
                                         className="absolute animate-pulse"
                                         style={{
                                             left: `${Math.random() * 100}%`,
                                             top: `${Math.random() * 100}%`,
                                             animationDelay: `${Math.random() * 2}s`
                                         }}>
                                        {i % 3 === 0 && <FileText className="h-4 w-4 text-emerald-400" />}
                                        {i % 3 === 1 && <Shield className="h-3 w-3 text-cyan-400" />}
                                        {i % 3 === 2 && <Award className="h-4 w-4 text-green-400" />}
                                    </div>
                                ))}
                            </div>
                            
                            <h3 className="relative font-black text-2xl text-gray-900 mb-6 flex items-center space-x-3">
                                <div className="p-4 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-2xl animate-pulse shadow-2xl">
                                    <FileText className="h-8 w-8 text-white" />
                                </div>
                                <span>📄 ИНФОРМАЦИЯ О ФАЙЛЕ</span>
                            </h3>
                            
                            <div className="relative space-y-4 text-lg">
                                <div className="flex items-center justify-between p-4 bg-white/80 rounded-2xl shadow-lg border-2 border-emerald-200/30">
                                    <span className="text-gray-700 font-bold">Файл:</span>
                                    <span className="font-black text-gray-900 truncate ml-2">
                                        {analysisResult?.file_name}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between p-4 bg-white/80 rounded-2xl shadow-lg border-2 border-emerald-200/30">
                                    <span className="text-gray-700 font-bold">Язык:</span>
                                    <span className="font-black text-gray-900">
                                        {analysisResult?.analysis_language === 'ru' ? '🇷🇺 Русский' : analysisResult?.analysis_language}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* СЕКЦИЯ ДЕТАЛЕЙ */}
                {currentSection === 'details' && (
                    <div className={`space-y-6 transform transition-all duration-700 ${
                        animateIn ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.6s'}}>
                        
                        <div className="relative overflow-hidden bg-gradient-to-br from-white/90 via-purple-50/90 to-pink-50/90 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border-4 border-purple-200/50">
                            {/* Background effects */}
                            <div className="absolute inset-0 opacity-20">
                                {[...Array(20)].map((_, i) => (
                                    <div key={i} 
                                         className="absolute animate-bounce"
                                         style={{
                                             left: `${Math.random() * 100}%`,
                                             top: `${Math.random() * 100}%`,
                                             animationDelay: `${Math.random() * 3}s`,
                                             animationDuration: `${2 + Math.random()}s`
                                         }}>
                                        {i % 5 === 0 && <Eye className="h-4 w-4 text-purple-400" />}
                                        {i % 5 === 1 && <Layers className="h-3 w-3 text-pink-400" />}
                                        {i % 5 === 2 && <Cpu className="h-4 w-4 text-indigo-400" />}
                                        {i % 5 === 3 && <Activity className="h-3 w-3 text-violet-400" />}
                                        {i % 5 === 4 && <Waves className="h-4 w-4 text-fuchsia-400" />}
                                    </div>
                                ))}
                            </div>
                            
                            <div className="relative flex items-center justify-between mb-6">
                                <h3 className="font-black text-2xl text-gray-900 flex items-center space-x-3">
                                    <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl animate-pulse shadow-2xl">
                                        <Eye className="h-8 w-8 text-white" />
                                    </div>
                                    <span>🔍 ПОЛНЫЙ АНАЛИЗ</span>
                                </h3>
                                <button
                                    onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                                    className={`p-4 rounded-2xl transition-all duration-500 transform shadow-2xl border-2 border-white/30 ${
                                        showFullAnalysis 
                                            ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white scale-110' 
                                            : 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 hover:scale-110'
                                    }`}
                                >
                                    {showFullAnalysis ? <ChevronUp className="h-6 w-6" /> : <ChevronDown className="h-6 w-6" />}
                                </button>
                            </div>

                            {showFullAnalysis && (
                                <div className="relative bg-gradient-to-br from-gray-50 to-purple-50 rounded-2xl p-6 shadow-inner border-2 border-purple-200/30 animate-fade-in-up">
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="font-black text-gray-900 text-xl flex items-center space-x-2">
                                            <Cpu className="h-6 w-6 text-purple-600" />
                                            <span>Полный текст анализа</span>
                                        </span>
                                        <button
                                            onClick={() => copyToClipboard(analysisResult?.analysis?.full_analysis, 'full')}
                                            className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl transition-all duration-300 transform hover:scale-110 shadow-xl"
                                        >
                                            <Copy className="h-5 w-5 text-white" />
                                        </button>
                                    </div>
                                    
                                    <div className="text-gray-700 leading-relaxed text-lg max-h-80 overflow-y-auto p-4 bg-white/80 rounded-xl border-2 border-purple-200/30">
                                        {formatText(analysisResult?.analysis?.full_analysis)}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* ДЕТАЛЬНЫЕ СЕКЦИИ */}
                        {analysisResult?.analysis?.formatted_sections && analysisResult.analysis.formatted_sections.length > 0 && (
                            <div className="space-y-4">
                                {analysisResult.analysis.formatted_sections.map((section, index) => (
                                    <div key={section.key} className="relative overflow-hidden bg-gradient-to-br from-white/95 via-indigo-50/95 to-purple-50/95 backdrop-blur-xl rounded-2xl p-6 shadow-2xl border-4 border-indigo-200/40 transform hover:scale-105 transition-all duration-500">
                                        {/* Background particles */}
                                        <div className="absolute inset-0 opacity-15">
                                            {[...Array(6)].map((_, i) => (
                                                <div key={i} 
                                                     className="absolute animate-pulse"
                                                     style={{
                                                         left: `${Math.random() * 100}%`,
                                                         top: `${Math.random() * 100}%`,
                                                         animationDelay: `${Math.random() * 2}s`
                                                     }}>
                                                    <Sparkles className="h-3 w-3 text-indigo-400" />
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="relative flex items-center space-x-3 mb-4">
                                            <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl shadow-xl">
                                                <span className="text-2xl">{section.icon}</span>
                                            </div>
                                            <h4 className="font-black text-xl text-gray-900">{section.title}</h4>
                                        </div>
                                        <div className="relative text-gray-700 leading-relaxed text-lg p-4 bg-white/70 rounded-xl">
                                            {formatText(section.content)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* СЕКЦИЯ ОТВЕТА */}
                {currentSection === 'response' && (
                    <div className={`space-y-6 transform transition-all duration-700 ${
                        animateIn ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.6s'}}>
                        
                        {suggestedResponse && (
                            <div className="relative overflow-hidden bg-gradient-to-br from-emerald-100/95 via-green-50/95 to-cyan-50/95 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border-4 border-emerald-300/50">
                                {/* Background effects */}
                                <div className="absolute inset-0 opacity-20">
                                    {[...Array(25)].map((_, i) => (
                                        <div key={i} 
                                             className="absolute animate-bounce"
                                             style={{
                                                 left: `${Math.random() * 100}%`,
                                                 top: `${Math.random() * 100}%`,
                                                 animationDelay: `${Math.random() * 3}s`,
                                                 animationDuration: `${2 + Math.random()}s`
                                             }}>
                                            {i % 6 === 0 && <Send className="h-4 w-4 text-emerald-400" />}
                                            {i % 6 === 1 && <MessageSquare className="h-3 w-3 text-green-400" />}
                                            {i % 6 === 2 && <Bot className="h-4 w-4 text-cyan-400" />}
                                            {i % 6 === 3 && <Wand2 className="h-3 w-3 text-teal-400" />}
                                            {i % 6 === 4 && <Heart className="h-4 w-4 text-pink-400" />}
                                            {i % 6 === 5 && <Star className="h-3 w-3 text-yellow-400" />}
                                        </div>
                                    ))}
                                </div>
                                
                                <div className="relative flex items-center justify-between mb-6">
                                    <h3 className="font-black text-2xl text-gray-900 flex items-center space-x-3">
                                        <div className="p-4 bg-gradient-to-r from-emerald-500 to-green-500 rounded-2xl animate-pulse shadow-2xl">
                                            <Send className="h-8 w-8 text-white" />
                                        </div>
                                        <span>💬 ПРЕДЛАГАЕМЫЙ ОТВЕТ</span>
                                    </h3>
                                    <button
                                        onClick={() => setShowSuggestedResponse(!showSuggestedResponse)}
                                        className={`px-6 py-3 rounded-2xl transition-all duration-500 text-lg font-black shadow-2xl border-2 ${
                                            showSuggestedResponse
                                                ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white border-white/30 scale-110'
                                                : 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border-emerald-300/50 hover:scale-110'
                                        }`}
                                    >
                                        {showSuggestedResponse ? '🙈 Скрыть' : '👁️ Показать'}
                                    </button>
                                </div>

                                {showSuggestedResponse && (
                                    <div className="relative space-y-6 animate-fade-in-up">
                                        <div className="flex items-center justify-between p-4 bg-white/80 rounded-2xl shadow-lg border-2 border-emerald-200/50">
                                            <div className="flex items-center space-x-3">
                                                <div className="p-3 bg-emerald-500 rounded-xl shadow-xl">
                                                    <Send className="h-6 w-6 text-white" />
                                                </div>
                                                <span className="font-black text-gray-900 text-xl">Готовый шаблон</span>
                                            </div>
                                            <button
                                                onClick={() => copyToClipboard(suggestedResponse.template, 'response')}
                                                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 rounded-2xl transition-all duration-300 transform hover:scale-110 shadow-2xl"
                                            >
                                                <Copy className="h-5 w-5 text-white" />
                                                <span className="text-white font-bold">
                                                    {copiedSection === 'response' ? '✅ Скопировано!' : '📋 Копировать'}
                                                </span>
                                            </button>
                                        </div>
                                        
                                        <div className="relative bg-white/90 rounded-2xl p-6 border-l-8 border-emerald-500 shadow-2xl">
                                            <pre className="whitespace-pre-wrap text-gray-800 leading-relaxed text-lg font-medium">
                                                {suggestedResponse.template}
                                            </pre>
                                        </div>
                                        
                                        <div className="flex items-center justify-center space-x-3 text-lg text-gray-600 p-4 bg-white/70 rounded-2xl">
                                            <Bot className="h-6 w-6 text-emerald-500 animate-pulse" />
                                            <span className="font-bold">🤖 Сгенерировано на основе AI-анализа содержания</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* БЫСТРЫЕ ДЕЙСТВИЯ */}
                        <div className="relative overflow-hidden bg-gradient-to-br from-white/95 via-orange-50/95 to-yellow-50/95 backdrop-blur-xl rounded-3xl p-6 shadow-2xl border-4 border-orange-200/50">
                            {/* Background effects */}
                            <div className="absolute inset-0 opacity-20">
                                {[...Array(15)].map((_, i) => (
                                    <div key={i} 
                                         className="absolute animate-pulse"
                                         style={{
                                             left: `${Math.random() * 100}%`,
                                             top: `${Math.random() * 100}%`,
                                             animationDelay: `${Math.random() * 2}s`
                                         }}>
                                        {i % 4 === 0 && <Zap className="h-4 w-4 text-orange-400" />}
                                        {i % 4 === 1 && <Rocket className="h-3 w-3 text-yellow-400" />}
                                        {i % 4 === 2 && <Lightning className="h-4 w-4 text-amber-400" />}
                                        {i % 4 === 3 && <Star className="h-3 w-3 text-orange-500" />}
                                    </div>
                                ))}
                            </div>
                            
                            <h3 className="relative font-black text-2xl text-gray-900 mb-6 flex items-center space-x-3">
                                <div className="p-4 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-2xl animate-pulse shadow-2xl">
                                    <Zap className="h-8 w-8 text-white" />
                                </div>
                                <span>⚡ БЫСТРЫЕ ДЕЙСТВИЯ</span>
                            </h3>
                            
                            <div className="relative space-y-4">
                                <button
                                    onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'quick-summary')}
                                    className="w-full flex items-center justify-between p-6 bg-gradient-to-r from-blue-100 to-cyan-100 hover:from-blue-200 hover:to-cyan-200 rounded-2xl transition-all duration-500 transform hover:scale-105 shadow-2xl border-4 border-blue-200/50"
                                >
                                    <span className="flex items-center space-x-3">
                                        <div className="p-3 bg-blue-500 rounded-xl shadow-xl">
                                            <Copy className="h-6 w-6 text-white" />
                                        </div>
                                        <span className="text-xl font-black text-blue-900">Копировать резюме</span>
                                    </span>
                                    <span className="text-3xl">📋</span>
                                </button>
                                
                                <button
                                    onClick={() => copyToClipboard(suggestedResponse?.template, 'quick-response')}
                                    className="w-full flex items-center justify-between p-6 bg-gradient-to-r from-emerald-100 to-green-100 hover:from-emerald-200 hover:to-green-200 rounded-2xl transition-all duration-500 transform hover:scale-105 shadow-2xl border-4 border-emerald-200/50"
                                >
                                    <span className="flex items-center space-x-3">
                                        <div className="p-3 bg-emerald-500 rounded-xl shadow-xl">
                                            <Send className="h-6 w-6 text-white" />
                                        </div>
                                        <span className="text-xl font-black text-emerald-900">Копировать ответ</span>
                                    </span>
                                    <span className="text-3xl">💬</span>
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* НИЖНЯЯ ПАНЕЛЬ С ЭФФЕКТАМИ */}
            <div className={`relative z-10 bg-white/15 backdrop-blur-xl px-6 py-4 transform transition-all duration-700 shadow-2xl border-t-4 border-white/30 ${
                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
            }`} style={{transitionDelay: '0.8s'}}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 text-lg text-white/90">
                        <div className="p-2 bg-emerald-500/80 rounded-xl animate-pulse">
                            <TrendingUp className="h-6 w-6 text-white" />
                        </div>
                        <span className="font-bold drop-shadow-lg">🚀 AI-анализ завершен успешно!</span>
                    </div>
                    
                    <button
                        onClick={handleClose}
                        className="px-8 py-4 bg-gradient-to-r from-white/30 to-white/20 hover:from-white/40 hover:to-white/30 rounded-2xl transition-all duration-300 transform hover:scale-110 shadow-2xl border-2 border-white/40"
                    >
                        <span className="text-white text-lg font-black drop-shadow-lg">✨ Готово ✨</span>
                    </button>
                </div>
            </div>

            {/* CSS Animation Styles */}
            <style jsx>{`
                @keyframes fade-in-up {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .animate-fade-in-up {
                    animation: fade-in-up 0.5s ease-out;
                }

                @keyframes cosmic-glow {
                    0%, 100% {
                        box-shadow: 0 0 30px rgba(139, 92, 246, 0.6);
                    }
                    50% {
                        box-shadow: 0 0 50px rgba(139, 92, 246, 1), 0 0 80px rgba(59, 130, 246, 0.8);
                    }
                }

                .cosmic-glow {
                    animation: cosmic-glow 3s ease-in-out infinite;
                }
            `}</style>
        </div>
    );
};

export default TelegramAnalysisResult;