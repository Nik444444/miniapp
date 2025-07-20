import React, { useState, useEffect } from 'react';
import { 
    Globe, 
    ChevronRight, 
    Star, 
    Sparkles, 
    Heart,
    Check,
    ArrowRight
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const LanguageSelector = ({ onLanguageSelect }) => {
    const { t, currentLanguage } = useLanguage();
    const [selectedLanguage, setSelectedLanguage] = useState(null);
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [animateIn, setAnimateIn] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setAnimateIn(true), 200);
        return () => clearTimeout(timer);
    }, []);

    const languages = [
        {
            code: 'uk',
            name: 'Українська',
            englishName: 'Ukrainian',
            flag: '🇺🇦',
            gradient: 'from-blue-400 via-yellow-400 to-blue-600',
            bgGradient: 'from-blue-500/20 via-yellow-500/20 to-blue-600/20',
            description: 'Українська мова для аналізу документів',
            welcomeText: 'Ласкаво просимо до Bürokrator AI!'
        },
        {
            code: 'ru',
            name: 'Русский',
            englishName: 'Russian',
            flag: '🇷🇺',
            gradient: 'from-red-400 via-blue-400 to-red-600',
            bgGradient: 'from-red-500/20 via-blue-500/20 to-red-600/20',
            description: 'Русский язык для анализа документов',
            welcomeText: 'Добро пожаловать в Bürokrator AI!'
        },
        {
            code: 'de',
            name: 'Deutsch',
            englishName: 'German',
            flag: '🇩🇪',
            gradient: 'from-red-400 via-yellow-400 to-black',
            bgGradient: 'from-red-500/20 via-yellow-500/20 to-gray-800/20',
            description: 'Deutsche Sprache für Dokumentenanalyse',
            welcomeText: 'Willkommen bei Bürokrator AI!'
        }
    ];

    const handleLanguageSelect = (language) => {
        setSelectedLanguage(language);
        setShowConfirmation(true);
        
        // Автоматически подтверждаем через 2 секунды
        setTimeout(() => {
            confirmLanguage(language);
        }, 2000);
    };

    const confirmLanguage = (language) => {
        // Сохраняем выбор языка в localStorage
        localStorage.setItem('selectedLanguage', language.code);
        localStorage.setItem('languageSelected', 'true');
        
        // Передаем выбранный язык родительскому компоненту
        onLanguageSelect(language.code);
    };

    if (showConfirmation && selectedLanguage) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center relative overflow-hidden">
                {/* Animated Background */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/30 to-pink-900/20"></div>
                
                {/* Floating Particles */}
                <div className="absolute inset-0">
                    {[...Array(20)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute animate-pulse"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 2}s`,
                                animationDuration: `${2 + Math.random() * 2}s`
                            }}
                        >
                            <div className="w-2 h-2 bg-white/30 rounded-full"></div>
                        </div>
                    ))}
                </div>

                {/* Confirmation Card */}
                <div className="relative z-10 bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 max-w-md w-full mx-4 text-center animate-scale-in">
                    <div className="mb-6">
                        <div className={`w-24 h-24 bg-gradient-to-br ${selectedLanguage.bgGradient} rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce`}>
                            <span className="text-4xl">{selectedLanguage.flag}</span>
                        </div>
                        <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Check className="w-8 h-8 text-green-400" />
                        </div>
                    </div>
                    
                    <h2 className="text-2xl font-bold text-white mb-2">
                        {selectedLanguage.welcomeText}
                    </h2>
                    
                    <p className="text-gray-300 mb-6">
                        {selectedLanguage.name} выбран как основной язык
                    </p>
                    
                    <div className="space-y-3">
                        <div className="flex items-center justify-center space-x-2 text-green-400">
                            <Check className="w-5 h-5" />
                            <span className="text-sm">Анализ документов</span>
                        </div>
                        <div className="flex items-center justify-center space-x-2 text-green-400">
                            <Check className="w-5 h-5" />
                            <span className="text-sm">Интерфейс приложения</span>
                        </div>
                        <div className="flex items-center justify-center space-x-2 text-green-400">
                            <Check className="w-5 h-5" />
                            <span className="text-sm">AI-помощник</span>
                        </div>
                    </div>
                    
                    <div className="mt-6 flex items-center justify-center space-x-2 text-gray-400">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span className="text-sm">Загрузка...</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center relative overflow-hidden">
            {/* Animated Background Effects */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/30 to-pink-900/20"></div>
            
            {/* Floating Elements */}
            <div className="absolute inset-0">
                {[...Array(30)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute animate-float"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 3}s`,
                            animationDuration: `${3 + Math.random() * 2}s`
                        }}
                    >
                        {Math.random() > 0.5 ? (
                            <Sparkles className="w-4 h-4 text-white/20" />
                        ) : (
                            <Star className="w-3 h-3 text-white/30" />
                        )}
                    </div>
                ))}
            </div>

            {/* Rotating Gradient Orbs */}
            <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-20 right-20 w-80 h-80 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>

            {/* Main Content */}
            <div className={`relative z-10 max-w-4xl w-full mx-4 transform transition-all duration-1000 ${
                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
            }`}>
                
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="flex items-center justify-center mb-6">
                        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center animate-pulse">
                            <Globe className="w-10 h-10 text-white" />
                        </div>
                    </div>
                    
                    <h1 className="text-5xl font-bold text-white mb-4">
                        <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                            Bürokrator AI
                        </span>
                    </h1>
                    
                    <p className="text-xl text-gray-300 mb-2">
                        {t('chooseYourLanguage')}
                    </p>
                    
                    <p className="text-gray-400">
                        {t('languageSelectionDescription')}
                    </p>
                </div>

                {/* Language Options */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {languages.map((language, index) => (
                        <div
                            key={language.code}
                            className={`group relative cursor-pointer transform transition-all duration-500 hover:scale-105 ${
                                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
                            }`}
                            style={{ transitionDelay: `${index * 200}ms` }}
                            onClick={() => handleLanguageSelect(language)}
                        >
                            {/* Language Card */}
                            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 relative overflow-hidden">
                                
                                {/* Background Gradient */}
                                <div className={`absolute inset-0 bg-gradient-to-br ${language.bgGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>
                                
                                {/* Content */}
                                <div className="relative z-10">
                                    <div className="text-center mb-4">
                                        <div className="text-6xl mb-3 transform group-hover:scale-110 transition-transform duration-300">
                                            {language.flag}
                                        </div>
                                        <h3 className="text-2xl font-bold text-white mb-1">
                                            {language.name}
                                        </h3>
                                        <p className="text-gray-400 text-sm">
                                            {language.englishName}
                                        </p>
                                    </div>
                                    
                                    <p className="text-gray-300 text-sm text-center mb-4">
                                        {language.description}
                                    </p>
                                    
                                    <div className="flex items-center justify-center space-x-2 text-white/80 group-hover:text-white transition-colors">
                                        <span className="text-sm font-medium">Select</span>
                                        <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform duration-300" />
                                    </div>
                                </div>
                                
                                {/* Hover Effects */}
                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    <Heart className="w-5 h-5 text-pink-400 animate-pulse" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer */}
                <div className={`text-center transform transition-all duration-700 ${
                    animateIn ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
                }`} style={{ transitionDelay: '800ms' }}>
                    <p className="text-gray-400 text-sm">
                        🤖 AI-powered document analysis in your language
                    </p>
                </div>
            </div>

            {/* CSS Animations */}
            <style jsx>{`
                @keyframes float {
                    0%, 100% { transform: translateY(0px) rotate(0deg); }
                    50% { transform: translateY(-20px) rotate(180deg); }
                }
                
                @keyframes scale-in {
                    0% { transform: scale(0.8) translateY(20px); opacity: 0; }
                    100% { transform: scale(1) translateY(0px); opacity: 1; }
                }
                
                .animate-float {
                    animation: float 4s ease-in-out infinite;
                }
                
                .animate-scale-in {
                    animation: scale-in 0.5s ease-out;
                }
            `}</style>
        </div>
    );
};

export default LanguageSelector;