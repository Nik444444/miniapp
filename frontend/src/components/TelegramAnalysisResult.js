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
        <div className="fixed inset-0 bg-gradient-to-br from-indigo-900/95 via-purple-900/95 to-pink-900/95 backdrop-blur-sm flex flex-col z-50">
            {/* Animated Header */}
            <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-4 py-4 relative overflow-hidden transform transition-all duration-700 ${
                animateIn ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'
            }`}>
                {/* Background Effects */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-2 right-4 animate-bounce">
                        <Sparkles className="h-6 w-6 text-white" />
                    </div>
                    <div className="absolute bottom-2 left-4 animate-pulse" style={{animationDelay: '1s'}}>
                        <Star className="h-4 w-4 text-white" />
                    </div>
                    <div className="absolute top-1/2 right-1/4 animate-ping" style={{animationDelay: '2s'}}>
                        <span className="w-2 h-2 bg-white rounded-full block"></span>
                    </div>
                </div>
                
                <div className="relative flex items-center justify-between">
                    <button
                        onClick={handleClose}
                        className="p-2 hover:bg-white/20 rounded-xl transition-all duration-300 transform hover:scale-110"
                    >
                        <ArrowLeft className="h-5 w-5 text-white" />
                    </button>
                    
                    <div className="flex items-center space-x-3">
                        <div className={`p-2 bg-white/20 rounded-xl ${urgencyConfig.pulse}`}>
                            {urgencyConfig.icon}
                        </div>
                        <div className="text-center">
                            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                                <span>Анализ готов</span>
                                <span className="text-xl">{urgencyConfig.emoji}</span>
                            </h2>
                            <p className="text-white/80 text-xs">
                                AI-анализ завершен
                            </p>
                        </div>
                    </div>
                    
                    <button
                        onClick={() => copyToClipboard(JSON.stringify(analysisResult, null, 2), 'export')}
                        className="p-2 hover:bg-white/20 rounded-xl transition-all duration-300 transform hover:scale-110"
                    >
                        <Share2 className="h-5 w-5 text-white" />
                    </button>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className={`bg-white/10 backdrop-blur-md px-2 py-2 transform transition-all duration-700 ${
                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
            }`} style={{transitionDelay: '0.1s'}}>
                <div className="flex space-x-1">
                    {[
                        { id: 'summary', label: 'Резюме', icon: '📋' },
                        { id: 'details', label: 'Детали', icon: '🔍' },
                        { id: 'response', label: 'Ответ', icon: '💬' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => handleSectionChange(tab.id)}
                            className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-300 ${
                                currentSection === tab.id
                                    ? 'bg-white text-gray-900 shadow-lg scale-105'
                                    : 'text-white/80 hover:bg-white/20'
                            }`}
                        >
                            <span className="mr-1">{tab.icon}</span>
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
                
                {/* Quick Stats */}
                <div className={`grid grid-cols-2 gap-3 transform transition-all duration-700 ${
                    animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
                }`} style={{transitionDelay: '0.2s'}}>
                    
                    <div className={`p-4 rounded-2xl ${urgencyConfig.bg} border-2 transform hover:scale-105 transition-all duration-300`}>
                        <div className="flex items-center space-x-2 mb-2">
                            {urgencyConfig.icon}
                            <span className="font-semibold text-gray-900 text-sm">Важность</span>
                        </div>
                        <p className={`text-lg font-bold ${urgencyConfig.color}`}>
                            {analysisResult?.urgency_level || 'Не определен'}
                        </p>
                    </div>
                </div>

                {/* Summary Section */}
                {currentSection === 'summary' && (
                    <div className={`space-y-4 transform transition-all duration-500 ${
                        animateIn ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.3s'}}>
                        
                        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                                    <span className="text-xl">💡</span>
                                    <span>Краткое содержание</span>
                                </h3>
                                <button
                                    onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'summary')}
                                    className="p-2 bg-blue-100 hover:bg-blue-200 rounded-xl transition-all duration-300 transform hover:scale-110"
                                >
                                    <Copy className="h-4 w-4 text-blue-600" />
                                </button>
                            </div>
                            
                            <div className="bg-gray-50 rounded-xl p-4">
                                <div className="text-gray-800 leading-relaxed">
                                    {formatText(analysisResult?.analysis?.main_content)}
                                </div>
                            </div>
                        </div>

                        {/* File Info */}
                        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
                            <h3 className="font-bold text-gray-900 mb-3 flex items-center space-x-2">
                                <span className="text-xl">📄</span>
                                <span>Информация о файле</span>
                            </h3>
                            
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Файл:</span>
                                    <span className="font-medium text-gray-900 truncate ml-2">
                                        {analysisResult?.file_name}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Язык:</span>
                                    <span className="font-medium text-gray-900">
                                        {analysisResult?.analysis_language === 'ru' ? 'Русский' : analysisResult?.analysis_language}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Details Section */}
                {currentSection === 'details' && (
                    <div className={`space-y-4 transform transition-all duration-500 ${
                        animateIn ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.3s'}}>
                        
                        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                                    <span className="text-xl">🔍</span>
                                    <span>Полный анализ</span>
                                </h3>
                                <button
                                    onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                                    className="p-2 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all duration-300"
                                >
                                    {showFullAnalysis ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                </button>
                            </div>

                            {showFullAnalysis && (
                                <div className="bg-gray-50 rounded-xl p-4 animate-fade-in-up">
                                    <div className="flex items-center justify-between mb-3">
                                        <span className="font-medium text-gray-900 text-sm">Полный текст анализа</span>
                                        <button
                                            onClick={() => copyToClipboard(analysisResult?.analysis?.full_analysis, 'full')}
                                            className="p-1 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
                                        >
                                            <Copy className="h-3 w-3 text-gray-600" />
                                        </button>
                                    </div>
                                    
                                    <div className="text-gray-700 leading-relaxed text-sm max-h-60 overflow-y-auto">
                                        {formatText(analysisResult?.analysis?.full_analysis)}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Detailed Sections */}
                        {analysisResult?.analysis?.formatted_sections && analysisResult.analysis.formatted_sections.length > 0 && (
                            <div className="space-y-3">
                                {analysisResult.analysis.formatted_sections.map((section, index) => (
                                    <div key={section.key} className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="text-lg">{section.icon}</span>
                                            <h4 className="font-bold text-gray-900 text-sm">{section.title}</h4>
                                        </div>
                                        <div className="text-gray-700 leading-relaxed text-sm">
                                            {formatText(section.content)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Response Section */}
                {currentSection === 'response' && (
                    <div className={`space-y-4 transform transition-all duration-500 ${
                        animateIn ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
                    }`} style={{transitionDelay: '0.3s'}}>
                        
                        {suggestedResponse && (
                            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-4 shadow-lg border border-green-200">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                                        <span className="text-xl">💬</span>
                                        <span>Предлагаемый ответ</span>
                                    </h3>
                                    <button
                                        onClick={() => setShowSuggestedResponse(!showSuggestedResponse)}
                                        className="px-3 py-1 bg-green-100 hover:bg-green-200 rounded-lg transition-all duration-300 text-sm font-medium text-green-700"
                                    >
                                        {showSuggestedResponse ? 'Скрыть' : 'Показать'}
                                    </button>
                                </div>

                                {showSuggestedResponse && (
                                    <div className="space-y-3 animate-fade-in-up">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-2">
                                                <Send className="h-4 w-4 text-green-600" />
                                                <span className="font-medium text-gray-900 text-sm">Готовый шаблон</span>
                                            </div>
                                            <button
                                                onClick={() => copyToClipboard(suggestedResponse.template, 'response')}
                                                className="flex items-center space-x-1 px-2 py-1 bg-green-100 hover:bg-green-200 rounded-lg transition-colors"
                                            >
                                                <Copy className="h-3 w-3 text-green-600" />
                                                <span className="text-xs text-green-600">
                                                    {copiedSection === 'response' ? 'Скопировано!' : 'Копировать'}
                                                </span>
                                            </button>
                                        </div>
                                        
                                        <div className="bg-white rounded-xl p-4 border-l-4 border-green-500">
                                            <pre className="whitespace-pre-wrap text-gray-800 leading-relaxed text-sm">
                                                {suggestedResponse.template}
                                            </pre>
                                        </div>
                                        
                                        <div className="flex items-center space-x-2 text-xs text-gray-600">
                                            <Bot className="h-3 w-3 text-green-500" />
                                            <span>Сгенерировано на основе анализа содержания</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Quick Actions */}
                        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
                            <h3 className="font-bold text-gray-900 mb-3 flex items-center space-x-2">
                                <span className="text-xl">⚡</span>
                                <span>Быстрые действия</span>
                            </h3>
                            
                            <div className="space-y-2">
                                <button
                                    onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'quick-summary')}
                                    className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 rounded-xl transition-all duration-300 transform hover:scale-105"
                                >
                                    <span className="flex items-center space-x-2">
                                        <Copy className="h-4 w-4 text-blue-600" />
                                        <span className="text-sm font-medium text-blue-900">Копировать резюме</span>
                                    </span>
                                    <span className="text-blue-600">📋</span>
                                </button>
                                
                                <button
                                    onClick={() => copyToClipboard(suggestedResponse?.template, 'quick-response')}
                                    className="w-full flex items-center justify-between p-3 bg-green-50 hover:bg-green-100 rounded-xl transition-all duration-300 transform hover:scale-105"
                                >
                                    <span className="flex items-center space-x-2">
                                        <Send className="h-4 w-4 text-green-600" />
                                        <span className="text-sm font-medium text-green-900">Копировать ответ</span>
                                    </span>
                                    <span className="text-green-600">💬</span>
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Bottom Actions */}
            <div className={`bg-white/10 backdrop-blur-md px-4 py-3 transform transition-all duration-700 ${
                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
            }`} style={{transitionDelay: '0.4s'}}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-xs text-white/80">
                        <TrendingUp className="h-3 w-3" />
                        <span>AI-анализ завершен</span>
                    </div>
                    
                    <button
                        onClick={handleClose}
                        className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl transition-all duration-300 transform hover:scale-105"
                    >
                        <span className="text-white text-sm font-medium">Готово</span>
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
            `}</style>
        </div>
    );
};

export default TelegramAnalysisResult;