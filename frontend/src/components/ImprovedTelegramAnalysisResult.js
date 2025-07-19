import React, { useState, useEffect } from 'react';
import { 
    ArrowLeft,
    Copy,
    FileText,
    Eye,
    CheckCircle,
    AlertTriangle,
    Clock,
    Target,
    Lightbulb,
    Zap,
    Star,
    User,
    Building,
    Calendar,
    Shield,
    Award,
    Crown,
    Sparkles,
    Bot
} from 'lucide-react';

const ImprovedTelegramAnalysisResult = ({ analysisResult, onClose }) => {
    const [animateIn, setAnimateIn] = useState(false);
    const [copiedSection, setCopiedSection] = useState('');
    const [sectionsVisible, setSectionsVisible] = useState({});

    useEffect(() => {
        // Плавное появление основного контейнера
        const timer = setTimeout(() => setAnimateIn(true), 200);
        
        // Постепенное появление секций
        if (animateIn) {
            const sections = parseAnalysisToSections();
            sections.forEach((_, index) => {
                setTimeout(() => {
                    setSectionsVisible(prev => ({
                        ...prev,
                        [index]: true
                    }));
                }, 400 + (index * 150));
            });
        }
        
        return () => clearTimeout(timer);
    }, [animateIn]);

    const copyToClipboard = async (text, section) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedSection(section);
            setTimeout(() => setCopiedSection(''), 2000);
        } catch (err) {
            console.error('Ошибка копирования:', err);
        }
    };

    // Парсинг полного анализа на отдельные секции
    const parseAnalysisToSections = () => {
        const analysis = analysisResult?.analysis;
        if (!analysis) return [];

        const sections = [];
        
        // Получаем полный анализ
        const fullText = analysis.full_analysis || analysis.main_content || '';
        if (!fullText) return [];

        // Разбиваем на секции по заголовкам и ключевым словам
        const lines = fullText.split('\n').filter(line => line.trim());
        let currentSection = null;
        let currentContent = [];

        lines.forEach((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return;

            // Определяем заголовки по ключевым словам и структуре
            const isHeader = (
                // Проверяем на заголовки с двоеточием
                (trimmedLine.includes(':') && trimmedLine.length < 100) ||
                // Ключевые слова для заголовков
                /^(резюме|содержание|отправитель|тип|ключевое|действия|сроки|последствия|срочность|анализ|основное|важно|требуется|необходимо|информация|детали)/i.test(trimmedLine) ||
                // Нумерованные заголовки
                /^\d+\./.test(trimmedLine) ||
                // Заголовки в верхнем регистре
                (trimmedLine === trimmedLine.toUpperCase() && trimmedLine.length > 3 && trimmedLine.length < 50)
            ) && !(/^\d{2,}/.test(trimmedLine)); // Исключаем даты и номера

            if (isHeader || (currentContent.length === 0 && index === 0)) {
                // Сохраняем предыдущую секцию
                if (currentSection && currentContent.length > 0) {
                    sections.push({
                        ...currentSection,
                        content: currentContent.join('\n').trim()
                    });
                }

                // Создаем новую секцию
                const sectionTitle = trimmedLine.replace(/[*#:]/g, '').trim();
                currentSection = {
                    id: `section-${sections.length}`,
                    title: sectionTitle || `Раздел ${sections.length + 1}`,
                    icon: getIconForSection(sectionTitle),
                    color: getColorForSection(sections.length),
                    importance: getImportanceForSection(sectionTitle)
                };
                currentContent = [];
                
                // Если это не первая строка и она содержательная, добавляем ее как контент
                if (index !== 0 && !isHeader) {
                    currentContent.push(trimmedLine);
                }
            } else {
                // Добавляем контент к текущей секции
                currentContent.push(trimmedLine);
            }
        });

        // Добавляем последнюю секцию
        if (currentSection && currentContent.length > 0) {
            sections.push({
                ...currentSection,
                content: currentContent.join('\n').trim()
            });
        }

        // Если секций нет или очень мало, создаем основную секцию
        if (sections.length === 0) {
            sections.push({
                id: 'main-analysis',
                title: 'Анализ документа',
                content: fullText,
                icon: '📋',
                color: 'indigo',
                importance: 'high'
            });
        }

        return sections.filter(section => section.content && section.content.length > 10);
    };

    const getIconForSection = (title) => {
        const titleLower = title.toLowerCase();
        if (titleLower.includes('резюме') || titleLower.includes('содержание')) return '📋';
        if (titleLower.includes('отправитель') || titleLower.includes('sender')) return '👤';
        if (titleLower.includes('тип') || titleLower.includes('type')) return '📄';
        if (titleLower.includes('ключевое') || titleLower.includes('key') || titleLower.includes('важно')) return '🔑';
        if (titleLower.includes('действия') || titleLower.includes('actions') || titleLower.includes('требуется')) return '⚡';
        if (titleLower.includes('сроки') || titleLower.includes('deadlines') || titleLower.includes('дата')) return '⏰';
        if (titleLower.includes('последствия') || titleLower.includes('consequences')) return '⚠️';
        if (titleLower.includes('срочность') || titleLower.includes('urgency')) return '🚨';
        if (titleLower.includes('анализ') || titleLower.includes('детали')) return '🔍';
        if (titleLower.includes('информация') || titleLower.includes('основное')) return '💡';
        if (titleLower.includes('контакт') || titleLower.includes('адрес')) return '📧';
        return '📝';
    };

    const getColorForSection = (index) => {
        const colors = ['blue', 'purple', 'green', 'orange', 'pink', 'teal', 'indigo', 'red'];
        return colors[index % colors.length];
    };

    const getImportanceForSection = (title) => {
        const titleLower = title.toLowerCase();
        if (titleLower.includes('действия') || titleLower.includes('сроки') || titleLower.includes('срочность')) return 'critical';
        if (titleLower.includes('последствия') || titleLower.includes('ключевое') || titleLower.includes('важно')) return 'high';
        return 'medium';
    };

    const getImportanceConfig = (importance) => {
        switch (importance) {
            case 'critical':
                return {
                    badge: 'bg-red-100 text-red-800',
                    icon: <Zap className="h-4 w-4" />,
                    text: 'КРИТИЧНО'
                };
            case 'high':
                return {
                    badge: 'bg-orange-100 text-orange-800',
                    icon: <Star className="h-4 w-4" />,
                    text: 'ВАЖНО'
                };
            default:
                return null;
        }
    };

    const getColorConfig = (color) => {
        const configs = {
            blue: {
                gradient: 'from-blue-500 to-blue-600',
                bg: 'bg-blue-50',
                border: 'border-blue-200',
                text: 'text-blue-900',
                icon: 'text-blue-600'
            },
            purple: {
                gradient: 'from-purple-500 to-purple-600',
                bg: 'bg-purple-50',
                border: 'border-purple-200',
                text: 'text-purple-900',
                icon: 'text-purple-600'
            },
            green: {
                gradient: 'from-green-500 to-green-600',
                bg: 'bg-green-50',
                border: 'border-green-200',
                text: 'text-green-900',
                icon: 'text-green-600'
            },
            orange: {
                gradient: 'from-orange-500 to-orange-600',
                bg: 'bg-orange-50',
                border: 'border-orange-200',
                text: 'text-orange-900',
                icon: 'text-orange-600'
            },
            pink: {
                gradient: 'from-pink-500 to-pink-600',
                bg: 'bg-pink-50',
                border: 'border-pink-200',
                text: 'text-pink-900',
                icon: 'text-pink-600'
            },
            teal: {
                gradient: 'from-teal-500 to-teal-600',
                bg: 'bg-teal-50',
                border: 'border-teal-200',
                text: 'text-teal-900',
                icon: 'text-teal-600'
            },
            indigo: {
                gradient: 'from-indigo-500 to-indigo-600',
                bg: 'bg-indigo-50',
                border: 'border-indigo-200',
                text: 'text-indigo-900',
                icon: 'text-indigo-600'
            },
            red: {
                gradient: 'from-red-500 to-red-600',
                bg: 'bg-red-50',
                border: 'border-red-200',
                text: 'text-red-900',
                icon: 'text-red-600'
            }
        };
        return configs[color] || configs.blue;
    };

    const sections = parseAnalysisToSections();

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className={`bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[95vh] overflow-hidden transform transition-all duration-700 ${
                animateIn ? 'scale-100 opacity-100 translate-y-0' : 'scale-95 opacity-0 translate-y-8'
            }`}>
                
                {/* Красивый заголовок */}
                <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-6 py-8 relative overflow-hidden">
                    {/* Фоновые эффекты */}
                    <div className="absolute inset-0 opacity-20">
                        <div className="absolute top-4 right-4 animate-pulse">
                            <Sparkles className="h-8 w-8 text-white" />
                        </div>
                        <div className="absolute bottom-4 left-4 animate-pulse">
                            <Crown className="h-6 w-6 text-white" />
                        </div>
                        <div className="absolute top-1/2 right-1/3 animate-bounce">
                            <Star className="h-5 w-5 text-white" />
                        </div>
                    </div>
                    
                    <div className="relative flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="p-4 bg-white/20 rounded-2xl backdrop-blur-sm">
                                <FileText className="h-8 w-8 text-white" />
                            </div>
                            <div>
                                <h2 className="text-3xl font-bold text-white mb-1">
                                    Полный анализ
                                </h2>
                                <p className="text-white/90 text-lg">
                                    Детальный разбор документа
                                </p>
                            </div>
                        </div>
                        
                        <button
                            onClick={onClose}
                            className="p-3 hover:bg-white/20 rounded-xl transition-colors backdrop-blur-sm"
                        >
                            <ArrowLeft className="h-6 w-6 text-white" />
                        </button>
                    </div>
                </div>

                {/* Основной контент */}
                <div className="p-6 max-h-[75vh] overflow-y-auto space-y-6 bg-gradient-to-br from-gray-50 to-blue-50">
                    
                    {/* Информация о файле */}
                    <div className={`bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 transform transition-all duration-500 ${
                        animateIn ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
                    }`}>
                        <div className="flex items-center space-x-4">
                            <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                                <FileText className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900 mb-1">
                                    {analysisResult?.file_name || 'Документ'}
                                </h3>
                                <p className="text-gray-600 flex items-center space-x-2">
                                    <Bot className="h-4 w-4" />
                                    <span>Обработано AI</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Секции анализа */}
                    <div className="space-y-6">
                        {sections.map((section, index) => {
                            const colorConfig = getColorConfig(section.color);
                            const importanceConfig = getImportanceConfig(section.importance);
                            
                            return (
                                <div
                                    key={section.id}
                                    className={`bg-white rounded-2xl shadow-lg border-2 ${colorConfig.border} p-6 transform transition-all duration-700 hover:shadow-xl hover:-translate-y-1 ${
                                        sectionsVisible[index] ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
                                    }`}
                                    style={{ transitionDelay: `${index * 150}ms` }}
                                >
                                    {/* Заголовок секции */}
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-4">
                                            <div className={`p-3 bg-gradient-to-r ${colorConfig.gradient} rounded-xl shadow-lg transform hover:scale-110 transition-transform`}>
                                                <span className="text-2xl">{section.icon}</span>
                                            </div>
                                            <div>
                                                <h4 className={`text-xl font-bold ${colorConfig.text} mb-1`}>
                                                    {section.title}
                                                </h4>
                                                {importanceConfig && (
                                                    <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-bold ${importanceConfig.badge}`}>
                                                        {importanceConfig.icon}
                                                        <span>{importanceConfig.text}</span>
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        
                                        <button
                                            onClick={() => copyToClipboard(section.content, section.id)}
                                            className={`p-3 bg-gradient-to-r ${colorConfig.gradient} hover:shadow-lg rounded-xl transition-all transform hover:scale-110 group`}
                                        >
                                            <Copy className="h-5 w-5 text-white" />
                                        </button>
                                    </div>
                                    
                                    {/* Контент секции */}
                                    <div className={`${colorConfig.bg} rounded-xl p-5 ${colorConfig.border} border`}>
                                        <div className={`${colorConfig.text} leading-relaxed text-base whitespace-pre-wrap`}>
                                            {section.content}
                                        </div>
                                    </div>
                                    
                                    {/* Индикатор копирования */}
                                    {copiedSection === section.id && (
                                        <div className="absolute top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-full text-sm font-bold animate-bounce shadow-lg">
                                            ✅ Скопировано!
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* Нижняя панель */}
                    <div className={`bg-gradient-to-r from-indigo-100 to-purple-100 rounded-2xl p-6 border-2 border-indigo-200 transform transition-all duration-700 ${
                        animateIn ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
                    }`} style={{ transitionDelay: `${sections.length * 150 + 300}ms` }}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl">
                                    <Award className="h-6 w-6 text-white" />
                                </div>
                                <div>
                                    <p className="font-bold text-gray-900">Анализ завершен</p>
                                    <p className="text-gray-600 text-sm">Результат готов к использованию</p>
                                </div>
                            </div>
                            
                            <button
                                onClick={onClose}
                                className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl transition-all transform hover:scale-105 shadow-lg font-bold"
                            >
                                Готово
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImprovedTelegramAnalysisResult;