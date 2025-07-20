import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    FileText, 
    Edit, 
    Home, 
    Briefcase, 
    ShoppingCart,
    Key,
    User,
    LogOut,
    Sparkles,
    Zap,
    Star,
    Crown,
    Wand2,
    Rocket,
    Settings,
    CheckCircle,
    AlertCircle,
    Menu,
    X,
    Plus,
    ArrowRight,
    ChevronRight,
    Layers,
    Globe,
    Shield,
    Heart,
    Lightbulb,
    Target,
    Inbox,
    PenTool,
    MapPin,
    Users,
    Package
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
    hapticFeedback, 
    showTelegramAlert 
} from '../utils/telegramWebApp';

const TelegramMainMenu = ({ onNavigate, onApiKeySetup, onLanguageSelection }) => {
    const { user, logout } = useContext(AuthContext);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [loadingTool, setLoadingTool] = useState(null);
    const [selectedTool, setSelectedTool] = useState(null);

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

    const handleToolClick = async (toolId, toolName) => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        
        setSelectedTool(toolId);
        setLoadingTool(toolId);
        
        // Небольшая задержка для анимации
        await new Promise(resolve => setTimeout(resolve, 800));
        
        if (toolId === 'api-key') {
            onApiKeySetup();
        } else if (toolId === 'language') {
            onLanguageSelection();
        } else {
            onNavigate(toolId);
        }
        
        setLoadingTool(null);
        setSelectedTool(null);
    };

    const handleLogout = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('warning');
        }
        logout();
    };

    const menuItems = [
        {
            id: 'language',
            title: 'Выбор языка',
            subtitle: 'Настройка языка анализа',
            icon: Globe,
            gradient: 'from-indigo-500 via-purple-500 to-blue-500',
            hoverGradient: 'from-indigo-600 via-purple-600 to-blue-600',
            bgGradient: 'from-indigo-500/20 to-blue-500/20',
            status: 'active',
            priority: 'high',
            description: `Текущий: ${user?.preferred_language ? 
                (user.preferred_language === 'uk' ? 'Українська' : 
                 user.preferred_language === 'ru' ? 'Русский' : 
                 user.preferred_language === 'de' ? 'Deutsch' : 'English') : 'Русский'}`
        },
        {
            id: 'api-key',
            title: 'API Ключ',
            subtitle: 'Настройка доступа к AI',
            icon: Key,
            gradient: 'from-emerald-500 via-green-500 to-teal-500',
            hoverGradient: 'from-emerald-600 via-green-600 to-teal-600',
            bgGradient: 'from-emerald-500/20 to-teal-500/20',
            status: user?.has_gemini_api_key ? 'active' : 'setup',
            priority: 'primary',
            description: 'Главный ключ для всей экосистемы'
        },
        {
            id: 'document-analysis',
            title: 'Анализ писем',
            subtitle: 'AI анализ документов',
            icon: FileText,
            gradient: 'from-blue-500 via-purple-500 to-indigo-500',
            hoverGradient: 'from-blue-600 via-purple-600 to-indigo-600',
            bgGradient: 'from-blue-500/20 to-purple-500/20',
            status: user?.has_gemini_api_key ? 'active' : 'locked',
            priority: 'high',
            description: 'Анализ и извлечение информации'
        },
        {
            id: 'letter-composer',
            title: 'Составление писем',
            subtitle: 'Генерация официальных писем',
            icon: Edit,
            gradient: 'from-orange-500 via-red-500 to-pink-500',
            hoverGradient: 'from-orange-600 via-red-600 to-pink-600',
            bgGradient: 'from-orange-500/20 to-pink-500/20',
            status: 'coming-soon',
            priority: 'medium',
            description: 'Скоро доступно'
        },
        {
            id: 'housing-search',
            title: 'Поиск жилья',
            subtitle: 'Поиск квартир и домов',
            icon: Home,
            gradient: 'from-cyan-500 via-blue-500 to-purple-500',
            hoverGradient: 'from-cyan-600 via-blue-600 to-purple-600',
            bgGradient: 'from-cyan-500/20 to-purple-500/20',
            status: 'coming-soon',
            priority: 'medium',
            description: 'Скоро доступно'
        },
        {
            id: 'job-search',
            title: 'Поиск работы',
            subtitle: 'Поиск вакансий',
            icon: Briefcase,
            gradient: 'from-violet-500 via-purple-500 to-fuchsia-500',
            hoverGradient: 'from-violet-600 via-purple-600 to-fuchsia-600',
            bgGradient: 'from-violet-500/20 to-fuchsia-500/20',
            status: 'coming-soon',
            priority: 'medium',
            description: 'Скоро доступно'
        },
        {
            id: 'marketplace',
            title: 'Маркетплейс',
            subtitle: 'Покупка и продажа',
            icon: ShoppingCart,
            gradient: 'from-yellow-500 via-orange-500 to-red-500',
            hoverGradient: 'from-yellow-600 via-orange-600 to-red-600',
            bgGradient: 'from-yellow-500/20 to-red-500/20',
            status: 'coming-soon',
            priority: 'medium',
            description: 'Скоро доступно'
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/30 to-pink-900/20"></div>
            
            {/* Floating Particles */}
            <FloatingParticles />
            
            {/* Animated Gradient Orbs */}
            <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 rounded-full blur-3xl animate-pulse delay-2000"></div>
            
            {/* Header */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="relative">
                            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-white animate-pulse" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center animate-bounce">
                                <Zap className="w-3 h-3 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">
                                <GradientText className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                                    AI Assistant
                                </GradientText>
                            </h1>
                            <p className="text-sm text-gray-300">Выберите инструмент</p>
                        </div>
                    </div>
                    
                    <div className="relative">
                        <button
                            onClick={() => {
                                setShowUserMenu(!showUserMenu);
                                if (isTelegramWebApp()) {
                                    hapticFeedback('light');
                                }
                            }}
                            className="w-10 h-10 bg-gradient-to-r from-gray-600 to-gray-700 rounded-full flex items-center justify-center hover:from-gray-500 hover:to-gray-600 transition-all duration-200 transform hover:scale-110"
                        >
                            <User className="w-5 h-5 text-white" />
                        </button>
                        
                        {showUserMenu && (
                            <div className="absolute right-0 top-12 w-48 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl shadow-xl py-2 z-20">
                                <div className="px-4 py-2 border-b border-white/10">
                                    <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                                    <p className="text-xs text-gray-300 truncate">{user?.email}</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full px-4 py-2 text-left text-red-300 hover:bg-red-500/20 transition-colors flex items-center space-x-2"
                                >
                                    <LogOut className="w-4 h-4" />
                                    <span>Выйти</span>
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 px-4 pb-8">
                {/* Welcome Message */}
                <div className="mb-8 text-center">
                    <FloatingElement delay={0}>
                        <div className="relative">
                            <h2 className="text-4xl font-bold mb-2">
                                <GradientText className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                                    Добро пожаловать!
                                </GradientText>
                            </h2>
                            <p className="text-gray-300 text-lg">
                                Выберите инструмент для работы с AI
                            </p>
                            <div className="absolute -top-4 -right-4 text-2xl animate-bounce">🚀</div>
                        </div>
                    </FloatingElement>
                </div>

                {/* Tools Grid */}
                <div className="grid grid-cols-1 gap-4 max-w-2xl mx-auto">
                    {menuItems.map((item, index) => (
                        <FloatingElement key={item.id} delay={index * 100}>
                            <MagneticElement>
                                <GlassCard
                                    className={`relative overflow-hidden transition-all duration-500 transform hover:scale-105 cursor-pointer ${
                                        selectedTool === item.id ? 'scale-105 shadow-2xl' : ''
                                    } ${
                                        item.priority === 'primary' ? 'border-2 border-emerald-400/50 shadow-emerald-500/25' : 
                                        item.priority === 'high' ? 'border border-blue-400/30' : 
                                        'border border-white/20'
                                    }`}
                                    onClick={() => handleToolClick(item.id, item.title)}
                                >
                                    {/* Background Gradient */}
                                    <div className={`absolute inset-0 bg-gradient-to-br ${item.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
                                    
                                    {/* Loading Overlay */}
                                    {loadingTool === item.id && (
                                        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-10">
                                            <div className="text-center">
                                                <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-2"></div>
                                                <p className="text-white text-sm">Загрузка...</p>
                                            </div>
                                        </div>
                                    )}
                                    
                                    {/* Priority Badge */}
                                    {item.priority === 'primary' && (
                                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full flex items-center justify-center animate-bounce">
                                            <Crown className="w-3 h-3 text-white" />
                                        </div>
                                    )}
                                    
                                    <div className="relative z-10 p-6 group">
                                        <div className="flex items-center space-x-4">
                                            <div className={`w-16 h-16 bg-gradient-to-r ${item.gradient} rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-all duration-300 shadow-lg`}>
                                                <item.icon className="w-8 h-8 text-white" />
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h3 className="text-xl font-bold text-white group-hover:text-blue-200 transition-colors">
                                                        {item.title}
                                                    </h3>
                                                    {item.status === 'active' && (
                                                        <CheckCircle className="w-5 h-5 text-green-400" />
                                                    )}
                                                    {item.status === 'locked' && (
                                                        <AlertCircle className="w-5 h-5 text-yellow-400" />
                                                    )}
                                                </div>
                                                <p className="text-gray-300 text-sm mb-2">{item.subtitle}</p>
                                                <p className="text-gray-400 text-xs">{item.description}</p>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                {item.status === 'coming-soon' && (
                                                    <div className="px-3 py-1 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-400/30 rounded-full">
                                                        <span className="text-xs text-yellow-300 font-medium">Скоро</span>
                                                    </div>
                                                )}
                                                <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
                                            </div>
                                        </div>
                                    </div>
                                </GlassCard>
                            </MagneticElement>
                        </FloatingElement>
                    ))}
                </div>

                {/* Status Info */}
                <div className="mt-8 text-center">
                    <FloatingElement delay={600}>
                        <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full px-4 py-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-sm text-gray-300">
                                {user?.has_gemini_api_key ? 'Система готова к работе' : 'Необходимо настроить API ключ'}
                            </span>
                        </div>
                    </FloatingElement>
                </div>
            </div>
        </div>
    );
};

export default TelegramMainMenu;