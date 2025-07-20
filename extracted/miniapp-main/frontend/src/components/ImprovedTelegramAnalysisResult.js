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
        <div className="fixed inset-0 bg-slate-900 z-50 overflow-hidden">
            <div className="h-full flex flex-col">
                
                {/* Заголовок во весь экран */}
                <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 px-4 py-4 flex-shrink-0">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                                <FileText className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white">Результат анализа</h2>
                                <p className="text-white/90 text-sm">AI обработка завершена</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/20 rounded-xl transition-colors"
                        >
                            <ArrowLeft className="h-5 w-5 text-white" />
                        </button>
                    </div>
                </div>

                {/* Основной контент во весь экран */}
                <div className="flex-1 overflow-y-auto bg-gray-50 p-4 space-y-4">
                    
                    {/* Информация о файле */}
                    <div className="bg-white rounded-xl shadow-lg border p-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg">
                                <FileText className="h-5 w-5 text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">
                                    {analysisResult?.file_name || 'Документ'}
                                </h3>
                                <p className="text-gray-600 text-sm flex items-center space-x-1">
                                    <Bot className="h-4 w-4" />
                                    <span>Обработано AI</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Секции анализа с исправленным выравниванием текста */}
                    <div className="space-y-4">
                        {sections.map((section, index) => {
                            const colorConfig = getColorConfig(section.color);
                            const importanceConfig = getImportanceConfig(section.importance);
                            
                            return (
                                <div
                                    key={section.id}
                                    className={`bg-white rounded-xl shadow-lg border-2 ${colorConfig.border} p-4`}
                                >
                                    {/* Заголовок секции */}
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-3 flex-1">
                                            <div className={`p-2 bg-gradient-to-r ${colorConfig.gradient} rounded-lg flex-shrink-0`}>
                                                <span className="text-lg">{section.icon}</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className={`text-lg font-bold ${colorConfig.text} mb-1`}>
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
                                            className={`p-2 bg-gradient-to-r ${colorConfig.gradient} hover:shadow-lg rounded-lg transition-all flex-shrink-0 ml-2`}
                                        >
                                            <Copy className="h-4 w-4 text-white" />
                                        </button>
                                    </div>
                                    
                                    {/* Контент секции с правильным выравниванием */}
                                    <div className={`${colorConfig.bg} rounded-lg p-4 ${colorConfig.border} border`}>
                                        <div className={`${colorConfig.text} leading-relaxed text-base`}>
                                            {section.content.split('\n').map((line, lineIndex) => (
                                                line.trim() && (
                                                    <p key={lineIndex} className="mb-2 text-left">
                                                        {line.trim()}
                                                    </p>
                                                )
                                            ))}
                                        </div>
                                    </div>
                                    
                                    {/* Индикатор копирования */}
                                    {copiedSection === section.id && (
                                        <div className="absolute top-2 right-2 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                                            ✅ Скопировано
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* Нижняя панель */}
                    <div className="bg-gradient-to-r from-indigo-100 to-purple-100 rounded-xl p-4 border-2 border-indigo-200">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg">
                                    <Award className="h-5 w-5 text-white" />
                                </div>
                                <div>
                                    <p className="font-bold text-gray-900">Анализ завершен</p>
                                    <p className="text-gray-600 text-sm">Результат готов к использованию</p>
                                </div>
                            </div>
                            
                            <button
                                onClick={onClose}
                                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-lg transition-all font-bold"
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