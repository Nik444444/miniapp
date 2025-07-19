import React, { useContext, useState, useCallback, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import TelegramAnalysisResult from './TelegramAnalysisResult';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { 
    Upload, 
    FileText, 
    Image, 
    AlertCircle,
    CheckCircle,
    ArrowLeft,
    Camera,
    Download,
    Trash2,
    Eye,
    Clock,
    Sparkles,
    Zap,
    Star,
    Heart,
    Settings,
    RotateCcw,
    RefreshCw,
    Crown,
    Diamond,
    Gem,
    Wand2,
    Flame,
    Bot,
    Cpu,
    Activity,
    Shield,
    Rocket,
    Globe,
    Layers,
    Target,
    Award
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const TelegramDocumentAnalysis = ({ onBack }) => {
    const { user } = useContext(AuthContext);
    const { t } = useLanguage();
    const [analysisResult, setAnalysisResult] = useState(null);
    const [showAnalysisResult, setShowAnalysisResult] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [dragActive, setDragActive] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [currentFile, setCurrentFile] = useState(null);

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

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setCurrentFile(file);
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
        setUploadProgress(0);
        
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }

        try {
            console.log('Starting file analysis:', file.name, 'User token:', user?.token ? 'present' : 'missing');
            
            // Проверяем есть ли токен для аутентификации
            if (!user?.token) {
                const errorMsg = 'Необходимо войти в систему для анализа документов';
                setError(errorMsg);
                if (isTelegramWebApp()) {
                    hapticFeedback('warning');
                    showTelegramAlert(errorMsg);
                }
                setLoading(false);
                return;
            }
            
            // Уведомляем пользователя, если нет API ключей (но продолжаем с системными)
            if (!user?.has_gemini_api_key && !user?.has_api_key_1 && !user?.gemini_api_key) {
                console.log('User has no API key, will try system providers');
            }
            
            // Симуляция прогресса загрузки
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return prev;
                    }
                    return prev + 10;
                });
            }, 200);
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Добавляем язык пользователя из профиля
            if (user?.preferred_language) {
                formData.append('language', user.preferred_language);
            }

            const response = await axios.post(`${BACKEND_URL}/api/analyze-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${user.token}`
                }
            });

            clearInterval(progressInterval);
            setUploadProgress(100);

            console.log('Analysis response:', response.data);

            if (response.data && (response.data.analysis || response.data.super_analysis)) {
                setAnalysisResult(response.data);
                setShowAnalysisResult(true);
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                    showTelegramAlert(t('analysisSuccess'));
                }
            } else {
                console.error('Analysis response missing expected fields:', response.data);
                setError('Анализ не удался - неверный формат ответа от сервера');
                if (isTelegramWebApp()) {
                    hapticFeedback('error');
                    showTelegramAlert('Анализ не удался - неверный формат ответа от сервера');
                }
            }
        } catch (error) {
            console.error('File analysis error:', error);
            
            let errorMessage = t('analysisError');
            
            if (error.response) {
                if (error.response.status === 401) {
                    errorMessage = t('authError');
                } else if (error.response.status === 400) {
                    if (error.response.data?.detail?.includes('API')) {
                        errorMessage = 'Недействительный API ключ или ключ не настроен';
                    } else {
                        errorMessage = 'Неверный формат файла или ошибка данных';
                    }
                } else if (error.response.data?.detail) {
                    errorMessage = error.response.data.detail;
                }
            } else if (error.request) {
                errorMessage = t('connectionError');
            }
            
            setError(errorMessage);
            if (isTelegramWebApp()) {
                hapticFeedback('error');
                showTelegramAlert(`${t('error')}: ${errorMessage}`);
            }
        } finally {
            setLoading(false);
            setUploadProgress(0);
        }
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setCurrentFile(file);
            analyzeFile(file);
        }
    };

    const resetAnalysis = () => {
        setAnalysisResult(null);
        setShowAnalysisResult(false);
        setError('');
        setCurrentFile(null);
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
    };

    if (showAnalysisResult && analysisResult) {
        return (
            <TelegramAnalysisResult 
                analysisResult={analysisResult} 
                onClose={() => setShowAnalysisResult(false)}
            />
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/30 to-pink-900/20"></div>
            
            {/* Floating Particles */}
            <FloatingParticles />
            
            {/* Animated Gradient Orbs */}
            <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
            
            {/* Header */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onBack}
                        className="flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl px-4 py-2 hover:bg-white/20 transition-all duration-200"
                    >
                        <ArrowLeft className="w-5 h-5 text-white" />
                        <span className="text-white">{t('back')}</span>
                    </button>
                    
                    <div className="text-center">
                        <h1 className="text-2xl font-bold">
                            <GradientText className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                                {t('documentAnalysis')}
                            </GradientText>
                        </h1>
                        <p className="text-sm text-gray-300">{t('aiAnalysis')}</p>
                    </div>
                    
                    <div className="w-16"></div> {/* Spacer */}
                </div>
            </div>

            {/* Main Content */}
            <div className="relative z-10 px-4 pb-8">
                <div className="max-w-2xl mx-auto space-y-6">
                    {/* File Upload */}
                    <FloatingElement delay={200}>
                        <GlassCard className="p-6 bg-white/10 backdrop-blur-xl border border-white/20">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                    <Upload className="w-8 h-8 text-white" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-white">{t('uploadDocument')}</h3>
                                    <p className="text-sm text-gray-300">{t('aiAnalysisInSeconds')}</p>
                                </div>
                            </div>
                            
                            <div
                                {...getRootProps()}
                                className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 relative overflow-hidden ${
                                    isDragActive 
                                        ? 'border-blue-400 bg-blue-500/20 scale-105' 
                                        : 'border-white/30 bg-white/5 hover:border-blue-400/50 hover:bg-white/10'
                                }`}
                            >
                                <input {...getInputProps()} />
                                <input 
                                    type="file"
                                    accept=".pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp,.txt"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                    id="file-input-analysis"
                                />
                                
                                {/* Loading Progress */}
                                {loading && uploadProgress > 0 && (
                                    <div className="absolute top-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300" 
                                         style={{width: `${uploadProgress}%`}}>
                                    </div>
                                )}
                                
                                <div className="space-y-6">
                                    <div className={`w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto transition-all duration-300 ${
                                        loading ? 'animate-pulse scale-110' : 'hover:scale-110'
                                    }`}>
                                        {loading ? (
                                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
                                        ) : (
                                            <FileText className="w-12 h-12 text-white" />
                                        )}
                                    </div>
                                    
                                    <div>
                                        <h4 className="text-xl font-semibold text-white mb-2">
                                            {loading ? (
                                                <span className="flex items-center justify-center space-x-2">
                                                    <span>{t('analyzing')}</span>
                                                    <span className="animate-pulse">🤖</span>
                                                </span>
                                            ) : (
                                                t('dragFileOrClick')
                                            )}
                                        </h4>
                                        <p className="text-sm text-gray-300 mb-4">
                                            📄 PDF • 🖼️ Изображения • 📝 Текст (до 10MB)
                                        </p>
                                        
                                        {loading && (
                                            <div className="bg-blue-500/20 border border-blue-400/30 rounded-lg p-3 mb-4">
                                                <div className="flex items-center justify-center space-x-2">
                                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></div>
                                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200"></div>
                                                </div>
                                                <p className="text-sm text-blue-200 text-center mt-2">
                                                    {uploadProgress < 100 ? `Загрузка ${uploadProgress}%` : 'Анализ документа...'}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {!loading && (
                                        <div className="space-y-4">
                                            <button
                                                type="button"
                                                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 flex items-center space-x-3 mx-auto font-medium transform hover:scale-105 shadow-lg"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    if (isTelegramWebApp()) {
                                                        hapticFeedback('light');
                                                    }
                                                    const fileInput = document.getElementById('file-input-analysis');
                                                    if (fileInput) {
                                                        fileInput.click();
                                                    }
                                                }}
                                            >
                                                <Upload className="w-5 h-5" />
                                                <span>{t('selectFile')}</span>
                                                <span className="text-xl">📁</span>
                                            </button>
                                            
                                            <div className="grid grid-cols-3 gap-4 text-center">
                                                <div className="bg-white/10 rounded-lg p-3">
                                                    <FileText className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                                                    <p className="text-xs text-gray-300">PDF</p>
                                                </div>
                                                <div className="bg-white/10 rounded-lg p-3">
                                                    <Image className="w-6 h-6 text-purple-400 mx-auto mb-1" />
                                                    <p className="text-xs text-gray-300">Фото</p>
                                                </div>
                                                <div className="bg-white/10 rounded-lg p-3">
                                                    <Camera className="w-6 h-6 text-pink-400 mx-auto mb-1" />
                                                    <p className="text-xs text-gray-300">Скан</p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </GlassCard>
                    </FloatingElement>

                    {/* Error Display */}
                    {error && (
                        <FloatingElement delay={400}>
                            <GlassCard className="p-4 bg-red-500/20 border border-red-400/30 animate-shake">
                                <div className="flex items-center space-x-3">
                                    <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
                                    <div>
                                        <p className="text-red-300 font-medium">{t('analysisError')}</p>
                                        <p className="text-red-200 text-sm">{error}</p>
                                    </div>
                                </div>
                            </GlassCard>
                        </FloatingElement>
                    )}

                    {/* Current File Info */}
                    {currentFile && !loading && (
                        <FloatingElement delay={600}>
                            <GlassCard className="p-4 bg-white/10 backdrop-blur-xl border border-white/20">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
                                            <FileText className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <p className="text-white font-medium truncate max-w-48">{currentFile.name}</p>
                                            <p className="text-gray-300 text-sm">{(currentFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={resetAnalysis}
                                        className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200"
                                    >
                                        <RefreshCw className="w-4 h-4 text-gray-300" />
                                    </button>
                                </div>
                            </GlassCard>
                        </FloatingElement>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TelegramDocumentAnalysis;