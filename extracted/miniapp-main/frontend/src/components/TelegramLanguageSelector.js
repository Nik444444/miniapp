import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Globe, 
    ChevronRight, 
    Star, 
    Sparkles, 
    Heart,
    Check,
    ArrowRight,
    ArrowLeft
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback 
} from '../utils/telegramWebApp';

const TelegramLanguageSelector = ({ onBack }) => {
    const { user, updateUserLanguage } = useContext(AuthContext);
    const [selectedLanguage, setSelectedLanguage] = useState(user?.preferred_language || 'ru');
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [animateIn, setAnimateIn] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

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
            bgGradient: 'from-red-500/20 via-yellow-500/20 to-black/20',
            description: 'Deutsche Sprache für Dokumentenanalyse',
            welcomeText: 'Willkommen bei Bürokrator AI!'
        },
        {
            code: 'en',
            name: 'English',
            englishName: 'English',
            flag: '🇬🇧',
            gradient: 'from-blue-400 via-red-400 to-blue-600',
            bgGradient: 'from-blue-500/20 via-red-500/20 to-blue-600/20',
            description: 'English language for document analysis',
            welcomeText: 'Welcome to Bürokrator AI!'
        }
    ];

    const handleLanguageSelect = async (language) => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        
        if (language.code === selectedLanguage) {
            return;
        }

        setIsLoading(true);
        setSelectedLanguage(language.code);
        
        try {
            const success = await updateUserLanguage(language.code);
            if (success) {
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                }
                setShowConfirmation(true);
                setTimeout(() => {
                    setShowConfirmation(false);
                    onBack();
                }, 1500);
            }
        } catch (error) {
            console.error('Error updating language:', error);
            if (isTelegramWebApp()) {
                hapticFeedback('error');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleBack = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        onBack();
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
            {/* Header */}
            <div className="relative z-10 p-6">
                <div className="flex items-center justify-between mb-8">
                    <button
                        onClick={handleBack}
                        className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span>Назад</span>
                    </button>
                    <div className="flex items-center space-x-2">
                        <Globe className="w-6 h-6 text-purple-400" />
                        <span className="text-lg font-semibold">Выбор языка</span>
                    </div>
                </div>

                {/* Description */}
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Выберите язык для анализа документов
                    </h1>
                    <p className="text-white/70 text-sm">
                        Этот язык будет использоваться для анализа документов и интерфейса
                    </p>
                </div>

                {/* Language Options */}
                <div className="space-y-4">
                    {languages.map((language, index) => (
                        <div
                            key={language.code}
                            className={`transform transition-all duration-500 ${
                                animateIn ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
                            }`}
                            style={{ transitionDelay: `${index * 100}ms` }}
                        >
                            <button
                                onClick={() => handleLanguageSelect(language)}
                                disabled={isLoading}
                                className={`w-full p-4 rounded-2xl border-2 transition-all duration-300 ${
                                    selectedLanguage === language.code
                                        ? 'border-purple-500 bg-gradient-to-r from-purple-500/20 to-pink-500/20 shadow-lg shadow-purple-500/25'
                                        : 'border-white/20 bg-white/10 hover:border-purple-400 hover:bg-white/20'
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="text-3xl">{language.flag}</div>
                                        <div className="text-left">
                                            <div className="font-semibold text-lg">{language.name}</div>
                                            <div className="text-sm text-white/70">{language.englishName}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {selectedLanguage === language.code && (
                                            <Check className="w-5 h-5 text-green-400" />
                                        )}
                                        <ChevronRight className="w-5 h-5 text-white/60" />
                                    </div>
                                </div>
                                <div className="mt-2 text-sm text-white/60 text-left">
                                    {language.description}
                                </div>
                            </button>
                        </div>
                    ))}
                </div>

                {/* Current Language Display */}
                {user?.preferred_language && (
                    <div className="mt-8 p-4 bg-white/10 rounded-xl border border-white/20">
                        <div className="flex items-center space-x-2 text-sm text-white/70">
                            <Star className="w-4 h-4 text-yellow-400" />
                            <span>Текущий язык: {languages.find(l => l.code === user.preferred_language)?.name || user.preferred_language}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Confirmation Modal */}
            {showConfirmation && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white/10 backdrop-blur-lg p-6 rounded-2xl border border-white/20 mx-4">
                        <div className="flex items-center space-x-3 mb-4">
                            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                                <Check className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg">Язык изменен!</h3>
                                <p className="text-sm text-white/70">
                                    Новый язык: {languages.find(l => l.code === selectedLanguage)?.name}
                                </p>
                            </div>
                        </div>
                        <div className="flex justify-center">
                            <div className="flex items-center space-x-1 text-sm text-white/70">
                                <Sparkles className="w-4 h-4" />
                                <span>Возвращаемся в меню...</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TelegramLanguageSelector;