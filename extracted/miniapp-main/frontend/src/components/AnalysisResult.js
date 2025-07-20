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
    Send
} from 'lucide-react';

const AnalysisResult = ({ analysisResult, onClose }) => {
    const [showFullAnalysis, setShowFullAnalysis] = useState(false);
    const [showSuggestedResponse, setShowSuggestedResponse] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [animateIn, setAnimateIn] = useState(false);

    useEffect(() => {
        // Анимация появления
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

        // Простая логика генерации ответа на основе содержания
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

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className={`bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto transform transition-all duration-500 ${
                animateIn ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
            }`}>
                
                {/* Заголовок с градиентом */}
                <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-8 py-6 relative overflow-hidden`}>
                    {/* Фоновые элементы */}
                    <div className="absolute inset-0 opacity-10">
                        <div className="absolute top-4 right-4">
                            <Sparkles className="h-8 w-8" />
                        </div>
                        <div className="absolute bottom-4 left-4">
                            <Award className="h-6 w-6" />
                        </div>
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className={`p-3 bg-white bg-opacity-20 rounded-full ${urgencyConfig.pulse}`}>
                                {urgencyConfig.icon}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-1">
                                    Анализ завершен
                                </h2>
                                <p className="text-white text-opacity-90 text-sm">
                                    AI-анализ документа завершен
                                </p>
                            </div>
                        </div>
                        
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                        >
                            <ExternalLink className="h-6 w-6 text-white" />
                        </button>
                    </div>
                </div>

                <div className="p-8 space-y-8">
                    
                    {/* Статистика и основная информация */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        
                        {/* Уровень важности */}
                        <div className={`${urgencyConfig.bg} border-2 rounded-xl p-6 text-center transform hover:scale-105 transition-transform`}>
                            <div className="flex justify-center mb-3">
                                {urgencyConfig.icon}
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-1">Уровень важности</h3>
                            <p className={`text-xl font-bold ${urgencyConfig.color}`}>
                                {analysisResult?.urgency_level || 'Не определен'}
                            </p>
                        </div>

                        {/* Тип документа */}
                        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 text-center transform hover:scale-105 transition-transform">
                            <div className="flex justify-center mb-3">
                                <FileText className="h-5 w-5 text-blue-500" />
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-1">Файл</h3>
                            <p className="text-blue-600 font-medium text-sm truncate">
                                {analysisResult?.file_name}
                            </p>
                        </div>
                    </div>

                    {/* Основное содержание */}
                    <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-8 border border-indigo-100">
                        <div className="flex items-center space-x-3 mb-6">
                            <div className="p-2 bg-indigo-500 rounded-lg">
                                <Lightbulb className="h-6 w-6 text-white" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900">Краткое содержание</h3>
                            <div className="flex-1"></div>
                            <button
                                onClick={() => copyToClipboard(analysisResult?.analysis?.main_content, 'summary')}
                                className="flex items-center space-x-2 px-3 py-1 bg-indigo-100 hover:bg-indigo-200 rounded-lg transition-colors"
                            >
                                <Copy className="h-4 w-4 text-indigo-600" />
                                <span className="text-sm text-indigo-600">
                                    {copiedSection === 'summary' ? 'Скопировано!' : 'Копировать'}
                                </span>
                            </button>
                        </div>
                        
                        <div className="bg-white rounded-lg p-6 shadow-sm">
                            <p className="text-gray-800 leading-relaxed text-lg">
                                {analysisResult?.analysis?.main_content}
                            </p>
                        </div>
                    </div>

                    {/* Предлагаемый ответ */}
                    {suggestedResponse && (
                        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-8 border border-green-100">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center space-x-3">
                                    <div className={`p-2 ${responseConfig.bg} rounded-lg`}>
                                        {responseConfig.icon}
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900">Предлагаемый ответ</h3>
                                    <span className={`px-3 py-1 ${responseConfig.bg} ${responseConfig.color} rounded-full text-sm font-medium`}>
                                        AI-генерация
                                    </span>
                                </div>
                                
                                <button
                                    onClick={() => setShowSuggestedResponse(!showSuggestedResponse)}
                                    className="flex items-center space-x-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                                >
                                    <MessageSquare className="h-4 w-4" />
                                    <span>{showSuggestedResponse ? 'Скрыть' : 'Показать'} ответ</span>
                                    {showSuggestedResponse ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                </button>
                            </div>

                            {showSuggestedResponse && (
                                <div className="bg-white rounded-lg p-6 shadow-sm space-y-4 transform transition-all duration-300">
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-2">
                                            <Send className="h-5 w-5 text-green-600" />
                                            <span className="font-semibold text-gray-900">Готовый шаблон ответа</span>
                                        </div>
                                        <button
                                            onClick={() => copyToClipboard(suggestedResponse.template, 'response')}
                                            className="flex items-center space-x-2 px-3 py-1 bg-green-100 hover:bg-green-200 rounded-lg transition-colors"
                                        >
                                            <Copy className="h-4 w-4 text-green-600" />
                                            <span className="text-sm text-green-600">
                                                {copiedSection === 'response' ? 'Скопировано!' : 'Копировать'}
                                            </span>
                                        </button>
                                    </div>
                                    
                                    <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-green-500">
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
                        </div>
                    )}

                    {/* Полный анализ */}
                    <div className="bg-gray-50 rounded-xl p-8 border border-gray-200">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-gray-600 rounded-lg">
                                    <Eye className="h-6 w-6 text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-900">Детальный анализ</h3>
                            </div>
                            
                            <button
                                onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                            >
                                <Eye className="h-4 w-4" />
                                <span>{showFullAnalysis ? 'Скрыть' : 'Показать'} детали</span>
                                {showFullAnalysis ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                            </button>
                        </div>

                        {showFullAnalysis && (
                            <div className="bg-white rounded-lg p-6 shadow-sm transform transition-all duration-300">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="font-semibold text-gray-900">Полный текст анализа</span>
                                    <button
                                        onClick={() => copyToClipboard(analysisResult?.analysis?.full_analysis, 'full')}
                                        className="flex items-center space-x-2 px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                                    >
                                        <Copy className="h-4 w-4 text-gray-600" />
                                        <span className="text-sm text-gray-600">
                                            {copiedSection === 'full' ? 'Скопировано!' : 'Копировать'}
                                        </span>
                                    </button>
                                </div>
                                
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <pre className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                                        {analysisResult?.analysis?.full_analysis}
                                    </pre>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Действия */}
                    <div className="flex flex-wrap gap-4 pt-6 border-t border-gray-200">
                        <button
                            onClick={() => copyToClipboard(JSON.stringify(analysisResult, null, 2), 'json')}
                            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                        >
                            <Download className="h-5 w-5" />
                            <span>Экспорт данных</span>
                        </button>
                        
                        <button
                            onClick={onClose}
                            className="flex items-center space-x-2 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                        >
                            <ArrowRight className="h-5 w-5" />
                            <span>Закрыть</span>
                        </button>
                        
                        <div className="flex-1"></div>
                        
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                            <ThumbsUp className="h-4 w-4" />
                            <span>Анализ выполнен с использованием современных AI технологий</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisResult;