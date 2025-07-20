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
    Shield,
    Brain,
    TrendingDown,
    AlertCircle,
    Scale,
    Users,
    Globe,
    BarChart3,
    Microscope,
    Fingerprint,
    Network,
    Radar,
    BookOpen,
    Briefcase,
    Activity
} from 'lucide-react';

const UltraSpectacularAnalysisResult = ({ analysisResult, onClose }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [expandedSections, setExpandedSections] = useState({});
    const [copiedSection, setCopiedSection] = useState('');
    const [animateIn, setAnimateIn] = useState(false);

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

    const toggleSection = (sectionKey) => {
        setExpandedSections(prev => ({
            ...prev,
            [sectionKey]: !prev[sectionKey]
        }));
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

    const urgencyConfig = getUrgencyConfig(analysisResult?.super_analysis?.urgency_assessment);

    // Получаем расширенные данные анализа
    const superAnalysis = analysisResult?.super_analysis || {};
    const psychProfile = superAnalysis.psychological_profile || {};
    const powerDynamics = superAnalysis.power_dynamics || {};
    const businessIntelligence = superAnalysis.business_intelligence || {};
    const riskAssessment = superAnalysis.risk_assessment || {};
    const legalCompliance = superAnalysis.legal_compliance || {};
    const predictiveScenarios = superAnalysis.predictive_scenarios || [];

    const tabs = [
        { 
            id: 'overview', 
            label: 'Обзор', 
            icon: <FileText className="h-4 w-4" />,
            color: 'blue' 
        },
        { 
            id: 'psychology', 
            label: 'Психология', 
            icon: <Brain className="h-4 w-4" />,
            color: 'purple' 
        },
        { 
            id: 'business', 
            label: 'Бизнес-анализ', 
            icon: <BarChart3 className="h-4 w-4" />,
            color: 'green' 
        },
        { 
            id: 'risks', 
            label: 'Риски', 
            icon: <Shield className="h-4 w-4" />,
            color: 'red' 
        },
        { 
            id: 'legal', 
            label: 'Правовые аспекты', 
            icon: <Scale className="h-4 w-4" />,
            color: 'indigo' 
        },
        { 
            id: 'predictions', 
            label: 'Прогнозы', 
            icon: <TrendingUp className="h-4 w-4" />,
            color: 'orange' 
        }
    ];

    const getTabColorClasses = (color, active) => {
        const colorClasses = {
            blue: active ? 'bg-blue-500 text-white' : 'text-blue-600 hover:bg-blue-50',
            purple: active ? 'bg-purple-500 text-white' : 'text-purple-600 hover:bg-purple-50',
            green: active ? 'bg-green-500 text-white' : 'text-green-600 hover:bg-green-50',
            red: active ? 'bg-red-500 text-white' : 'text-red-600 hover:bg-red-50',
            indigo: active ? 'bg-indigo-500 text-white' : 'text-indigo-600 hover:bg-indigo-50',
            orange: active ? 'bg-orange-500 text-white' : 'text-orange-600 hover:bg-orange-50'
        };
        return colorClasses[color] || colorClasses.blue;
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className={`bg-white rounded-2xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden transform transition-all duration-500 ${
                animateIn ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
            }`}>
                
                {/* Заголовок с градиентом */}
                <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-8 py-6 relative overflow-hidden`}>
                    <div className="absolute inset-0 opacity-10">
                        <div className="absolute top-4 right-4">
                            <Sparkles className="h-8 w-8" />
                        </div>
                        <div className="absolute bottom-4 left-4">
                            <Award className="h-6 w-6" />
                        </div>
                        <div className="absolute top-1/2 left-1/4 transform -translate-y-1/2">
                            <Microscope className="h-10 w-10" />
                        </div>
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className={`p-3 bg-white bg-opacity-20 rounded-full ${urgencyConfig.pulse}`}>
                                <Radar className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-1">
                                    Супер-анализ завершен
                                </h2>
                                <p className="text-white text-opacity-90 text-sm">
                                    Глубокий AI-анализ с проникновением во все аспекты документа
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

                <div className="flex flex-col h-full max-h-[calc(90vh-120px)]">
                    {/* Табы */}
                    <div className="flex space-x-1 p-6 pb-0 overflow-x-auto">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 whitespace-nowrap ${
                                    getTabColorClasses(tab.color, activeTab === tab.id)
                                }`}
                            >
                                {tab.icon}
                                <span className="font-medium">{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Содержимое */}
                    <div className="flex-1 overflow-y-auto p-6">
                        {activeTab === 'overview' && (
                            <div className="space-y-6">
                                {/* Ключевые метрики */}
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div className={`${urgencyConfig.bg} border-2 rounded-xl p-4 text-center`}>
                                        <div className="flex justify-center mb-2">
                                            {urgencyConfig.icon}
                                        </div>
                                        <h3 className="font-semibold text-gray-900 text-sm">Уровень важности</h3>
                                        <p className={`text-lg font-bold ${urgencyConfig.color}`}>
                                            {superAnalysis.urgency_assessment || 'Средний'}
                                        </p>
                                    </div>

                                    <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 text-center">
                                        <div className="flex justify-center mb-2">
                                            <BarChart3 className="h-5 w-5 text-blue-500" />
                                        </div>
                                        <h3 className="font-semibold text-gray-900 text-sm">Качество анализа</h3>
                                        <p className="text-blue-600 font-bold text-lg">
                                            {Math.round((superAnalysis.quality_score || 0.8) * 100)}%
                                        </p>
                                    </div>

                                    <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-4 text-center">
                                        <div className="flex justify-center mb-2">
                                            <Brain className="h-5 w-5 text-purple-500" />
                                        </div>
                                        <h3 className="font-semibold text-gray-900 text-sm">Психологический тон</h3>
                                        <p className="text-purple-600 font-bold text-lg">
                                            {psychProfile.emotional_tone === 'positive' ? 'Позитивный' : 
                                             psychProfile.emotional_tone === 'negative' ? 'Негативный' : 'Нейтральный'}
                                        </p>
                                    </div>

                                    <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4 text-center">
                                        <div className="flex justify-center mb-2">
                                            <FileText className="h-5 w-5 text-green-500" />
                                        </div>
                                        <h3 className="font-semibold text-gray-900 text-sm">Файл</h3>
                                        <p className="text-green-600 font-medium text-sm truncate">
                                            {analysisResult?.file_name}
                                        </p>
                                    </div>
                                </div>

                                {/* Исполнительное резюме */}
                                <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border border-indigo-100">
                                    <div className="flex items-center space-x-3 mb-4">
                                        <div className="p-2 bg-indigo-500 rounded-lg">
                                            <Award className="h-6 w-6 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-gray-900">Исполнительное резюме</h3>
                                        <button
                                            onClick={() => copyToClipboard(analysisResult?.summary, 'summary')}
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
                                            {analysisResult?.summary || 'Резюме анализа недоступно'}
                                        </p>
                                    </div>
                                </div>

                                {/* Ключевые инсайты */}
                                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
                                    <div className="flex items-center space-x-3 mb-4">
                                        <div className="p-2 bg-purple-500 rounded-lg">
                                            <Lightbulb className="h-6 w-6 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-gray-900">Ключевые инсайты</h3>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {(superAnalysis.insights || []).slice(0, 6).map((insight, index) => (
                                            <div key={index} className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-purple-400">
                                                <p className="text-gray-700">{insight}</p>
                                            </div>
                                        ))}
                                    </div>
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
                                        <Sparkles className="h-4 w-4" />
                                        <span>Супер-анализ выполнен с использованием современных AI технологий</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UltraSpectacularAnalysisResult;