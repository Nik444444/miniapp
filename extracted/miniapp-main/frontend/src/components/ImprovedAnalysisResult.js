import React, { useState, useEffect } from 'react';
import { 
    CheckCircle, 
    AlertTriangle, 
    Clock, 
    Eye, 
    Copy, 
    Download, 
    Star,
    ArrowRight,
    Mail,
    Zap,
    Target,
    Lightbulb,
    MessageSquare,
    ThumbsUp,
    Timer,
    TrendingUp,
    Sparkles,
    Award,
    FileText,
    Tag,
    Calendar,
    User,
    Building,
    ExternalLink,
    ChevronDown,
    ChevronUp,
    Heart,
    Send,
    X,
    BookOpen,
    Flag,
    AlertCircle,
    Info,
    Globe
} from 'lucide-react';
import { GlassCard, GradientText, FloatingElement, PulsingDot, MagneticElement, ShimmerEffect } from './UIEffects';

const ImprovedAnalysisResult = ({ analysisResult, onClose }) => {
    const [showFullAnalysis, setShowFullAnalysis] = useState(false);
    const [showSuggestedResponse, setShowSuggestedResponse] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [animateIn, setAnimateIn] = useState(false);
    const [selectedSection, setSelectedSection] = useState(null);

    useEffect(() => {
        const timer = setTimeout(() => setAnimateIn(true), 100);
        return () => clearTimeout(timer);
    }, []);

    const copyToClipboard = async (text, section) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedSection(section);
            setTimeout(() => setCopiedSection(''), 2000);
        } catch (err) {
            console.error('Ошибка копирования:', err);
        }
    };

    const getUrgencyConfig = (urgency) => {
        switch (urgency?.toUpperCase()) {
            case 'ВЫСОКИЙ':
            case 'HIGH':
                return {
                    color: 'text-red-600',
                    bg: 'bg-red-50 border-red-200',
                    icon: <Zap className="h-5 w-5 text-red-500" />,
                    gradient: 'from-red-500 to-red-600',
                    pulse: 'animate-pulse'
                };
            case 'СРЕДНИЙ':
            case 'MEDIUM':
                return {
                    color: 'text-amber-600',
                    bg: 'bg-amber-50 border-amber-200',
                    icon: <Target className="h-5 w-5 text-amber-500" />,
                    gradient: 'from-amber-500 to-orange-500',
                    pulse: ''
                };
            case 'НИЗКИЙ':
            case 'LOW':
                return {
                    color: 'text-green-600',
                    bg: 'bg-green-50 border-green-200',
                    icon: <CheckCircle className="h-5 w-5 text-green-500" />,
                    gradient: 'from-green-500 to-emerald-500',
                    pulse: ''
                };
            default:
                return {
                    color: 'text-gray-600',
                    bg: 'bg-gray-50 border-gray-200',
                    icon: <Clock className="h-5 w-5 text-gray-500" />,
                    gradient: 'from-gray-500 to-gray-600',
                    pulse: ''
                };
        }
    };

    const urgencyConfig = getUrgencyConfig(analysisResult?.urgency_level);

    // Генерируем предлагаемый ответ на основе анализа
    const generateSuggestedResponse = () => {
        const analysis = analysisResult?.analysis;
        if (!analysis) return null;

        const content = analysis.main_content?.toLowerCase() || '';
        const fullAnalysis = analysis.full_analysis?.toLowerCase() || '';
        
        let responseTemplate = '';
        let responseType = 'info';

        if (content.includes('счет') || content.includes('оплата') || content.includes('платеж')) {
            responseTemplate = `Уважаемые господа,

Благодарю за направленный счет. Подтверждаю получение документа и информирую, что оплата будет произведена в установленные сроки.

При необходимости уточнения деталей готов предоставить дополнительную информацию.

С уважением`;
            responseType = 'payment';
        } else if (content.includes('приглашение') || content.includes('встреча') || content.includes('собрание')) {
            responseTemplate = `Уважаемые коллеги,

Благодарю за приглашение. Подтверждаю свое участие в предложенном мероприятии.

Прошу сообщить дополнительные детали при необходимости.

С наилучшими пожеланиями`;
            responseType = 'meeting';
        } else if (content.includes('заявление') || content.includes('документ') || content.includes('справка')) {
            responseTemplate = `Добрый день,

Подтверждаю получение Вашего обращения. Документ принят к рассмотрению.

О результатах рассмотрения будет сообщено дополнительно.

С уважением`;
            responseType = 'document';
        } else if (urgencyConfig.color === 'text-red-600') {
            responseTemplate = `Уважаемые господа,

Благодарю за срочное уведомление. Принимаю к сведению важность данного сообщения и готов оперативно предоставить необходимую информацию или предпринять требуемые действия.

Прошу связаться со мной для уточнения деталей.

С уважением`;
            responseType = 'urgent';
        } else {
            responseTemplate = `Уважаемые господа,

Благодарю за Ваше письмо. Информация принята к сведению.

При необходимости готов предоставить дополнительную информацию или ответить на Ваши вопросы.

С уважением`;
            responseType = 'general';
        }

        return { template: responseTemplate, type: responseType };
    };

    const suggestedResponse = generateSuggestedResponse();

    const getResponseTypeConfig = (type) => {
        switch (type) {
            case 'payment':
                return { icon: <Star className="h-5 w-5" />, color: 'text-blue-600', bg: 'bg-blue-50' };
            case 'meeting':
                return { icon: <Calendar className="h-5 w-5" />, color: 'text-green-600', bg: 'bg-green-50' };
            case 'document':
                return { icon: <FileText className="h-5 w-5" />, color: 'text-purple-600', bg: 'bg-purple-50' };
            case 'urgent':
                return { icon: <Zap className="h-5 w-5" />, color: 'text-red-600', bg: 'bg-red-50' };
            default:
                return { icon: <MessageSquare className="h-5 w-5" />, color: 'text-gray-600', bg: 'bg-gray-50' };
        }
    };

    const responseConfig = getResponseTypeConfig(suggestedResponse?.type);

    // Функция для красивого форматирования текста
    const formatText = (text) => {
        if (!text) return '';
        
        // Убираем звездочки и другие символы форматирования
        let formatted = text.replace(/\*+/g, '').replace(/#+/g, '').trim();
        
        // Разбиваем на абзацы
        const paragraphs = formatted.split('\n').filter(p => p.trim());
        
        return paragraphs.map((paragraph, index) => {
            const trimmed = paragraph.trim();
            if (!trimmed) return null;
            
            // Проверяем если это заголовок (большие буквы)
            const isHeader = trimmed === trimmed.toUpperCase() && trimmed.length > 3;
            
            if (isHeader) {
                return (
                    <h4 key={index} className="font-bold text-lg text-gray-900 mt-4 mb-2 flex items-center space-x-2">
                        <BookOpen className="h-5 w-5 text-blue-500" />
                        <span>{trimmed}</span>
                    </h4>
                );
            } else {
                return (
                    <p key={index} className="text-gray-700 leading-relaxed mb-3">
                        {trimmed}
                    </p>
                );
            }
        });
    };

    // Извлекаем секции из formatted_sections если они есть
    const formattedSections = analysisResult?.analysis?.formatted_sections || [];

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className={`bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto transform transition-all duration-700 ${
                animateIn ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
            }`}>
                
                {/* Hero Header */}
                <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-8 py-8 relative overflow-hidden`}>
                    {/* Background Effects */}
                    <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-4 right-4 animate-float">
                            <Sparkles className="h-8 w-8 text-white" />
                        </div>
                        <div className="absolute bottom-4 left-4 animate-float" style={{animationDelay: '1s'}}>
                            <Award className="h-6 w-6 text-white" />
                        </div>
                        <div className="absolute top-1/2 right-1/4 animate-float" style={{animationDelay: '2s'}}>
                            <Star className="h-5 w-5 text-white" />
                        </div>
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <FloatingElement>
                            <div className="flex items-center space-x-6">
                                <div className={`p-4 bg-white/20 rounded-2xl ${urgencyConfig.pulse}`}>
                                    {urgencyConfig.icon}
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold text-white mb-2">
                                        Анализ завершен успешно
                                    </h2>
                                    <p className="text-white/90 text-lg flex items-center space-x-3">
                                        <span>AI-анализ документа</span>
                                        <span className="w-2 h-2 bg-white/60 rounded-full"></span>
                                        <span>Завершен успешно</span>
                                    </p>
                                </div>
                            </div>
                        </FloatingElement>
                        
                        <MagneticElement>
                            <button
                                onClick={onClose}
                                className="p-3 hover:bg-white/20 rounded-2xl transition-all duration-300 hover:scale-110"
                            >
                                <X className="h-6 w-6 text-white" />
                            </button>
                        </MagneticElement>
                    </div>
                </div>

                <div className="p-8 space-y-8">
                    
                    {/* Quick Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        
                        <FloatingElement delay={0.1}>
                            <GlassCard className={`p-6 text-center transform hover:scale-105 transition-all duration-300 ${urgencyConfig.bg} border-2`}>
                                <div className="flex justify-center mb-3">
                                    {urgencyConfig.icon}
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-1">Уровень важности</h3>
                                <p className={`text-xl font-bold ${urgencyConfig.color}`}>
                                    {analysisResult?.urgency_level || 'Не определен'}
                                </p>
                            </GlassCard>
                        </FloatingElement>

                        <FloatingElement delay={0.2}>
                            <GlassCard className="p-6 text-center bg-blue-50 border-2 border-blue-200 transform hover:scale-105 transition-all duration-300">
                                <div className="flex justify-center mb-3">
                                    <FileText className="h-5 w-5 text-blue-500" />
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-1">Файл</h3>
                                <p className="text-blue-600 font-medium text-sm truncate">
                                    {analysisResult?.file_name}
                                </p>
                            </GlassCard>
                        </FloatingElement>

                        <FloatingElement delay={0.4}>
                            <GlassCard className="p-6 text-center bg-green-50 border-2 border-green-200 transform hover:scale-105 transition-all duration-300">
                                <div className="flex justify-center mb-3">
                                    <Globe className="h-5 w-5 text-green-500" />
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-1">Язык</h3>
                                <p className="text-green-600 font-medium">
                                    {analysisResult?.analysis_language === 'ru' ? 'Русский' : analysisResult?.analysis_language}
                                </p>
                            </GlassCard>
                        </FloatingElement>
                    </div>

                    {/* Main Content */}
                    <FloatingElement delay={0.5}>
                        <GlassCard className="p-8 bg-gradient-to-br from-indigo-50/80 to-blue-50/80 border border-indigo-100">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="p-3 bg-indigo-500 rounded-xl shadow-lg">
                                    <Lightbulb className="h-6 w-6 text-white" />
                                </div>
                                <h3 className="text-2xl font-bold text-gray-900">Краткое содержание</h3>
                                <div className="flex-1"></div>
                                <MagneticElement>
                                    <button
                                        onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'summary')}
                                        className="flex items-center space-x-2 px-4 py-2 bg-indigo-100 hover:bg-indigo-200 rounded-xl transition-all duration-300 hover:scale-105"
                                    >
                                        <Copy className="h-4 w-4 text-indigo-600" />
                                        <span className="text-sm text-indigo-600 font-medium">
                                            {copiedSection === 'summary' ? 'Скопировано!' : 'Копировать'}
                                        </span>
                                    </button>
                                </MagneticElement>
                            </div>
                            
                            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg">
                                <div className="text-gray-800 leading-relaxed text-lg">
                                    {formatText(analysisResult?.analysis?.main_content)}
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Detailed Sections */}
                    {formattedSections.length > 0 && (
                        <FloatingElement delay={0.6}>
                            <GlassCard className="p-8">
                                <div className="flex items-center space-x-4 mb-6">
                                    <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                        <BookOpen className="h-6 w-6 text-white" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-gray-900">Детальный анализ</h3>
                                </div>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {formattedSections.map((section, index) => (
                                        <div key={section.key} className="relative">
                                            <div className={`p-6 rounded-xl bg-${section.color}-50 border border-${section.color}-200 hover:shadow-lg transition-all duration-300`}>
                                                <div className="flex items-center space-x-3 mb-4">
                                                    <span className="text-2xl">{section.icon}</span>
                                                    <h4 className="font-bold text-gray-900">{section.title}</h4>
                                                </div>
                                                <div className="text-gray-700 leading-relaxed">
                                                    {formatText(section.content)}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </GlassCard>
                        </FloatingElement>
                    )}

                    {/* Suggested Response */}
                    {suggestedResponse && (
                        <FloatingElement delay={0.7}>
                            <GlassCard className="p-8 bg-gradient-to-br from-green-50/80 to-emerald-50/80 border border-green-100">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="flex items-center space-x-4">
                                        <div className={`p-3 ${responseConfig.bg} rounded-xl`}>
                                            {responseConfig.icon}
                                        </div>
                                        <div>
                                            <h3 className="text-2xl font-bold text-gray-900 mb-1">Предлагаемый ответ</h3>
                                            <span className={`px-3 py-1 ${responseConfig.bg} ${responseConfig.color} rounded-full text-sm font-medium`}>
                                                AI-генерация
                                            </span>
                                        </div>
                                    </div>
                                    
                                    <MagneticElement>
                                        <button
                                            onClick={() => setShowSuggestedResponse(!showSuggestedResponse)}
                                            className="flex items-center space-x-3 px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl transition-all duration-300 hover:scale-105 font-medium"
                                        >
                                            <MessageSquare className="h-5 w-5" />
                                            <span>{showSuggestedResponse ? 'Скрыть' : 'Показать'} ответ</span>
                                            {showSuggestedResponse ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                        </button>
                                    </MagneticElement>
                                </div>

                                {showSuggestedResponse && (
                                    <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg space-y-4 animate-fade-in-up">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center space-x-2">
                                                <Send className="h-5 w-5 text-green-600" />
                                                <span className="font-semibold text-gray-900">Готовый шаблон ответа</span>
                                            </div>
                                            <button
                                                onClick={() => copyToClipboard(suggestedResponse.template, 'response')}
                                                className="flex items-center space-x-2 px-3 py-2 bg-green-100 hover:bg-green-200 rounded-lg transition-colors"
                                            >
                                                <Copy className="h-4 w-4 text-green-600" />
                                                <span className="text-sm text-green-600">
                                                    {copiedSection === 'response' ? 'Скопировано!' : 'Копировать'}
                                                </span>
                                            </button>
                                        </div>
                                        
                                        <div className="bg-gray-50 rounded-xl p-6 border-l-4 border-green-500">
                                            <pre className="whitespace-pre-wrap text-gray-800 leading-relaxed font-medium">
                                                {suggestedResponse.template}
                                            </pre>
                                        </div>
                                        
                                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                                            <Heart className="h-4 w-4 text-red-500" />
                                            <span>Этот ответ сгенерирован на основе анализа содержания письма</span>
                                        </div>
                                    </div>
                                )}
                            </GlassCard>
                        </FloatingElement>
                    )}

                    {/* Full Analysis */}
                    <FloatingElement delay={0.8}>
                        <GlassCard className="p-8 bg-gray-50/80">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center space-x-4">
                                    <div className="p-3 bg-gray-600 rounded-xl">
                                        <Eye className="h-6 w-6 text-white" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-gray-900">Полный анализ</h3>
                                </div>
                                
                                <MagneticElement>
                                    <button
                                        onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                                        className="flex items-center space-x-3 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl transition-all duration-300 hover:scale-105 font-medium"
                                    >
                                        <Eye className="h-5 w-5" />
                                        <span>{showFullAnalysis ? 'Скрыть' : 'Показать'} детали</span>
                                        {showFullAnalysis ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                    </button>
                                </MagneticElement>
                            </div>

                            {showFullAnalysis && (
                                <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg animate-fade-in-up">
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="font-semibold text-gray-900">Полный текст анализа</span>
                                        <button
                                            onClick={() => copyToClipboard(analysisResult?.analysis?.full_analysis, 'full')}
                                            className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                                        >
                                            <Copy className="h-4 w-4 text-gray-600" />
                                            <span className="text-sm text-gray-600">
                                                {copiedSection === 'full' ? 'Скопировано!' : 'Копировать'}
                                            </span>
                                        </button>
                                    </div>
                                    
                                    <div className="bg-gray-50 rounded-xl p-6">
                                        <div className="text-gray-700 leading-relaxed">
                                            {formatText(analysisResult?.analysis?.full_analysis)}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </GlassCard>
                    </FloatingElement>

                    {/* Action Buttons */}
                    <FloatingElement delay={0.9}>
                        <div className="flex flex-wrap gap-4 pt-6 border-t border-gray-200 justify-between">
                            <div className="flex flex-wrap gap-4">
                                <MagneticElement>
                                    <button
                                        onClick={() => copyToClipboard(JSON.stringify(analysisResult, null, 2), 'json')}
                                        className="flex items-center space-x-3 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-300 hover:scale-105 font-medium"
                                    >
                                        <Download className="h-5 w-5" />
                                        <span>Экспорт данных</span>
                                    </button>
                                </MagneticElement>
                                
                                <MagneticElement>
                                    <button
                                        onClick={onClose}
                                        className="flex items-center space-x-3 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl transition-all duration-300 hover:scale-105 font-medium"
                                    >
                                        <ArrowRight className="h-5 w-5" />
                                        <span>Закрыть</span>
                                    </button>
                                </MagneticElement>
                            </div>
                            
                            <div className="flex items-center space-x-3 text-sm text-gray-500">
                                <ThumbsUp className="h-4 w-4" />
                                <span>Анализ выполнен с использованием современных AI технологий</span>
                            </div>
                        </div>
                    </FloatingElement>
                </div>
            </div>
        </div>
    );
};

export default ImprovedAnalysisResult;