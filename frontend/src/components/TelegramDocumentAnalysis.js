import React, { useContext, useState, useCallback, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import ImprovedTelegramAnalysisResult from './ImprovedTelegramAnalysisResult';
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
    const [animateIn, setAnimateIn] = useState(false);
    const [processingStage, setProcessingStage] = useState('');
    const [magneticHover, setMagneticHover] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [filePreview, setFilePreview] = useState(null);

    // Анимация появления
    useEffect(() => {
        const timer = setTimeout(() => setAnimateIn(true), 300);
        return () => clearTimeout(timer);
    }, []);

    // Симуляция этапов обработки
    useEffect(() => {
        if (loading) {
            const stages = [
                '🚀 Подготовка к анализу...',
                '🔍 Сканирование документа...',
                '🤖 Извлечение текста...',
                '💎 Обработка содержимого...',
                '⚡ Создание анализа...',
                '✨ Финализация результатов...'
            ];
            let currentStage = 0;
            
            const interval = setInterval(() => {
                setProcessingStage(stages[currentStage]);
                currentStage = (currentStage + 1) % stages.length;
            }, 1500);
            
            return () => clearInterval(interval);
        } else {
            setProcessingStage('');
        }
    }, [loading]);

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
            setSelectedFile(file);
            
            // Создаем превью для изображений
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => setFilePreview(e.target.result);
                reader.readAsDataURL(file);
            } else {
                setFilePreview(null);
            }
            
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
            
            // Симуляция прогресса загрузки с более красивой анимацией
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return prev;
                    }
                    return prev + Math.random() * 15 + 5; // Более динамичный прогресс
                });
            }, 300);
            
            const formData = new FormData();
            formData.append('file', file);
            
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
                    // Убираем уведомление - результаты показываются сразу
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
            setSelectedFile(file);
            analyzeFile(file);
        }
    };

    const resetAnalysis = () => {
        setAnalysisResult(null);
        setShowAnalysisResult(false);
        setError('');
        setCurrentFile(null);
        setSelectedFile(null);
        setFilePreview(null);
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
    };

    const getFileIcon = (file) => {
        if (!file) return <FileText className="h-8 w-8" />;
        
        if (file.type.startsWith('image/')) {
            return <Image className="h-8 w-8" />;
        } else if (file.type === 'application/pdf') {
            return <FileText className="h-8 w-8" />;
        } else {
            return <FileText className="h-8 w-8" />;
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    if (showAnalysisResult && analysisResult) {
        return (
            <ImprovedTelegramAnalysisResult 
                analysisResult={analysisResult} 
                onClose={() => setShowAnalysisResult(false)}
            />
        );
    }

    return (
        <div className={`min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative transition-all duration-500 ${
            animateIn ? 'opacity-100' : 'opacity-0'
        }`}>
            
            {/* Простой фон без анимаций */}
            <div className="absolute inset-0">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/30 to-pink-900/20"></div>
            </div>
            
            {/* Header */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onBack}
                        className="flex items-center space-x-2 bg-white/20 backdrop-blur-xl rounded-xl px-4 py-2 hover:bg-white/30 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-white" />
                        <span className="text-white font-semibold">Назад</span>
                    </button>
                    
                    <div className="text-center">
                        <h1 className="text-2xl font-black text-white mb-1">
                            Анализ документов
                        </h1>
                        <p className="text-blue-200 font-medium">AI анализ</p>
                    </div>
                    
                    <div className="w-20"></div>
                </div>
            </div>

            {/* Основной контент с невероятными эффектами */}
            <div className="relative z-10 px-4 pb-8">
                <div className="max-w-2xl mx-auto space-y-8">
                    
                    {/* ОБЛАСТЬ ЗАГРУЗКИ */}
                    <div className={`transform transition-all duration-500 ${
                        animateIn ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
                    }`}>
                        <div className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 ${
                            isDragActive
                                ? 'border-blue-400 bg-blue-50/80' 
                                : 'border-gray-400 bg-white/20 hover:border-blue-300'
                        }`}>

                            <div 
                                {...getRootProps()}
                                className="relative p-8 cursor-pointer"
                            >
                                <input {...getInputProps()} />
                                <input 
                                    type="file"
                                    accept=".pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp,.txt"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                    id="file-input-analysis"
                                />
                                
                                {/* Простой прогресс-бар */}
                                {loading && uploadProgress > 0 && (
                                    <div className="absolute top-0 left-0 h-1 bg-blue-500 transition-all duration-300 rounded-t-2xl" 
                                         style={{width: `${uploadProgress}%`}}>
                                    </div>
                                )}
                                
                                {loading ? (
                                    // Простое состояние загрузки
                                    <div className="space-y-4 text-center">
                                        <div className="mx-auto w-16 h-16 border-4 border-blue-200 rounded-full animate-spin border-t-blue-600"></div>
                                        <div className="space-y-2">
                                            <h3 className="text-xl font-bold text-white">Анализ документа</h3>
                                            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 max-w-sm mx-auto">
                                                <p className="text-white">{processingStage}</p>
                                            </div>
                                            <div className="mt-2 bg-white/20 rounded-full p-2">
                                                <div className="text-sm text-white/80">Загрузка результата...</div>
                                            </div>
                                        </div>
                                    </div>
                                ) : selectedFile ? (
                                    // Простое отображение выбранного файла
                                    <div className="space-y-4 text-center">
                                        <div className="mx-auto w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center">
                                            <CheckCircle className="h-10 w-10 text-white" />
                                        </div>
                                        <div className="space-y-3">
                                            <h3 className="text-xl font-bold text-white">Файл готов к анализу</h3>
                                            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 max-w-sm mx-auto">
                                                <div className="flex items-center space-x-3">
                                                    <div className="text-green-300">{getFileIcon(selectedFile)}</div>
                                                    <div className="text-left">
                                                        <p className="font-bold text-white text-sm truncate">
                                                            {selectedFile.name}
                                                        </p>
                                                        <p className="text-green-200 text-sm">
                                                            {formatFileSize(selectedFile.size)}
                                                        </p>
                                                    </div>
                                                </div>
                                                {filePreview && (
                                                    <div className="mt-3">
                                                        <img 
                                                            src={filePreview} 
                                                            alt="Preview" 
                                                            className="max-w-full max-h-24 rounded-xl mx-auto border border-green-300/50"
                                                        />
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    // Простое состояние по умолчанию
                                    <div className="space-y-6 text-center">
                                        <div className="mx-auto w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                                            <Upload className="h-12 w-12 text-white" />
                                        </div>
                                        <div className="space-y-4">
                                            <h3 className="text-xl font-bold text-white">Загрузить документ для анализа</h3>
                                            <div className="bg-white/20 backdrop-blur-sm rounded-xl p-4 border border-gray-300/30">
                                                <p className="text-white mb-4 font-medium">
                                                    {isDragActive 
                                                        ? "Отпустите файл для анализа" 
                                                        : "Перетащите файл сюда или нажмите для выбора"
                                                    }
                                                </p>
                                                <div className="grid grid-cols-3 gap-3 max-w-xs mx-auto mb-4">
                                                    <div className="flex flex-col items-center space-y-2 p-3 bg-blue-500/20 rounded-xl">
                                                        <FileText className="h-6 w-6 text-blue-300" />
                                                        <span className="text-xs font-medium text-blue-200">PDF</span>
                                                    </div>
                                                    <div className="flex flex-col items-center space-y-2 p-3 bg-purple-500/20 rounded-xl">
                                                        <Image className="h-6 w-6 text-purple-300" />
                                                        <span className="text-xs font-medium text-purple-200">Фото</span>
                                                    </div>
                                                    <div className="flex flex-col items-center space-y-2 p-3 bg-cyan-500/20 rounded-xl">
                                                        <Camera className="h-6 w-6 text-cyan-300" />
                                                        <span className="text-xs font-medium text-cyan-200">Скан</span>
                                                    </div>
                                                </div>
                                                <button
                                                    type="button"
                                                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-colors flex items-center space-x-2 mx-auto font-bold"
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
                                                    <Upload className="w-4 h-4" />
                                                    <span>Выбрать файл</span>
                                                </button>
                                            </div>
                                            <div className="bg-gray-500/20 rounded-xl p-3 border border-gray-300/30">
                                                <p className="text-sm text-gray-300 font-medium flex items-center justify-center space-x-2">
                                                    <Shield className="h-4 w-4" />
                                                    <span>Максимальный размер: 10MB</span>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                
                                {error && (
                                    <div className="mt-6 p-4 bg-red-500/20 border border-red-400/30 rounded-xl">
                                        <div className="flex items-center space-x-2 text-red-300">
                                            <AlertCircle className="h-5 w-5" />
                                            <span className="font-bold">{error}</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Информация о файле */}
                    {currentFile && !loading && (
                        <div className={`transform transition-all duration-300 ${
                            animateIn ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                        }`}>
                            <div className="bg-white/20 backdrop-blur-xl rounded-xl p-4 border border-white/30">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
                                            {getFileIcon(currentFile)}
                                        </div>
                                        <div>
                                            <p className="text-white font-bold truncate max-w-32">{currentFile.name}</p>
                                            <p className="text-green-200 text-sm">{(currentFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={resetAnalysis}
                                        className="p-2 bg-white/20 hover:bg-white/30 rounded-xl transition-colors"
                                    >
                                        <RefreshCw className="w-5 h-5 text-white" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TelegramDocumentAnalysis;