import React, { useState, useEffect } from 'react';
import { 
    CheckCircle, 
    AlertTriangle, 
    Clock, 
    Eye, 
    Copy, 
    Star,
    ArrowRight,
    Zap,
    Target,
    Lightbulb,
    MessageSquare,
    Timer,
    TrendingUp,
    Sparkles,
    Award,
    FileText,
    Calendar,
    User,
    Building,
    ExternalLink,
    Heart,
    Send,
    X,
    ChevronDown,
    ChevronUp,
    Flame,
    Bookmark,
    Shield,
    Globe,
    Mail,
    Phone,
    MapPin,
    CreditCard,
    AlertCircle,
    Info,
    Layers,
    Briefcase,
    Archive,
    Flag,
    AlertOctagon,
    Megaphone,
    MessageCircle,
    Clock3,
    Hourglass,
    Zap as ZapIcon,
    Activity,
    Gauge,
    TrendingDown,
    Bot,
    Cpu,
    Wand2,
    Rocket,
    Crown,
    Diamond,
    Gem,
    Magic,
    Palette,
    Prism,
    Waves,
    Zap as Lightning,
    PartyPopper,
    Fireworks,
    Comet,
    Explosion,
    Sparkle,
    Twinkle,
    Glow,
    Flash,
    Beam,
    Rays,
    Aurora,
    Nebula,
    Supernova,
    Pulsar,
    Quasar,
    Magnetosphere,
    Helix,
    Spiral,
    Vortex,
    Whirlpool,
    Cyclone,
    Hurricane,
    Tornado,
    Windmill,
    Pinwheel,
    Ferris,
    Carousel,
    Kaleidoscope,
    Mandala,
    Fractal,
    Hologram,
    Prism as PrismIcon,
    Crystal,
    Snowflake
} from 'lucide-react';

const SpectacularAnalysisResult = ({ analysisResult, onClose }) => {
    const [animateIn, setAnimateIn] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [expandedSections, setExpandedSections] = useState({});

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
                    icon: <Flame className="h-6 w-6 text-red-500" />,
                    gradient: 'from-red-500 via-red-600 to-red-700',
                    pulse: 'animate-pulse',
                    glow: 'shadow-red-500/50',
                    effect: 'drop-shadow-lg',
                    particles: 'text-red-500'
                };
            case 'СРЕДНИЙ':
            case 'MEDIUM':
                return {
                    color: 'text-amber-600',
                    bg: 'bg-amber-50 border-amber-200',
                    icon: <Gauge className="h-6 w-6 text-amber-500" />,
                    gradient: 'from-amber-500 via-orange-500 to-yellow-500',
                    pulse: '',
                    glow: 'shadow-amber-500/50',
                    effect: 'drop-shadow-md',
                    particles: 'text-amber-500'
                };
            case 'НИЗКИЙ':
            case 'LOW':
                return {
                    color: 'text-green-600',
                    bg: 'bg-green-50 border-green-200',
                    icon: <CheckCircle className="h-6 w-6 text-green-500" />,
                    gradient: 'from-green-500 via-emerald-500 to-teal-500',
                    pulse: '',
                    glow: 'shadow-green-500/50',
                    effect: 'drop-shadow-md',
                    particles: 'text-green-500'
                };
            default:
                return {
                    color: 'text-gray-600',
                    bg: 'bg-gray-50 border-gray-200',
                    icon: <Clock className="h-6 w-6 text-gray-500" />,
                    gradient: 'from-gray-500 via-gray-600 to-slate-600',
                    pulse: '',
                    glow: 'shadow-gray-500/50',
                    effect: 'drop-shadow-md',
                    particles: 'text-gray-500'
                };
        }
    };

    const urgencyConfig = getUrgencyConfig(analysisResult?.urgency_level);

    // Преобразуем анализ в структурированные секции
    const parseAnalysisToSections = () => {
        const analysis = analysisResult?.analysis;
        if (!analysis) return [];

        const sections = [];
        
        // Если есть formatted_sections, используем их
        if (analysis.formatted_sections && analysis.formatted_sections.length > 0) {
            return analysis.formatted_sections.map(section => ({
                id: section.key,
                title: section.title,
                content: section.content,
                icon: section.icon || '📄',
                color: getColorForSection(section.key),
                gradient: getGradientForSection(section.key),
                importance: getImportanceForSection(section.key)
            }));
        }

        // Если нет formatted_sections, создаем базовую структуру
        const fullText = analysis.full_analysis || analysis.main_content || '';
        const parts = fullText.split('\n\n').filter(part => part.trim());
        
        parts.forEach((part, index) => {
            const lines = part.split('\n');
            const title = lines[0] || `Секция ${index + 1}`;
            const content = lines.slice(1).join('\n') || part;
            
            sections.push({
                id: `section-${index}`,
                title: title.replace(/[*#]/g, '').trim(),
                content: content.replace(/[*#]/g, '').trim(),
                icon: getIconForSection(title),
                color: getColorForSection(`section-${index}`),
                gradient: getGradientForSection(`section-${index}`),
                importance: getImportanceForSection(`section-${index}`)
            });
        });

        return sections;
    };

    const getColorForSection = (sectionKey) => {
        const colorMap = {
            'main_content': 'text-blue-600',
            'sender_info': 'text-purple-600',
            'document_type': 'text-indigo-600',
            'key_content': 'text-emerald-600',
            'required_actions': 'text-red-600',
            'deadlines': 'text-orange-600',
            'consequences': 'text-pink-600',
            'urgency_level': 'text-yellow-600',
            'response_template': 'text-green-600'
        };
        return colorMap[sectionKey] || `text-${['blue', 'purple', 'indigo', 'emerald', 'red', 'orange', 'pink', 'yellow', 'green'][Math.floor(Math.random() * 9)]}-600`;
    };

    const getGradientForSection = (sectionKey) => {
        const gradientMap = {
            'main_content': 'from-blue-500 via-blue-600 to-indigo-600',
            'sender_info': 'from-purple-500 via-purple-600 to-pink-600',
            'document_type': 'from-indigo-500 via-indigo-600 to-purple-600',
            'key_content': 'from-emerald-500 via-emerald-600 to-teal-600',
            'required_actions': 'from-red-500 via-red-600 to-rose-600',
            'deadlines': 'from-orange-500 via-orange-600 to-amber-600',
            'consequences': 'from-pink-500 via-pink-600 to-rose-600',
            'urgency_level': 'from-yellow-500 via-yellow-600 to-orange-600',
            'response_template': 'from-green-500 via-green-600 to-emerald-600'
        };
        return gradientMap[sectionKey] || 'from-gray-500 via-gray-600 to-slate-600';
    };

    const getImportanceForSection = (sectionKey) => {
        const importanceMap = {
            'required_actions': 'critical',
            'deadlines': 'high',
            'consequences': 'high',
            'urgency_level': 'critical',
            'main_content': 'high',
            'key_content': 'high',
            'sender_info': 'medium',
            'document_type': 'medium',
            'response_template': 'medium'
        };
        return importanceMap[sectionKey] || 'medium';
    };

    const getIconForSection = (title) => {
        const titleLower = title.toLowerCase();
        if (titleLower.includes('содержание') || titleLower.includes('резюме')) return '📋';
        if (titleLower.includes('отправитель') || titleLower.includes('sender')) return '👤';
        if (titleLower.includes('тип') || titleLower.includes('type')) return '📄';
        if (titleLower.includes('ключевое') || titleLower.includes('key')) return '🔑';
        if (titleLower.includes('действия') || titleLower.includes('actions')) return '⚡';
        if (titleLower.includes('сроки') || titleLower.includes('deadlines')) return '⏰';
        if (titleLower.includes('последствия') || titleLower.includes('consequences')) return '⚠️';
        if (titleLower.includes('срочность') || titleLower.includes('urgency')) return '🚨';
        if (titleLower.includes('ответ') || titleLower.includes('response')) return '💬';
        return '📄';
    };

    const sections = parseAnalysisToSections();

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className={`bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-hidden transform transition-all duration-1000 ${
                animateIn ? 'scale-100 opacity-100 rotate-0' : 'scale-95 opacity-0 rotate-1'
            }`}>
                
                {/* Spectacular Header */}
                <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-8 py-6 relative overflow-hidden`}>
                    {/* Animated Background Effects */}
                    <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-4 right-4 animate-bounce">
                            <Sparkles className="h-8 w-8 text-white" />
                        </div>
                        <div className="absolute bottom-4 left-4 animate-pulse" style={{animationDelay: '0.5s'}}>
                            <Star className="h-6 w-6 text-white" />
                        </div>
                        <div className="absolute top-1/2 right-1/4 animate-ping" style={{animationDelay: '1s'}}>
                            <Diamond className="h-4 w-4 text-white" />
                        </div>
                        <div className="absolute bottom-1/3 right-1/3 animate-pulse" style={{animationDelay: '1.5s'}}>
                            <Gem className="h-5 w-5 text-white" />
                        </div>
                        <div className="absolute top-1/4 left-1/3 animate-bounce" style={{animationDelay: '2s'}}>
                            <Crown className="h-4 w-4 text-white" />
                        </div>
                    </div>
                    
                    {/* Floating Particles */}
                    <div className="absolute inset-0 pointer-events-none">
                        {[...Array(12)].map((_, i) => (
                            <div
                                key={i}
                                className={`absolute w-2 h-2 ${urgencyConfig.particles} rounded-full animate-pulse`}
                                style={{
                                    left: `${Math.random() * 100}%`,
                                    top: `${Math.random() * 100}%`,
                                    animationDelay: `${Math.random() * 2}s`,
                                    animationDuration: `${2 + Math.random() * 2}s`
                                }}
                            />
                        ))}
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className={`p-4 bg-white/20 rounded-2xl ${urgencyConfig.pulse} backdrop-blur-sm`}>
                                <div className="relative">
                                    {urgencyConfig.icon}
                                    <div className="absolute inset-0 bg-white/30 rounded-full animate-ping"></div>
                                </div>
                            </div>
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-1 drop-shadow-lg">
                                    ✨ Анализ завершен
                                </h2>
                                <p className="text-white/90 text-lg drop-shadow-md">
                                    Интеллектуальный анализ документа
                                </p>
                            </div>
                        </div>
                        
                        <button
                            onClick={onClose}
                            className="p-3 hover:bg-white/20 rounded-2xl transition-all duration-300 transform hover:scale-110 hover:rotate-90"
                        >
                            <X className="h-6 w-6 text-white drop-shadow-lg" />
                        </button>
                    </div>
                </div>

                {/* Spectacular Content */}
                <div className="p-8 max-h-[80vh] overflow-y-auto space-y-8">
                    
                    {/* Importance Indicator */}
                    <div className={`relative overflow-hidden rounded-2xl border-2 p-6 text-center transform hover:scale-105 transition-all duration-500 ${urgencyConfig.bg} ${urgencyConfig.glow} shadow-2xl`}>
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 animate-pulse"></div>
                        <div className="relative z-10">
                            <div className="flex justify-center mb-4">
                                <div className="relative">
                                    {urgencyConfig.icon}
                                    <div className="absolute inset-0 bg-current rounded-full animate-ping opacity-30"></div>
                                </div>
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">Уровень важности</h3>
                            <p className={`text-3xl font-black ${urgencyConfig.color} drop-shadow-lg`}>
                                {analysisResult?.urgency_level || 'Не определен'}
                            </p>
                        </div>
                    </div>

                    {/* Spectacular Analysis Sections */}
                    <div className="space-y-6">
                        {sections.map((section, index) => (
                            <div
                                key={section.id}
                                className={`relative overflow-hidden rounded-2xl border-2 shadow-2xl transform transition-all duration-700 hover:scale-105 ${
                                    section.importance === 'critical' ? 'border-red-300 bg-red-50' :
                                    section.importance === 'high' ? 'border-orange-300 bg-orange-50' :
                                    'border-blue-300 bg-blue-50'
                                }`}
                                style={{
                                    animationDelay: `${index * 0.1}s`
                                }}
                            >
                                {/* Animated Background */}
                                <div className="absolute inset-0 opacity-10">
                                    <div className={`absolute inset-0 bg-gradient-to-r ${section.gradient} transform -skew-x-12`}></div>
                                </div>
                                
                                {/* Floating Effects */}
                                <div className="absolute inset-0 pointer-events-none">
                                    {section.importance === 'critical' && (
                                        <div className="absolute top-2 right-2 animate-bounce">
                                            <Flame className="h-4 w-4 text-red-500" />
                                        </div>
                                    )}
                                    {section.importance === 'high' && (
                                        <div className="absolute top-2 right-2 animate-pulse">
                                            <Zap className="h-4 w-4 text-orange-500" />
                                        </div>
                                    )}
                                </div>

                                <div className="relative z-10 p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-3">
                                            <div className={`p-3 rounded-xl bg-gradient-to-r ${section.gradient} shadow-lg`}>
                                                <span className="text-2xl">{section.icon}</span>
                                            </div>
                                            <div>
                                                <h3 className={`text-xl font-bold ${section.color} drop-shadow-md`}>
                                                    {section.title}
                                                </h3>
                                                {section.importance === 'critical' && (
                                                    <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                                                        🚨 Критично
                                                    </span>
                                                )}
                                                {section.importance === 'high' && (
                                                    <span className="inline-flex items-center px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded-full">
                                                        ⚡ Важно
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-center space-x-2">
                                            <button
                                                onClick={() => copyToClipboard(section.content, section.id)}
                                                className={`p-2 rounded-lg transition-all duration-300 transform hover:scale-110 bg-gradient-to-r ${section.gradient} text-white shadow-lg hover:shadow-xl`}
                                            >
                                                <Copy className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => toggleSection(section.id)}
                                                className={`p-2 rounded-lg transition-all duration-300 transform hover:scale-110 bg-gradient-to-r ${section.gradient} text-white shadow-lg hover:shadow-xl`}
                                            >
                                                {expandedSections[section.id] ? 
                                                    <ChevronUp className="h-4 w-4" /> : 
                                                    <ChevronDown className="h-4 w-4" />
                                                }
                                            </button>
                                        </div>
                                    </div>
                                    
                                    {/* Content Preview */}
                                    <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-white/30">
                                        <div className={`${section.color} leading-relaxed ${
                                            !expandedSections[section.id] ? 'line-clamp-3' : ''
                                        }`}>
                                            {section.content.split('\n').map((line, lineIndex) => (
                                                <p key={lineIndex} className="mb-2 text-gray-700">
                                                    {line}
                                                </p>
                                            ))}
                                        </div>
                                        
                                        {!expandedSections[section.id] && section.content.length > 200 && (
                                            <div className="mt-2 text-center">
                                                <button
                                                    onClick={() => toggleSection(section.id)}
                                                    className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                                                >
                                                    Показать полностью...
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {/* Status Indicator */}
                                    {copiedSection === section.id && (
                                        <div className="absolute top-2 left-2 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium animate-bounce">
                                            Скопировано! ✅
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Spectacular Footer */}
                    <div className="flex items-center justify-center space-x-4 pt-8 border-t border-gray-200">
                        <button
                            onClick={onClose}
                            className="flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-2xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                        >
                            <ArrowRight className="h-5 w-5" />
                            <span className="font-semibold">Завершить анализ</span>
                        </button>
                        
                        <div className="flex items-center space-x-2 text-gray-500">
                            <Bot className="h-5 w-5" />
                            <span className="text-sm">Анализ выполнен с использованием AI</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SpectacularAnalysisResult;