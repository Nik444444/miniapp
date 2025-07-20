import React, { useContext, useEffect, useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { AuthContext } from '../context/AuthContext';
import { 
    FileText, 
    Mail, 
    Globe, 
    Sparkles, 
    CheckCircle, 
    Clock, 
    Users,
    Brain,
    Zap,
    Shield,
    Star,
    ArrowRight,
    Play,
    Palette,
    Crown,
    Wand2,
    Rocket,
    Heart,
    MessageSquare,
    Languages,
    History,
    Key
} from 'lucide-react';

// Анимированный фон с документами
const AnimatedBackground = () => {
    const documents = [
        { icon: FileText, delay: 0, duration: 15, x: 10, y: 20 },
        { icon: Mail, delay: 2, duration: 20, x: 80, y: 10 },
        { icon: Globe, delay: 4, duration: 18, x: 60, y: 70 },
        { icon: MessageSquare, delay: 6, duration: 16, x: 20, y: 80 },
        { icon: Brain, delay: 8, duration: 22, x: 90, y: 50 },
        { icon: Languages, delay: 10, duration: 19, x: 40, y: 30 },
        { icon: History, delay: 12, duration: 17, x: 15, y: 60 },
        { icon: Key, delay: 14, duration: 21, x: 75, y: 25 },
    ];

    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {/* Градиентный фон */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 opacity-80"></div>
            
            {/* Анимированные световые круги */}
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
            <div className="absolute bottom-1/4 left-1/3 w-48 h-48 bg-pink-500/20 rounded-full blur-3xl animate-pulse delay-2000"></div>
            
            {/* Летающие документы */}
            {documents.map((doc, index) => (
                <div
                    key={index}
                    className="absolute animate-float"
                    style={{
                        left: `${doc.x}%`,
                        top: `${doc.y}%`,
                        animationDelay: `${doc.delay}s`,
                        animationDuration: `${doc.duration}s`,
                    }}
                >
                    <div className="transform rotate-12 hover:rotate-0 transition-transform duration-1000">
                        <doc.icon className="w-8 h-8 text-white/20 hover:text-white/40 transition-colors" />
                    </div>
                </div>
            ))}
            
            {/* Плавающие частицы */}
            <div className="absolute inset-0">
                {[...Array(30)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute w-1 h-1 bg-white/30 rounded-full animate-twinkle"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 3}s`,
                            animationDuration: `${2 + Math.random() * 2}s`,
                        }}
                    />
                ))}
            </div>
        </div>
    );
};

// Основной компонент авторизации
const Auth = () => {
    const { loginWithGoogle } = useContext(AuthContext);
    const [isLoading, setIsLoading] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handleGoogleSuccess = async (credentialResponse) => {
        setIsLoading(true);
        const result = await loginWithGoogle(credentialResponse.credential);
        if (!result.success) {
            alert(result.error);
        }
        setIsLoading(false);
    };

    const handleGoogleError = () => {
        alert('Ошибка авторизации Google');
    };

    const features = [
        {
            icon: FileText,
            title: 'Анализ PDF документов',
            description: 'Мгновенный анализ любых PDF файлов',
            color: 'from-blue-500 to-cyan-500'
        },
        {
            icon: Mail,
            title: 'Анализ изображений писем',
            description: 'Распознавание текста с фотографий',
            color: 'from-purple-500 to-pink-500'
        },
        {
            icon: Globe,
            title: 'Поддержка нескольких языков',
            description: 'Русский, English, Deutsch',
            color: 'from-green-500 to-teal-500'
        },
        {
            icon: Brain,
            title: 'AI провайдеры',
            description: 'Интеграция с современными AI моделями',
            color: 'from-orange-500 to-red-500'
        },
        {
            icon: History,
            title: 'История анализов',
            description: 'Сохранение всех ваших анализов',
            color: 'from-indigo-500 to-purple-500'
        },
        {
            icon: Shield,
            title: 'Безопасность',
            description: 'Надежная защита ваших данных',
            color: 'from-emerald-500 to-green-500'
        }
    ];

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Анимированный фон */}
            <AnimatedBackground />
            
            {/* Основной контент */}
            <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
                <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    
                    {/* Левая часть - информация */}
                    <div className={`space-y-8 text-white transition-all duration-1000 ${mounted ? 'translate-x-0 opacity-100' : '-translate-x-20 opacity-0'}`}>
                        <div className="space-y-6">
                            <div className="flex items-center space-x-4">
                                <div className="relative">
                                    <div className="w-20 h-20 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-3xl flex items-center justify-center shadow-2xl">
                                        <Crown className="w-10 h-10 text-white" />
                                    </div>
                                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                                        <Sparkles className="w-4 h-4 text-yellow-900" />
                                    </div>
                                </div>
                                <div>
                                    <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
                                        German Letter AI
                                    </h1>
                                    <p className="text-xl text-blue-100 flex items-center space-x-2">
                                        <Wand2 className="w-5 h-5" />
                                        <span>Революционный анализ писем</span>
                                        <Rocket className="w-5 h-5" />
                                    </p>
                                </div>
                            </div>
                            
                            <p className="text-xl text-gray-200 leading-relaxed">
                                Анализируйте немецкие официальные письма с помощью 
                                <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent font-bold"> искусственного интеллекта</span>
                            </p>
                        </div>

                        {/* Характеристики */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {features.slice(0, 4).map((feature, index) => (
                                <div
                                    key={index}
                                    className={`p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300 transform hover:scale-105 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}
                                    style={{ transitionDelay: `${index * 100}ms` }}
                                >
                                    <div className="flex items-center space-x-3">
                                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center`}>
                                            <feature.icon className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-white">{feature.title}</h3>
                                            <p className="text-sm text-gray-300">{feature.description}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Правая часть - форма авторизации */}
                    <div className={`transition-all duration-1000 delay-300 ${mounted ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0'}`}>
                        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
                            <div className="text-center mb-8">
                                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                    <Play className="w-8 h-8 text-white" />
                                </div>
                                <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
                                    Добро пожаловать
                                </h2>
                                <p className="text-gray-600">
                                    Войдите в аккаунт для начала работы
                                </p>
                            </div>

                            <div className="space-y-6">
                                <div className="text-center">
                                    <div className="relative inline-block">
                                        <GoogleLogin
                                            onSuccess={handleGoogleSuccess}
                                            onError={handleGoogleError}
                                            size="large"
                                            theme="outline"
                                            shape="rectangular"
                                            width="320"
                                            text="signin_with"
                                            locale="ru"
                                        />
                                        {isLoading && (
                                            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                                                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="text-center">
                                    <p className="text-sm text-gray-500 flex items-center justify-center space-x-2">
                                        <Shield className="w-4 h-4" />
                                        <span>Безопасная авторизация через Google</span>
                                    </p>
                                </div>
                            </div>

                            {/* Дополнительные возможности */}
                            <div className="mt-8 pt-6 border-t border-gray-200">
                                <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                    <Star className="w-5 h-5 text-yellow-500 mr-2" />
                                    Возможности сервиса
                                </h4>
                                <div className="space-y-3">
                                    {features.slice(4).map((feature, index) => (
                                        <div key={index} className="flex items-center space-x-3">
                                            <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center`}>
                                                <feature.icon className="w-4 h-4 text-white" />
                                            </div>
                                            <div>
                                                <span className="text-sm font-medium text-gray-900">{feature.title}</span>
                                                <p className="text-xs text-gray-500">{feature.description}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Auth;