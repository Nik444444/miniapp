import React, { useContext, useState, useCallback, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import UserProfile from './UserProfile';
import ImprovedAnalysisResult from './ImprovedAnalysisResult';
import TelegramNews from './TelegramNews';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
    Upload, 
    User, 
    LogOut, 
    FileText, 
    Image, 
    Clock, 
    AlertCircle,
    CheckCircle,
    Eye,
    History,
    Settings,
    Download,
    Trash2,
    X,
    Sparkles,
    Zap,
    Star,
    Heart,
    Crown,
    Wand2,
    Rainbow,
    Flame,
    Rocket,
    Key,
    Palette,
    Shield,
    ChevronDown,
    ChevronUp,
    Camera,
    Smartphone,
    ExternalLink
} from 'lucide-react';
import { 
    GlassCard, 
    GradientText
} from './UIEffects';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const BrowserMainApp = () => {
    const { user, logout } = useContext(AuthContext);
    const [showProfile, setShowProfile] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [showAnalysisResult, setShowAnalysisResult] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [showGeminiSetup, setShowGeminiSetup] = useState(false);
    const [geminiApiKey, setGeminiApiKey] = useState('');
    const [geminiKeyLoading, setGeminiKeyLoading] = useState(false);
    const [geminiKeyMessage, setGeminiKeyMessage] = useState('');
    const [geminiKeySuccessful, setGeminiKeySuccessful] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            analyzeFile(file);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
            'text/*': ['.txt']
        },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024 // 10MB
    });

    const analyzeFile = async (file) => {
        setLoading(true);
        setError('');
        setAnalysisResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(`${BACKEND_URL}/api/analyze-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${user.token}`
                }
            });

            if (response.data.analysis) {
                setAnalysisResult(response.data.analysis);
                setShowAnalysisResult(true);
            } else {
                setError('Анализ не удался');
            }
        } catch (error) {
            setError(error.response?.data?.detail || 'Ошибка при анализе файла');
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            analyzeFile(file);
        }
    };

    const openGeminiSetup = () => {
        setShowGeminiSetup(true);
    };

    const handleGeminiKeySubmit = async () => {
        if (!geminiApiKey.trim()) {
            setGeminiKeyMessage('Введите API ключ');
            return;
        }

        setGeminiKeyLoading(true);
        setGeminiKeyMessage('');
        
        try {
            const response = await axios.post(`${BACKEND_URL}/api/quick-gemini-setup`, {
                api_key: geminiApiKey
            }, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            
            if (response.data.status === 'success') {
                setGeminiKeySuccessful(true);
                setGeminiKeyMessage('API ключ успешно сохранен!');
                
                setTimeout(() => {
                    setShowGeminiSetup(false);
                    setGeminiApiKey('');
                }, 2000);
            } else {
                setGeminiKeyMessage(response.data.message || 'Ошибка сохранения API ключа');
            }
        } catch (error) {
            setGeminiKeyMessage('Ошибка сохранения API ключа');
        } finally {
            setGeminiKeyLoading(false);
        }
    };

    const fetchHistory = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/analysis-history`, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            setHistory(response.data.history || []);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    const toggleHistory = () => {
        setShowHistory(!showHistory);
        if (!showHistory) {
            fetchHistory();
        }
    };

    const handleLogout = () => {
        logout();
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                                    <FileText className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
                                        German Letter AI
                                    </h1>
                                    <p className="text-xs text-gray-500">Browser Version</p>
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                            <div className="hidden md:flex items-center space-x-2">
                                <span className="text-sm text-gray-600">Привет, {user.name}!</span>
                            </div>
                            <button
                                onClick={() => setShowProfile(!showProfile)}
                                className="relative p-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
                            >
                                <User className="w-5 h-5" />
                            </button>
                            <button
                                onClick={handleLogout}
                                className="p-2 rounded-xl bg-red-500 text-white hover:bg-red-600 transition-all duration-200 transform hover:scale-105 shadow-lg"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                    {/* Left Column - Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Profile Section */}
                        {showProfile && (
                            <UserProfile />
                        )}

                        {/* API Key Setup */}
                        <GlassCard className="p-6 bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl">
                            <div className="flex items-center space-x-4 mb-4">
                                <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl">
                                    <Key className="h-6 w-6 text-white" />
                                </div>
                                <h2 className="text-xl font-bold">
                                    <GradientText>API Ключ</GradientText>
                                </h2>
                            </div>
                            
                            {!geminiKeySuccessful ? (
                                <div className="space-y-4">
                                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
                                        <div className="flex items-center space-x-3">
                                            <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                                <Sparkles className="h-4 w-4 text-white" />
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-gray-900">Нужен API ключ для работы с AI</h3>
                                                <p className="text-sm text-gray-600">Получите бесплатный API ключ от Google</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={openGeminiSetup}
                                            className="mt-3 w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2"
                                        >
                                            <Key className="w-4 h-4" />
                                            <span>Настроить API ключ</span>
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl p-4 border border-green-200">
                                    <div className="flex items-center space-x-3">
                                        <CheckCircle className="h-8 w-8 text-green-500" />
                                        <div>
                                            <h3 className="font-semibold text-green-900">API ключ настроен</h3>
                                            <p className="text-sm text-green-600">Готово к анализу документов</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </GlassCard>

                        {/* File Upload */}
                        <GlassCard className="p-6 bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                    <Upload className="h-6 w-6 text-white" />
                                </div>
                                <h2 className="text-xl font-bold">
                                    <GradientText>Загрузите документ</GradientText>
                                </h2>
                            </div>
                            
                            <div
                                {...getRootProps()}
                                className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
                                    isDragActive 
                                        ? 'border-blue-500 bg-blue-50' 
                                        : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50'
                                }`}
                            >
                                <input {...getInputProps()} />
                                <div className="space-y-4">
                                    <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto shadow-lg">
                                        {loading ? (
                                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white"></div>
                                        ) : (
                                            <FileText className="w-10 h-10 text-white" />
                                        )}
                                    </div>
                                    <div>
                                        <p className="text-xl font-semibold text-gray-900 mb-2">
                                            {loading ? 'Анализируем документ...' : 'Перетащите файл сюда'}
                                        </p>
                                        <p className="text-gray-600">
                                            PDF, изображения, текстовые файлы (до 10MB)
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center space-x-2 mx-auto"
                                        disabled={loading}
                                    >
                                        <Upload className="w-5 h-5" />
                                        <span>Выбрать файл</span>
                                    </button>
                                </div>
                            </div>
                            
                            {error && (
                                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
                                    <div className="flex items-center space-x-2">
                                        <AlertCircle className="w-5 h-5 text-red-500" />
                                        <p className="text-sm text-red-700">{error}</p>
                                    </div>
                                </div>
                            )}
                        </GlassCard>

                        {/* History */}
                        <GlassCard className="p-6 bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-4">
                                    <div className="p-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl">
                                        <History className="h-6 w-6 text-white" />
                                    </div>
                                    <h2 className="text-xl font-bold">
                                        <GradientText>История анализов</GradientText>
                                    </h2>
                                </div>
                                <button
                                    onClick={toggleHistory}
                                    className="p-2 rounded-lg bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 transition-all duration-200"
                                >
                                    {showHistory ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                                </button>
                            </div>
                            
                            {showHistory && (
                                <div className="space-y-3">
                                    {history.length === 0 ? (
                                        <p className="text-gray-500 text-center py-4">История пуста</p>
                                    ) : (
                                        history.map((item, index) => (
                                            <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-3">
                                                        <FileText className="w-4 h-4 text-gray-400" />
                                                        <div>
                                                            <p className="font-medium text-gray-900">{item.filename}</p>
                                                            <p className="text-sm text-gray-500">{item.date}</p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => {
                                                            setAnalysisResult(item.result);
                                                            setShowAnalysisResult(true);
                                                        }}
                                                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                    >
                                                        <Eye className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </GlassCard>
                    </div>

                    {/* Right Column - News */}
                    <div className="lg:col-span-1">
                        <TelegramNews />
                    </div>
                </div>
            </main>

            {/* Analysis Result Modal */}
            {showAnalysisResult && analysisResult && (
                <ImprovedAnalysisResult
                    analysisResult={analysisResult}
                    onClose={() => setShowAnalysisResult(false)}
                />
            )}

            {/* Gemini API Key Setup Modal */}
            {showGeminiSetup && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full">
                        {/* Header */}
                        <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-t-2xl">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center">
                                        <Key className="h-5 w-5 text-white" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold">Получить API ключ</h2>
                                        <p className="text-blue-100 text-sm">Быстрое получение за 1 минуту</p>
                                    </div>
                                </div>
                                <button 
                                    onClick={() => setShowGeminiSetup(false)}
                                    className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                                >
                                    <X className="h-5 w-5 text-white" />
                                </button>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="p-6">
                            <div className="space-y-4">
                                <div className="bg-blue-50 rounded-xl p-4">
                                    <h3 className="font-semibold text-blue-900 mb-2">Получите бесплатный API ключ</h3>
                                    <p className="text-sm text-blue-800 mb-3">
                                        Нажмите кнопку ниже, чтобы перейти к Google AI Studio и получить API ключ
                                    </p>
                                </div>

                                <div className="bg-yellow-50 rounded-xl p-4">
                                    <h4 className="font-semibold text-yellow-800 mb-2">Простая инструкция:</h4>
                                    <ol className="text-sm text-yellow-700 space-y-1">
                                        <li>1. Нажмите "Получить API ключ"</li>
                                        <li>2. Войдите в Google аккаунт</li>
                                        <li>3. Нажмите "Create API key"</li>
                                        <li>4. Скопируйте ключ и вернитесь сюда</li>
                                    </ol>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Gemini API Key
                                    </label>
                                    <input
                                        type="password"
                                        placeholder="Вставьте ваш Gemini API ключ"
                                        value={geminiApiKey}
                                        onChange={(e) => setGeminiApiKey(e.target.value)}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">
                                        Формат: AIza...
                                    </p>
                                </div>

                                {geminiKeyMessage && (
                                    <div className={`p-3 rounded-lg ${
                                        geminiKeySuccessful 
                                            ? 'bg-green-50 text-green-800' 
                                            : 'bg-red-50 text-red-800'
                                    }`}>
                                        <p className="text-sm">{geminiKeyMessage}</p>
                                    </div>
                                )}

                                <div className="flex space-x-3">
                                    <button
                                        onClick={() => window.open('https://aistudio.google.com/apikey', '_blank')}
                                        className="flex-1 inline-flex items-center justify-center space-x-2 bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-3 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
                                    >
                                        <ExternalLink className="h-4 w-4" />
                                        <span>Получить API ключ</span>
                                    </button>
                                    <button
                                        onClick={handleGeminiKeySubmit}
                                        disabled={geminiKeyLoading || !geminiApiKey.trim()}
                                        className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        {geminiKeyLoading ? (
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                        ) : (
                                            <Zap className="h-4 w-4" />
                                        )}
                                        <span>Сохранить</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BrowserMainApp;