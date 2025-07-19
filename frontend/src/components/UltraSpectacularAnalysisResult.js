import React, { useState, useEffect } from 'react';
import { 
    Sparkles, 
    Star,
    Diamond,
    Gem,
    Crown,
    Wand2,
    Flame,
    Zap,
    Eye,
    Copy,
    X,
    ChevronDown,
    ChevronUp,
    ArrowRight,
    Bot,
    Cpu,
    Activity,
    Layers,
    FileText,
    Lightbulb,
    Target,
    Clock,
    AlertTriangle,
    CheckCircle,
    Award,
    Trophy,
    Medal,
    Rocket,
    Palette,
    Comet,
    Heart,
    Shield,
    Globe
} from 'lucide-react';

const UltraSpectacularAnalysisResult = ({ analysisResult, onClose }) => {
    const [animateIn, setAnimateIn] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [expandedSections, setExpandedSections] = useState({});
    const [particleAnimation, setParticleAnimation] = useState(true);

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
                    bg: 'bg-red-50 border-red-300',
                    icon: <Flame className="h-8 w-8 text-red-500" />,
                    gradient: 'from-red-500 via-red-600 to-red-700',
                    glow: 'shadow-red-500/50 drop-shadow-2xl',
                    pulse: 'animate-pulse',
                    particles: 'text-red-400'
                };
            case 'СРЕДНИЙ':
            case 'MEDIUM':
                return {
                    color: 'text-amber-600',
                    bg: 'bg-amber-50 border-amber-300',
                    icon: <Flame className="h-8 w-8 text-red-500" />,
                    gradient: 'from-amber-500 via-orange-500 to-yellow-500',
                    glow: 'shadow-amber-500/50 drop-shadow-2xl',
                    pulse: '',
                    particles: 'text-amber-400'
                };
            case 'НИЗКИЙ':
            case 'LOW':
                return {
                    color: 'text-green-600',
                    bg: 'bg-green-50 border-green-300',
                    icon: <CheckCircle className="h-8 w-8 text-green-500" />,
                    gradient: 'from-green-500 via-emerald-500 to-teal-500',
                    glow: 'shadow-green-500/50 drop-shadow-2xl',
                    pulse: '',
                    particles: 'text-green-400'
                };
            default:
                return {
                    color: 'text-purple-600',
                    bg: 'bg-purple-50 border-purple-300',
                    icon: <Clock className="h-8 w-8 text-purple-500" />,
                    gradient: 'from-purple-500 via-purple-600 to-indigo-600',
                    glow: 'shadow-purple-500/50 drop-shadow-2xl',
                    pulse: '',
                    particles: 'text-purple-400'
                };
        }
    };

    const urgencyConfig = getUrgencyConfig(analysisResult?.urgency_level);

    // Парсинг полного анализа на отдельные секции
    const parseFullAnalysisToSections = () => {
        const analysis = analysisResult?.analysis;
        if (!analysis) return [];

        const sections = [];
        
        // Получаем полный анализ
        const fullText = analysis.full_analysis || analysis.main_content || '';
        if (!fullText) return [];

        // Разбиваем на секции по заголовкам
        const lines = fullText.split('\n');
        let currentSection = null;
        let currentContent = [];

        lines.forEach(line => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return;

            // Проверяем, является ли строка заголовком (содержит ключевые слова)
            const isHeader = (
                trimmedLine.toLowerCase().includes('резюме') ||
                trimmedLine.toLowerCase().includes('содержание') ||
                trimmedLine.toLowerCase().includes('отправитель') ||
                trimmedLine.toLowerCase().includes('тип') ||
                trimmedLine.toLowerCase().includes('ключевое') ||
                trimmedLine.toLowerCase().includes('действия') ||
                trimmedLine.toLowerCase().includes('сроки') ||
                trimmedLine.toLowerCase().includes('последствия') ||
                trimmedLine.toLowerCase().includes('срочность') ||
                trimmedLine.toLowerCase().includes('анализ') ||
                trimmedLine.toLowerCase().includes('основное') ||
                trimmedLine.toLowerCase().includes('важно') ||
                trimmedLine.toLowerCase().includes('требуется') ||
                trimmedLine.toLowerCase().includes('необходимо')
            ) && trimmedLine.length > 5;

            if (isHeader) {
                // Сохраняем предыдущую секцию
                if (currentSection && currentContent.length > 0) {
                    sections.push({
                        ...currentSection,
                        content: currentContent.join('\n')
                    });
                }

                // Начинаем новую секцию
                currentSection = {
                    id: `section-${sections.length}`,
                    title: trimmedLine.replace(/[*#:]/g, '').trim(),
                    icon: getIconForSection(trimmedLine),
                    color: getColorForSection(sections.length),
                    gradient: getGradientForSection(sections.length),
                    importance: getImportanceForSection(trimmedLine)
                };
                currentContent = [];
            } else {
                // Добавляем контент к текущей секции
                if (currentSection) {
                    currentContent.push(trimmedLine);
                } else {
                    // Если нет активной секции, создаем общую
                    if (!currentSection) {
                        currentSection = {
                            id: 'main-analysis',
                            title: 'Основной анализ',
                            icon: '📋',
                            color: 'text-blue-600',
                            gradient: 'from-blue-500 via-blue-600 to-indigo-600',
                            importance: 'high'
                        };
                        currentContent = [];
                    }
                    currentContent.push(trimmedLine);
                }
            }
        });

        // Добавляем последнюю секцию
        if (currentSection && currentContent.length > 0) {
            sections.push({
                ...currentSection,
                content: currentContent.join('\n')
            });
        }

        // Если секций нет, создаем одну общую
        if (sections.length === 0 && fullText) {
            sections.push({
                id: 'full-analysis',
                title: 'Полный анализ документа',
                content: fullText,
                icon: '📄',
                color: 'text-blue-600',
                gradient: 'from-blue-500 via-blue-600 to-indigo-600',
                importance: 'critical'
            });
        }

        return sections;
    };

    const getIconForSection = (title) => {
        const titleLower = title.toLowerCase();
        if (titleLower.includes('резюме') || titleLower.includes('содержание')) return '📋';
        if (titleLower.includes('отправитель') || titleLower.includes('sender')) return '👤';
        if (titleLower.includes('тип') || titleLower.includes('type')) return '📄';
        if (titleLower.includes('ключевое') || titleLower.includes('key')) return '🔑';
        if (titleLower.includes('действия') || titleLower.includes('actions')) return '⚡';
        if (titleLower.includes('сроки') || titleLower.includes('deadlines')) return '⏰';
        if (titleLower.includes('последствия') || titleLower.includes('consequences')) return '⚠️';
        if (titleLower.includes('срочность') || titleLower.includes('urgency')) return '🚨';
        if (titleLower.includes('анализ')) return '🔍';
        if (titleLower.includes('основное') || titleLower.includes('важно')) return '💡';
        if (titleLower.includes('требуется') || titleLower.includes('необходимо')) return '✅';
        return '📝';
    };

    const getColorForSection = (index) => {
        const colors = [
            'text-blue-600',
            'text-purple-600', 
            'text-indigo-600',
            'text-emerald-600',
            'text-red-600',
            'text-orange-600',
            'text-pink-600',
            'text-teal-600',
            'text-cyan-600'
        ];
        return colors[index % colors.length];
    };

    const getGradientForSection = (index) => {
        const gradients = [
            'from-blue-500 via-blue-600 to-indigo-600',
            'from-purple-500 via-purple-600 to-pink-600',
            'from-indigo-500 via-indigo-600 to-purple-600',
            'from-emerald-500 via-emerald-600 to-teal-600',
            'from-red-500 via-red-600 to-rose-600',
            'from-orange-500 via-orange-600 to-amber-600',
            'from-pink-500 via-pink-600 to-rose-600',
            'from-teal-500 via-teal-600 to-emerald-600',
            'from-cyan-500 via-cyan-600 to-blue-600'
        ];
        return gradients[index % gradients.length];
    };

    const getImportanceForSection = (title) => {
        const titleLower = title.toLowerCase();
        if (titleLower.includes('действия') || titleLower.includes('сроки') || titleLower.includes('срочность')) return 'critical';
        if (titleLower.includes('последствия') || titleLower.includes('ключевое') || titleLower.includes('важно')) return 'high';
        return 'medium';
    };

    const sections = parseFullAnalysisToSections();

    return (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-2 sm:p-4">
            <div className={`bg-white rounded-3xl shadow-2xl max-w-7xl w-full max-h-[98vh] overflow-hidden transform transition-all duration-1000 ${
                animateIn ? 'scale-100 opacity-100 rotate-0' : 'scale-95 opacity-0 rotate-1'
            }`}>
                
                {/* Ultra Spectacular Header */}
                <div className={`bg-gradient-to-r ${urgencyConfig.gradient} px-6 sm:px-8 py-6 sm:py-8 relative overflow-hidden`}>
                    
                    {/* Cosmic Background Effects */}
                    <div className="absolute inset-0 opacity-30">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 animate-pulse"></div>
                        <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
                            {[...Array(30)].map((_, i) => (
                                <div
                                    key={i}
                                    className={`absolute w-1 h-1 ${urgencyConfig.particles} rounded-full animate-pulse`}
                                    style={{
                                        left: `${Math.random() * 100}%`,
                                        top: `${Math.random() * 100}%`,
                                        animationDelay: `${Math.random() * 3}s`,
                                        animationDuration: `${2 + Math.random() * 3}s`
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                    
                    {/* Floating Magical Elements */}
                    <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute top-4 right-4 animate-bounce">
                            <Sparkles className="h-10 w-10 text-white/80" />
                        </div>
                        <div className="absolute top-6 right-20 animate-pulse" style={{animationDelay: '0.5s'}}>
                            <Star className="h-6 w-6 text-white/70" />
                        </div>
                        <div className="absolute bottom-4 left-4 animate-pulse" style={{animationDelay: '1s'}}>
                            <Diamond className="h-8 w-8 text-white/80" />
                        </div>
                        <div className="absolute bottom-6 left-20 animate-bounce" style={{animationDelay: '1.5s'}}>
                            <Gem className="h-5 w-5 text-white/70" />
                        </div>
                        <div className="absolute top-1/2 right-1/4 animate-ping" style={{animationDelay: '2s'}}>
                            <Crown className="h-6 w-6 text-white/60" />
                        </div>
                        <div className="absolute top-1/4 left-1/3 animate-pulse" style={{animationDelay: '2.5s'}}>
                            <Wand2 className="h-7 w-7 text-white/80" />
                        </div>
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <div className="flex items-center space-x-4 sm:space-x-6">
                            <div className={`p-4 sm:p-6 bg-white/20 rounded-3xl ${urgencyConfig.pulse} backdrop-blur-sm ${urgencyConfig.glow} border border-white/30`}>
                                <div className="relative">
                                    {urgencyConfig.icon}
                                    <div className="absolute inset-0 bg-white/30 rounded-full animate-ping"></div>
                                </div>
                            </div>
                            <div>
                                <h2 className="text-2xl sm:text-4xl font-black text-white mb-2 drop-shadow-2xl">
                                    ✨ АНАЛИЗ ДОКУМЕНТА
                                </h2>
                                <p className="text-white/90 text-base sm:text-xl drop-shadow-lg font-semibold">
                                    Полный интеллектуальный разбор
                                </p>
                            </div>
                        </div>
                        
                        <button
                            onClick={onClose}
                            className="p-3 sm:p-4 hover:bg-white/20 rounded-2xl transition-all duration-300 transform hover:scale-110 hover:rotate-90 backdrop-blur-sm border border-white/20"
                        >
                            <X className="h-6 w-6 sm:h-7 sm:w-7 text-white drop-shadow-lg" />
                        </button>
                    </div>
                </div>

                {/* Ultra Spectacular Content */}
                <div className="p-4 sm:p-8 max-h-[80vh] overflow-y-auto space-y-6 sm:space-y-8 bg-gradient-to-br from-gray-50/50 to-blue-50/50">
                    
                    {/* Cosmic Importance Indicator */}
                    <div className={`relative overflow-hidden rounded-3xl border-4 p-6 sm:p-8 text-center transform hover:scale-105 transition-all duration-700 ${urgencyConfig.bg} ${urgencyConfig.glow} shadow-2xl`}>
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -skew-x-12 animate-pulse"></div>
                        <div className="relative z-10">
                            <div className="flex justify-center mb-4 sm:mb-6">
                                <div className="relative p-4">
                                    {urgencyConfig.icon}
                                    <div className="absolute inset-0 bg-current rounded-full animate-ping opacity-40"></div>
                                    <div className="absolute inset-0 bg-current rounded-full animate-pulse opacity-20"></div>
                                </div>
                            </div>
                            <h3 className="text-xl sm:text-3xl font-black text-gray-900 mb-3">УРОВЕНЬ ВАЖНОСТИ</h3>
                            <p className={`text-2xl sm:text-4xl font-black ${urgencyConfig.color} drop-shadow-xl animate-pulse`}>
                                {analysisResult?.urgency_level || 'НЕ ОПРЕДЕЛЕН'}
                            </p>
                        </div>
                    </div>

                    {/* Ultra Spectacular Analysis Sections */}
                    <div className="space-y-6 sm:space-y-8">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl sm:text-3xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                                📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПО РАЗДЕЛАМ
                            </h2>
                            <p className="text-gray-600 text-sm sm:text-base">Каждый раздел содержит ключевую информацию из документа</p>
                        </div>

                        {sections.map((section, index) => (
                            <div
                                key={section.id}
                                className={`relative overflow-hidden rounded-3xl border-4 shadow-2xl transform transition-all duration-1000 hover:scale-105 hover:-rotate-1 ${
                                    section.importance === 'critical' ? 'border-red-400 bg-red-50/80 shadow-red-500/50' :
                                    section.importance === 'high' ? 'border-orange-400 bg-orange-50/80 shadow-orange-500/50' :
                                    'border-blue-400 bg-blue-50/80 shadow-blue-500/50'
                                }`}
                                style={{
                                    animationDelay: `${index * 0.2}s`
                                }}
                            >
                                {/* Cosmic Background for Each Section */}
                                <div className="absolute inset-0 opacity-20">
                                    <div className={`absolute inset-0 bg-gradient-to-r ${section.gradient} transform -skew-x-12`}></div>
                                    <div className="absolute inset-0 bg-gradient-to-l from-transparent via-white/30 to-transparent transform skew-x-12 animate-pulse"></div>
                                </div>
                                
                                {/* Critical Section Effects */}
                                {section.importance === 'critical' && (
                                    <div className="absolute top-2 right-2 animate-bounce">
                                        <Flame className="h-6 w-6 text-red-500" />
                                    </div>
                                )}
                                {section.importance === 'high' && (
                                    <div className="absolute top-2 right-2 animate-pulse">
                                        <Lightning className="h-6 w-6 text-orange-500" />
                                    </div>
                                )}

                                <div className="relative z-10 p-6 sm:p-8">
                                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 space-y-4 sm:space-y-0">
                                        <div className="flex items-center space-x-4">
                                            <div className={`p-4 rounded-2xl bg-gradient-to-r ${section.gradient} shadow-2xl transform hover:scale-110 transition-transform duration-300`}>
                                                <span className="text-2xl sm:text-3xl">{section.icon}</span>
                                            </div>
                                            <div>
                                                <h3 className={`text-xl sm:text-2xl font-black ${section.color} drop-shadow-md mb-2`}>
                                                    {section.title.toUpperCase()}
                                                </h3>
                                                {section.importance === 'critical' && (
                                                    <span className="inline-flex items-center px-3 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full animate-pulse">
                                                        🚨 КРИТИЧНО
                                                    </span>
                                                )}
                                                {section.importance === 'high' && (
                                                    <span className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-xs font-bold rounded-full">
                                                        ⚡ ВАЖНО
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-center space-x-2">
                                            <button
                                                onClick={() => copyToClipboard(section.content, section.id)}
                                                className={`p-3 rounded-2xl transition-all duration-300 transform hover:scale-110 bg-gradient-to-r ${section.gradient} text-white shadow-xl hover:shadow-2xl`}
                                            >
                                                <Copy className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={() => toggleSection(section.id)}
                                                className={`p-3 rounded-2xl transition-all duration-300 transform hover:scale-110 bg-gradient-to-r ${section.gradient} text-white shadow-xl hover:shadow-2xl`}
                                            >
                                                {expandedSections[section.id] ? 
                                                    <ChevronUp className="h-5 w-5" /> : 
                                                    <ChevronDown className="h-5 w-5" />
                                                }
                                            </button>
                                        </div>
                                    </div>
                                    
                                    {/* Content Display */}
                                    <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 border-2 border-white/50 shadow-xl">
                                        <div className={`${section.color} leading-relaxed text-base sm:text-lg ${
                                            !expandedSections[section.id] && section.content.length > 300 ? 'line-clamp-4' : ''
                                        }`}>
                                            {section.content.split('\n').map((line, lineIndex) => (
                                                line.trim() && (
                                                    <p key={lineIndex} className="mb-3 text-gray-800 font-medium">
                                                        {line.trim()}
                                                    </p>
                                                )
                                            ))}
                                        </div>
                                        
                                        {!expandedSections[section.id] && section.content.length > 300 && (
                                            <div className="mt-4 text-center">
                                                <button
                                                    onClick={() => toggleSection(section.id)}
                                                    className="text-blue-600 hover:text-blue-800 font-bold text-sm bg-blue-50 px-4 py-2 rounded-full hover:bg-blue-100 transition-colors"
                                                >
                                                    Показать полностью...
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {/* Copy Success Indicator */}
                                    {copiedSection === section.id && (
                                        <div className="absolute top-4 left-4 bg-green-500 text-white px-4 py-2 rounded-full text-sm font-bold animate-bounce shadow-xl">
                                            ✅ СКОПИРОВАНО!
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Ultra Spectacular Footer */}
                    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 p-6 sm:p-8 shadow-2xl">
                        <div className="absolute inset-0 opacity-20">
                            {[...Array(15)].map((_, i) => (
                                <div
                                    key={i}
                                    className="absolute w-2 h-2 text-white rounded-full animate-pulse"
                                    style={{
                                        left: `${Math.random() * 100}%`,
                                        top: `${Math.random() * 100}%`,
                                        animationDelay: `${Math.random() * 2}s`,
                                    }}
                                >✨</div>
                            ))}
                        </div>
                        
                        <div className="relative flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
                            <div className="flex items-center space-x-4">
                                <Bot className="h-8 w-8 text-white" />
                                <div className="text-white">
                                    <p className="font-bold text-lg">Анализ выполнен с использованием AI</p>
                                    <p className="text-white/80 text-sm">Искусственный интеллект последнего поколения</p>
                                </div>
                            </div>
                            
                            <button
                                onClick={onClose}
                                className="flex items-center space-x-3 px-8 py-4 bg-white/20 hover:bg-white/30 text-white rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-xl backdrop-blur-sm border border-white/30 font-bold"
                            >
                                <ArrowRight className="h-6 w-6" />
                                <span>ЗАВЕРШИТЬ ПРОСМОТР</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UltraSpectacularAnalysisResult;