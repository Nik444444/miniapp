import React, { useEffect } from 'react';
import { 
    ArrowLeft,
    Clock,
    Sparkles,
    Star,
    Heart,
    Zap,
    Rocket,
    Crown,
    Gift,
    Bell,
    Calendar,
    CheckCircle
} from 'lucide-react';
import { 
    GlassCard, 
    GradientText,
    FloatingElement,
    MagneticElement,
    FloatingParticles 
} from './UIEffects';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback 
} from '../utils/telegramWebApp';

const TelegramComingSoon = ({ onBack, toolInfo }) => {
    // Telegram WebApp настройки
    useEffect(() => {
        if (isTelegramWebApp()) {
            const tg = getTelegramWebApp();
            if (tg) {
                tg.ready();
                tg.expand();
                tg.setHeaderColor('#0f0f23');
                tg.setBackgroundColor('#0f0f23');
            }
        }
    }, []);

    const handleBack = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        onBack();
    };

    const features = {
        'letter-composer': [
            'Генерация официальных писем',
            'Шаблоны для разных ситуаций',
            'Персонализация контента',
            'Проверка грамматики'
        ],
        'housing-search': [
            'Поиск квартир и домов',
            'Фильтры по цене и району',
            'Интеграция с популярными сайтами',
            'Уведомления о новых предложениях'
        ],
        'job-search': [
            'Поиск вакансий',
            'AI-анализ резюме',
            'Подбор подходящих позиций',
            'Подготовка к собеседованию'
        ],
        'marketplace': [
            'Покупка и продажа товаров',
            'Безопасные сделки',
            'Система рейтингов',
            'Интеграция с доставкой'
        ]
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
            {/* Animated Background */}
            <div className={`absolute inset-0 bg-gradient-to-br ${toolInfo.bgGradient}`}></div>
            
            {/* Floating Particles */}
            <FloatingParticles />
            
            {/* Animated Gradient Orbs */}
            <div className={`absolute top-20 left-20 w-72 h-72 bg-gradient-to-br ${toolInfo.gradient} opacity-30 rounded-full blur-3xl animate-pulse`}></div>
            <div className={`absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br ${toolInfo.gradient} opacity-20 rounded-full blur-3xl animate-pulse delay-1000`}></div>
            
            {/* Header */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={handleBack}
                        className="flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl px-4 py-2 hover:bg-white/20 transition-all duration-200"
                    >
                        <ArrowLeft className="w-5 h-5 text-white" />
                        <span className="text-white">Назад</span>
                    </button>
                    
                    <div className="text-center">
                        <h1 className="text-2xl font-bold">
                            <GradientText className={`bg-gradient-to-r ${toolInfo.gradient}`}>
                                {toolInfo.title}
                            </GradientText>
                        </h1>
                        <p className="text-sm text-gray-300">{toolInfo.subtitle}</p>
                    </div>
                    
                    <div className="w-16 flex justify-center">
                        <div className="relative">
                            <div className={`w-8 h-8 bg-gradient-to-r ${toolInfo.gradient} rounded-full flex items-center justify-center`}>
                                <toolInfo.icon className="w-4 h-4 text-white" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full flex items-center justify-center animate-bounce">
                                <Star className="w-2 h-2 text-white" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 px-4 pb-8">
                <div className="max-w-2xl mx-auto space-y-6">
                    {/* Coming Soon Banner */}
                    <FloatingElement delay={0}>
                        <GlassCard className="p-8 bg-white/10 backdrop-blur-xl border border-white/20 text-center">
                            <div className="relative">
                                <div className="w-24 h-24 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                                    <Clock className="w-12 h-12 text-white" />
                                </div>
                                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center animate-bounce">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                            </div>
                            
                            <h2 className="text-3xl font-bold mb-4">
                                <GradientText className="bg-gradient-to-r from-yellow-400 via-orange-400 to-red-400">
                                    Скоро доступно!
                                </GradientText>
                            </h2>
                            <p className="text-gray-300 text-lg mb-6">
                                Мы работаем над этим инструментом
                            </p>
                            
                            <div className="flex items-center justify-center space-x-4 mb-6">
                                <div className="flex items-center space-x-2">
                                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                                    <span className="text-sm text-gray-300">В разработке</span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse delay-500"></div>
                                    <span className="text-sm text-gray-300">Тестирование</span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse delay-1000"></div>
                                    <span className="text-sm text-gray-300">Скоро запуск</span>
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Features Preview */}
                    <FloatingElement delay={200}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className={`p-3 bg-gradient-to-r ${toolInfo.gradient} rounded-xl`}>
                                    <Gift className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-white">Что вас ждет</h3>
                                    <p className="text-sm text-gray-300">Возможности нового инструмента</p>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                {features[toolInfo.id]?.map((feature, index) => (
                                    <div key={index} className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                                            <CheckCircle className="w-4 h-4 text-white" />
                                        </div>
                                        <p className="text-white font-medium">{feature}</p>
                                    </div>
                                ))}
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Notification Signup */}
                    <FloatingElement delay={400}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-4">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                    <Bell className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Будьте первыми</h3>
                                    <p className="text-sm text-gray-300">Получите уведомление о запуске</p>
                                </div>
                            </div>
                            
                            <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 rounded-xl p-4">
                                <div className="flex items-center space-x-3 mb-3">
                                    <Rocket className="w-5 h-5 text-purple-300" />
                                    <p className="text-purple-200 font-medium">Автоматическое уведомление</p>
                                </div>
                                <p className="text-purple-100 text-sm">
                                    Как только инструмент будет готов, вы получите уведомление прямо в Telegram!
                                </p>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Progress Timeline */}
                    <FloatingElement delay={600}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="p-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl">
                                    <Calendar className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Прогресс разработки</h3>
                                    <p className="text-sm text-gray-300">Текущий статус</p>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="flex items-center space-x-4">
                                    <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                                    <div className="flex-1">
                                        <p className="text-white font-medium">Планирование</p>
                                        <p className="text-gray-300 text-sm">Завершено</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center space-x-4">
                                    <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                                    <div className="flex-1">
                                        <p className="text-white font-medium">Разработка</p>
                                        <p className="text-gray-300 text-sm">В процессе</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center space-x-4">
                                    <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
                                    <div className="flex-1">
                                        <p className="text-white font-medium">Тестирование</p>
                                        <p className="text-gray-300 text-sm">Ожидает</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center space-x-4">
                                    <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
                                    <div className="flex-1">
                                        <p className="text-white font-medium">Запуск</p>
                                        <p className="text-gray-300 text-sm">Скоро</p>
                                    </div>
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Back to Menu */}
                    <FloatingElement delay={800}>
                        <div className="text-center">
                            <button
                                onClick={handleBack}
                                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white py-3 px-6 rounded-xl transition-all duration-200 flex items-center space-x-2 mx-auto transform hover:scale-105 shadow-lg"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                <span>Вернуться в меню</span>
                            </button>
                        </div>
                    </FloatingElement>
                </div>
            </div>
        </div>
    );
};

export default TelegramComingSoon;