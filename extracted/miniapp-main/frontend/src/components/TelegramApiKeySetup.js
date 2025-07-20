import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Key,
    CheckCircle,
    AlertCircle,
    ArrowLeft,
    ExternalLink,
    Copy,
    Eye,
    EyeOff,
    Sparkles,
    Shield,
    Globe,
    Zap,
    Star,
    Crown,
    Wand2,
    Settings,
    RefreshCw,
    Lock,
    Unlock,
    Heart,
    Lightbulb
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

const TelegramApiKeySetup = ({ onBack }) => {
    const { user, saveGeminiApiKey, fetchUserProfile } = useContext(AuthContext);
    const [apiKey, setApiKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [showKey, setShowKey] = useState(false);
    const [step, setStep] = useState(1);
    const [isSuccess, setIsSuccess] = useState(false);

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

    const handleSaveApiKey = async () => {
        if (!apiKey.trim()) {
            setMessage('Пожалуйста, введите API ключ');
            if (isTelegramWebApp()) {
                hapticFeedback('warning');
            }
            return;
        }

        if (!apiKey.startsWith('AIza')) {
            setMessage('API ключ должен начинаться с "AIza"');
            if (isTelegramWebApp()) {
                hapticFeedback('warning');
            }
            return;
        }

        setLoading(true);
        setMessage('');
        
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }

        try {
            const result = await saveGeminiApiKey(apiKey);
            
            if (result.success) {
                setMessage('API ключ успешно сохранен! Обновляем страницу...');
                setIsSuccess(true);
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                    showTelegramAlert('API ключ успешно сохранен! 🎉');
                }
                
                // Обновляем профиль пользователя
                await fetchUserProfile();
                
                // Автоматически перезагружаем страницу через 500ms
                setTimeout(() => {
                    window.location.reload();
                }, 500);
                
            } else {
                setMessage(result.error || 'Ошибка при сохранении API ключа');
                if (isTelegramWebApp()) {
                    hapticFeedback('error');
                }
            }
        } catch (error) {
            console.error('Error saving API key:', error);
            setMessage('Ошибка при сохранении API ключа');
            if (isTelegramWebApp()) {
                hapticFeedback('error');
            }
        } finally {
            setLoading(false);
        }
    };

    const pasteFromClipboard = async () => {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                const text = await navigator.clipboard.readText();
                if (text.trim()) {
                    setApiKey(text.trim());
                    setMessage('Текст вставлен из буфера обмена');
                    if (isTelegramWebApp()) {
                        hapticFeedback('success');
                    }
                } else {
                    setMessage('Буфер обмена пуст');
                    if (isTelegramWebApp()) {
                        hapticFeedback('warning');
                    }
                }
            } else {
                setMessage('Функция буфера обмена не поддерживается');
                if (isTelegramWebApp()) {
                    hapticFeedback('warning');
                }
            }
        } catch (error) {
            console.error('Clipboard error:', error);
            setMessage('Ошибка при чтении буфера обмена');
            if (isTelegramWebApp()) {
                hapticFeedback('error');
            }
        }
    };

    const openGoogleAI = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
            const tg = getTelegramWebApp();
            if (tg && tg.openLink) {
                tg.openLink('https://aistudio.google.com/apikey');
            } else {
                window.open('https://aistudio.google.com/apikey', '_blank');
            }
        } else {
            window.open('https://aistudio.google.com/apikey', '_blank');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/20 via-green-900/30 to-teal-900/20"></div>
            
            {/* Floating Particles */}
            <FloatingParticles />
            
            {/* Animated Gradient Orbs */}
            <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-br from-emerald-500/30 to-teal-500/30 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-green-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
            
            {/* Header */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onBack}
                        className="flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl px-4 py-2 hover:bg-white/20 transition-all duration-200"
                    >
                        <ArrowLeft className="w-5 h-5 text-white" />
                        <span className="text-white">Назад</span>
                    </button>
                    
                    <div className="text-center">
                        <h1 className="text-2xl font-bold">
                            <GradientText className="bg-gradient-to-r from-emerald-400 via-green-400 to-teal-400">
                                API Ключ
                            </GradientText>
                        </h1>
                        <p className="text-sm text-gray-300">Настройка доступа к AI</p>
                    </div>
                    
                    <div className="w-16 flex justify-center">
                        <div className="relative">
                            <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center">
                                <Key className="w-4 h-4 text-white" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-green-400 to-blue-400 rounded-full flex items-center justify-center animate-bounce">
                                <Crown className="w-2 h-2 text-white" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 px-4 pb-8">
                <div className="max-w-2xl mx-auto space-y-6">
                    {/* Status Card */}
                    <FloatingElement delay={0}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="text-center">
                                <div className="flex items-center justify-center mb-4">
                                    {user?.has_gemini_api_key ? (
                                        <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center animate-pulse">
                                            <CheckCircle className="w-8 h-8 text-white" />
                                        </div>
                                    ) : (
                                        <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center animate-pulse">
                                            <AlertCircle className="w-8 h-8 text-white" />
                                        </div>
                                    )}
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">
                                    {user?.has_gemini_api_key ? 'API ключ настроен' : 'Нужен API ключ'}
                                </h3>
                                <p className="text-gray-300 text-sm">
                                    {user?.has_gemini_api_key 
                                        ? 'Все инструменты доступны для использования'
                                        : 'Для работы с AI необходим бесплатный API ключ от Google'
                                    }
                                </p>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Instructions */}
                    <FloatingElement delay={200}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-4">
                                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl">
                                    <Lightbulb className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Инструкция</h3>
                                    <p className="text-sm text-gray-300">Получите бесплатный API ключ</p>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                        <span className="text-white text-sm font-bold">1</span>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium">Перейдите на сайт Google AI Studio</p>
                                        <p className="text-gray-300 text-sm">Нажмите кнопку ниже для перехода</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                        <span className="text-white text-sm font-bold">2</span>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium">Создайте API ключ</p>
                                        <p className="text-gray-300 text-sm">Нажмите "Create API Key" и выберите проект</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-gradient-to-r from-pink-500 to-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                        <span className="text-white text-sm font-bold">3</span>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium">Скопируйте ключ</p>
                                        <p className="text-gray-300 text-sm">Ключ начинается с "AIza..." - скопируйте его</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                        <span className="text-white text-sm font-bold">4</span>
                                    </div>
                                    <div>
                                        <p className="text-white font-medium">Вставьте в поле ниже</p>
                                        <p className="text-gray-300 text-sm">Используйте кнопку "Вставить" или введите вручную</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="mt-6">
                                <button
                                    onClick={openGoogleAI}
                                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 transform hover:scale-105 shadow-lg"
                                >
                                    <ExternalLink className="w-5 h-5" />
                                    <span>Открыть Google AI Studio</span>
                                </button>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* API Key Input */}
                    <FloatingElement delay={400}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-4">
                                <div className="p-3 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl">
                                    <Key className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Введите API ключ</h3>
                                    <p className="text-sm text-gray-300">Безопасное сохранение в системе</p>
                                </div>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="relative">
                                    <input
                                        type={showKey ? 'text' : 'password'}
                                        placeholder="AIza..."
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-emerald-400/50 focus:ring-2 focus:ring-emerald-400/20 transition-all duration-200"
                                        disabled={loading}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowKey(!showKey)}
                                        className="absolute right-3 top-3 p-1 text-gray-400 hover:text-white transition-colors"
                                    >
                                        {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                
                                <div className="flex space-x-3">
                                    <button
                                        onClick={pasteFromClipboard}
                                        className="flex-1 bg-white/10 hover:bg-white/20 border border-white/20 text-white py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                                        disabled={loading}
                                    >
                                        <Copy className="w-4 h-4" />
                                        <span>Вставить</span>
                                    </button>
                                    
                                    <button
                                        onClick={handleSaveApiKey}
                                        disabled={loading || !apiKey.trim()}
                                        className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 transform hover:scale-105 shadow-lg"
                                    >
                                        {loading ? (
                                            <>
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                <span>Сохранение...</span>
                                            </>
                                        ) : (
                                            <>
                                                <Shield className="w-4 h-4" />
                                                <span>Сохранить</span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Message */}
                    {message && (
                        <FloatingElement delay={600}>
                            <GlassCard className={`p-4 ${isSuccess ? 'bg-green-500/20 border-green-400/30' : 'bg-red-500/20 border-red-400/30'}`}>
                                <div className="flex items-center space-x-3">
                                    {isSuccess ? (
                                        <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                                    ) : (
                                        <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
                                    )}
                                    <div>
                                        <p className={`font-medium ${isSuccess ? 'text-green-300' : 'text-red-300'}`}>
                                            {isSuccess ? 'Успешно!' : 'Ошибка'}
                                        </p>
                                        <p className={`text-sm ${isSuccess ? 'text-green-200' : 'text-red-200'}`}>
                                            {message}
                                        </p>
                                    </div>
                                </div>
                            </GlassCard>
                        </FloatingElement>
                    )}

                    {/* Security Info */}
                    <FloatingElement delay={800}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-4">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                    <Shield className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">Безопасность</h3>
                                    <p className="text-sm text-gray-300">Защита ваших данных</p>
                                </div>
                            </div>
                            
                            <div className="space-y-3">
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                    <p className="text-sm text-gray-300">Ключ сохраняется в зашифрованном виде</p>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                    <p className="text-sm text-gray-300">Используется только для AI запросов</p>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                    <p className="text-sm text-gray-300">Не передается третьим лицам</p>
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>
                </div>
            </div>
        </div>
    );
};

export default TelegramApiKeySetup;