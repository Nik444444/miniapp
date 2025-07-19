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
        <div className={`min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden transition-all duration-1000 ${
            animateIn ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
        }`}>
            
            {/* СУПЕР ЭФФЕКТНЫЙ АНИМИРОВАННЫЙ ФОН */}
            <div className="absolute inset-0">
                {/* Основные градиентные слои */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/40 via-purple-900/60 to-pink-900/40 animate-pulse"></div>
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-800/30 via-transparent to-rose-800/30"></div>
                
                {/* Анимированные космические орбы */}
                <div className="absolute top-10 left-10 w-96 h-96 bg-gradient-to-br from-blue-500/40 to-purple-500/40 rounded-full blur-3xl animate-pulse opacity-80"></div>
                <div className="absolute top-40 right-20 w-80 h-80 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-full blur-3xl animate-pulse delay-1000 opacity-70"></div>
                <div className="absolute bottom-20 left-32 w-72 h-72 bg-gradient-to-br from-cyan-500/35 to-blue-500/35 rounded-full blur-3xl animate-pulse delay-2000 opacity-75"></div>
                <div className="absolute bottom-40 right-10 w-64 h-64 bg-gradient-to-br from-pink-500/30 to-purple-500/30 rounded-full blur-3xl animate-pulse delay-3000 opacity-80"></div>
                
                {/* Движущиеся световые полосы */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/10 to-transparent transform -skew-x-12 animate-pulse"></div>
                <div className="absolute inset-0 bg-gradient-to-l from-transparent via-purple-400/10 to-transparent transform skew-x-12 animate-pulse delay-1000"></div>
                
                {/* Множественные анимированные частицы */}
                <div className="absolute inset-0 pointer-events-none">
                    {[...Array(60)].map((_, i) => (
                        <div
                            key={i}
                            className={`absolute animate-pulse opacity-80`}
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 5}s`,
                                animationDuration: `${3 + Math.random() * 4}s`
                            }}
                        >
                            {i % 8 === 0 && <Sparkles className="h-3 w-3 text-blue-400/60" />}
                            {i % 8 === 1 && <Star className="h-2 w-2 text-purple-400/60" />}
                            {i % 8 === 2 && <Diamond className="h-3 w-3 text-pink-400/60" />}
                            {i % 8 === 3 && <Gem className="h-2 w-2 text-cyan-400/60" />}
                            {i % 8 === 4 && <Crown className="h-3 w-3 text-yellow-400/60" />}
                            {i % 8 === 5 && <Wand2 className="h-2 w-2 text-emerald-400/60" />}
                            {i % 8 === 6 && <Flame className="h-3 w-3 text-red-400/60" />}
                            {i % 8 === 7 && <Rocket className="h-2 w-2 text-orange-400/60" />}
                        </div>
                    ))}
                </div>

                {/* Дополнительные волновые эффекты */}
                <div className="absolute inset-0 opacity-30">
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-pulse"></div>
                    <div className="absolute bottom-0 left-0 w-full h-2 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 animate-pulse delay-1000"></div>
                    <div className="absolute left-0 top-0 w-2 h-full bg-gradient-to-b from-cyan-500 via-blue-500 to-purple-500 animate-pulse delay-2000"></div>
                    <div className="absolute right-0 top-0 w-2 h-full bg-gradient-to-b from-purple-500 via-pink-500 to-rose-500 animate-pulse delay-3000"></div>
                </div>
            </div>
            
            {/* Header с улучшенными эффектами */}
            <div className="relative z-10 px-4 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <button
                        onClick={onBack}
                        className="flex items-center space-x-2 bg-white/20 backdrop-blur-xl border-2 border-white/30 rounded-2xl px-6 py-3 hover:bg-white/30 transition-all duration-300 transform hover:scale-105 hover:rotate-1 shadow-2xl"
                    >
                        <ArrowLeft className="w-5 h-5 text-white drop-shadow-lg" />
                        <span className="text-white font-semibold drop-shadow-lg">{t('back')}</span>
                    </button>
                    
                    <div className="text-center">
                        <h1 className="text-3xl font-black mb-2">
                            <GradientText className="bg-gradient-to-r from-cyan-300 via-blue-300 to-purple-300 drop-shadow-2xl">
                                🚀 {t('documentAnalysis')}
                            </GradientText>
                        </h1>
                        <p className="text-lg text-blue-200 drop-shadow-xl font-medium">✨ {t('aiAnalysis')} ✨</p>
                    </div>
                    
                    <div className="w-20"></div>
                </div>
            </div>

            {/* Основной контент с невероятными эффектами */}
            <div className="relative z-10 px-4 pb-8">
                <div className="max-w-2xl mx-auto space-y-8">
                    
                    {/* СУПЕР ЭФФЕКТНАЯ ОБЛАСТЬ ЗАГРУЗКИ */}
                    <div className={`transform transition-all duration-1000 ${
                        animateIn ? 'translate-y-0 opacity-100 rotate-0' : 'translate-y-10 opacity-0 rotate-3'
                    }`}>
                        <div className={`relative overflow-hidden rounded-3xl border-4 border-dashed transition-all duration-700 shadow-2xl ${
                            isDragActive || magneticHover
                                ? 'border-cyan-400 bg-cyan-500/20 shadow-cyan-500/50 transform scale-105 rotate-1' 
                                : 'border-purple-400/60 bg-gradient-to-br from-purple-500/10 via-blue-500/10 to-pink-500/10 hover:border-purple-300 hover:scale-102 hover:-rotate-1'
                        }`}>
                            
                            {/* Анимированный фон области загрузки */}
                            <div className="absolute inset-0 opacity-40">
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-200/30 to-transparent transform -skew-x-12 animate-pulse"></div>
                                <div className="absolute inset-0 bg-gradient-to-l from-purple-200/20 via-transparent to-blue-200/20 transform skew-x-12 animate-pulse delay-500"></div>
                            </div>
                            
                            {/* Орбитальные элементы вокруг области загрузки */}
                            <div className="absolute inset-0 pointer-events-none">
                                {[...Array(20)].map((_, i) => (
                                    <div
                                        key={i}
                                        className="absolute animate-pulse opacity-70"
                                        style={{
                                            left: `${Math.random() * 100}%`,
                                            top: `${Math.random() * 100}%`,
                                            animationDelay: `${Math.random() * 3}s`,
                                            animationDuration: `${2 + Math.random() * 2}s`
                                        }}
                                    >
                                        {i % 4 === 0 && '✨'}
                                        {i % 4 === 1 && '⭐'}
                                        {i % 4 === 2 && '💎'}
                                        {i % 4 === 3 && '🚀'}
                                    </div>
                                ))}
                            </div>

                            <div 
                                {...getRootProps()}
                                className="relative z-10 p-12 cursor-pointer"
                                onMouseEnter={() => setMagneticHover(true)}
                                onMouseLeave={() => setMagneticHover(false)}
                            >
                                <input {...getInputProps()} />
                                <input 
                                    type="file"
                                    accept=".pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp,.txt"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                    id="file-input-analysis"
                                />
                                
                                {/* Анимированный прогресс-бар */}
                                {loading && uploadProgress > 0 && (
                                    <div className="absolute top-0 left-0 h-2 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 transition-all duration-500 rounded-t-3xl overflow-hidden" 
                                         style={{width: `${uploadProgress}%`}}>
                                        <div className="absolute inset-0 bg-gradient-to-r from-white/30 to-transparent animate-pulse"></div>
                                        <div className="absolute top-0 left-0 w-full h-full">
                                            {[...Array(10)].map((_, i) => (
                                                <div key={i} 
                                                     className="absolute top-0 w-1 h-full bg-white/40 animate-pulse"
                                                     style={{
                                                         left: `${i * 10}%`,
                                                         animationDelay: `${i * 0.1}s`
                                                     }}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}
                                
                                {loading ? (
                                    // СУПЕР ЭФФЕКТНАЯ АНИМАЦИЯ ЗАГРУЗКИ
                                    <div className="space-y-10 text-center">
                                        <div className="relative mx-auto w-48 h-48">
                                            {/* Множественные вращающиеся кольца */}
                                            <div className="absolute inset-0 border-4 border-cyan-300 rounded-full animate-spin opacity-80"></div>
                                            <div className="absolute inset-4 border-4 border-blue-400 rounded-full animate-spin reverse-spin opacity-70"></div>
                                            <div className="absolute inset-8 border-4 border-purple-500 rounded-full animate-spin opacity-60" style={{animationDuration: '0.8s'}}></div>
                                            <div className="absolute inset-12 border-4 border-pink-600 rounded-full animate-spin reverse-spin opacity-50" style={{animationDuration: '1.2s'}}></div>
                                            <div className="absolute inset-16 border-4 border-cyan-700 rounded-full animate-spin opacity-40" style={{animationDuration: '1.5s'}}></div>
                                            
                                            {/* Центральная анимированная иконка */}
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <div className="bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 rounded-full p-8 shadow-2xl animate-pulse">
                                                    <Bot className="h-16 w-16 text-white animate-bounce" />
                                                </div>
                                            </div>
                                            
                                            {/* Орбитальные элементы */}
                                            <div className="absolute inset-0 animate-spin" style={{animationDuration: '3s'}}>
                                                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                                    <Sparkles className="h-8 w-8 text-cyan-400 animate-pulse" />
                                                </div>
                                                <div className="absolute top-1/2 -right-4 transform -translate-y-1/2">
                                                    <Star className="h-6 w-6 text-blue-400 animate-pulse delay-500" />
                                                </div>
                                                <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2">
                                                    <Diamond className="h-10 w-10 text-purple-400 animate-pulse delay-1000" />
                                                </div>
                                                <div className="absolute top-1/2 -left-4 transform -translate-y-1/2">
                                                    <Gem className="h-8 w-8 text-pink-400 animate-pulse delay-1500" />
                                                </div>
                                            </div>
                                            
                                            {/* Дополнительные летающие элементы */}
                                            {[...Array(12)].map((_, i) => (
                                                <div key={i} 
                                                     className="absolute animate-bounce opacity-80"
                                                     style={{
                                                         left: `${20 + Math.random() * 60}%`,
                                                         top: `${20 + Math.random() * 60}%`,
                                                         animationDelay: `${Math.random() * 2}s`,
                                                         animationDuration: `${1 + Math.random()}s`
                                                     }}>
                                                    {i % 6 === 0 && <Rocket className="h-4 w-4 text-orange-400" />}
                                                    {i % 6 === 1 && <Crown className="h-3 w-3 text-yellow-400" />}
                                                    {i % 6 === 2 && <Wand2 className="h-4 w-4 text-emerald-400" />}
                                                    {i % 6 === 3 && <Flame className="h-3 w-3 text-red-400" />}
                                                    {i % 6 === 4 && <Shield className="h-4 w-4 text-teal-400" />}
                                                    {i % 6 === 5 && <Award className="h-3 w-3 text-violet-400" />}
                                                </div>
                                            ))}
                                        </div>
                                        
                                        <div className="space-y-6">
                                            <h3 className="text-4xl font-black bg-gradient-to-r from-cyan-300 via-blue-300 to-purple-300 bg-clip-text text-transparent animate-pulse drop-shadow-2xl">
                                                🚀 МАГИЯ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА
                                            </h3>
                                            
                                            <div className="bg-white/20 backdrop-blur-sm rounded-3xl p-8 border-2 border-cyan-300/30 shadow-2xl">
                                                <p className="text-2xl font-bold text-white animate-pulse drop-shadow-xl">
                                                    {processingStage}
                                                </p>
                                                <div className="mt-6 flex justify-center space-x-3">
                                                    {[1, 2, 3, 4, 5, 6].map((i) => (
                                                        <div 
                                                            key={i}
                                                            className="w-4 h-4 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full animate-bounce shadow-lg"
                                                            style={{ animationDelay: `${i * 0.2}s` }}
                                                        ></div>
                                                    ))}
                                                </div>
                                            </div>
                                            
                                            {/* Этапы обработки с красивыми иконками */}
                                            <div className="grid grid-cols-5 gap-4 max-w-lg mx-auto">
                                                {[
                                                    { icon: Bot, label: 'AI Сканер', color: 'from-cyan-500 to-blue-600' },
                                                    { icon: Eye, label: 'Распознавание', color: 'from-blue-500 to-purple-600' },
                                                    { icon: Cpu, label: 'Обработка', color: 'from-purple-500 to-pink-600' },
                                                    { icon: Wand2, label: 'Анализ', color: 'from-pink-500 to-red-600' },
                                                    { icon: Sparkles, label: 'Результат', color: 'from-red-500 to-orange-600' }
                                                ].map(({ icon: Icon, label, color }, index) => (
                                                    <div key={index} className="text-center">
                                                        <div className={`p-4 rounded-2xl transition-all duration-500 shadow-2xl transform hover:scale-110 ${
                                                            index < Math.floor(uploadProgress / 20) ? `bg-gradient-to-r ${color} text-white scale-110 animate-pulse` : 
                                                            'bg-gray-700 text-gray-400'
                                                        }`}>
                                                            <Icon className="h-6 w-6 mx-auto" />
                                                        </div>
                                                        <p className="text-xs font-bold mt-2 text-gray-300 drop-shadow-lg">{label}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ) : selectedFile ? (
                                    // СУПЕР КРАСИВОЕ ОТОБРАЖЕНИЕ ВЫБРАННОГО ФАЙЛА
                                    <div className="space-y-8 text-center">
                                        <div className="mx-auto w-40 h-40 bg-gradient-to-r from-emerald-400 via-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-2xl animate-pulse transform hover:scale-110 transition-transform duration-300">
                                            <CheckCircle className="h-20 w-20 text-white drop-shadow-2xl" />
                                        </div>
                                        
                                        <div className="space-y-6">
                                            <h3 className="text-4xl font-black bg-gradient-to-r from-emerald-300 via-cyan-300 to-blue-300 bg-clip-text text-transparent drop-shadow-2xl">
                                                ✅ ФАЙЛ ГОТОВ К МАГИЧЕСКОМУ АНАЛИЗУ
                                            </h3>
                                            
                                            <div className="bg-white/20 backdrop-blur-sm rounded-3xl p-8 border-2 border-emerald-300/30 max-w-md mx-auto shadow-2xl">
                                                <div className="flex items-center space-x-6">
                                                    <div className="flex-shrink-0 text-emerald-300 animate-bounce">
                                                        {getFileIcon(selectedFile)}
                                                    </div>
                                                    <div className="flex-grow text-left">
                                                        <p className="font-black text-white truncate text-xl drop-shadow-lg">
                                                            {selectedFile.name}
                                                        </p>
                                                        <p className="text-lg text-emerald-200 font-semibold drop-shadow-lg">
                                                            {formatFileSize(selectedFile.size)}
                                                        </p>
                                                    </div>
                                                </div>
                                                
                                                {filePreview && (
                                                    <div className="mt-8">
                                                        <img 
                                                            src={filePreview} 
                                                            alt="Preview" 
                                                            className="max-w-full max-h-48 rounded-2xl shadow-2xl mx-auto border-4 border-emerald-300/50"
                                                        />
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    // Упрощенное состояние по умолчанию
                                    <div className="space-y-8 text-center">
                                        <div className="relative mx-auto w-32 h-32">
                                            {/* Основной круг с простым градиентом */}
                                            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full shadow-xl"></div>
                                            <div className="absolute inset-2 bg-slate-900 rounded-full flex items-center justify-center">
                                                <Upload className="h-16 w-16 text-blue-400" />
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-6">
                                            <h3 className="text-2xl font-bold text-white">
                                                Загрузить документ для анализа
                                            </h3>
                                            
                                            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-6 border border-purple-300/30">
                                                <p className="text-lg text-white mb-6 font-medium">
                                                    {isDragActive 
                                                        ? "Отпустите файл для анализа" 
                                                        : "Перетащите файл сюда или нажмите для выбора"
                                                    }
                                                </p>
                                                
                                                <div className="grid grid-cols-3 gap-4 max-w-sm mx-auto mb-6">
                                                    <div className="flex flex-col items-center space-y-2 p-4 bg-blue-500/20 rounded-xl">
                                                        <FileText className="h-8 w-8 text-blue-300" />
                                                        <span className="text-sm font-medium text-blue-200">PDF</span>
                                                    </div>
                                                    <div className="flex flex-col items-center space-y-2 p-4 bg-purple-500/20 rounded-xl">
                                                        <Image className="h-8 w-8 text-purple-300" />
                                                        <span className="text-sm font-medium text-purple-200">Фото</span>
                                                    </div>
                                                    <div className="flex flex-col items-center space-y-2 p-4 bg-cyan-500/20 rounded-xl">
                                                        <Camera className="h-8 w-8 text-cyan-300" />
                                                        <span className="text-sm font-medium text-cyan-200">Скан</span>
                                                    </div>
                                                </div>
                                                
                                                <button
                                                    type="button"
                                                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-colors flex items-center space-x-3 mx-auto font-bold"
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
                                                </button>
                                            </div>
                                            
                                            <div className="bg-gradient-to-r from-purple-500/20 to-cyan-500/20 rounded-2xl p-6 border-2 border-purple-300/30 shadow-xl">
                                                <p className="text-lg text-white font-bold flex items-center justify-center space-x-3 drop-shadow-lg">
                                                    <Shield className="h-6 w-6 text-emerald-400" />
                                                    <span>Максимальный размер файла: 10MB</span>
                                                    <Shield className="h-6 w-6 text-emerald-400" />
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                
                                {error && (
                                    <div className="mt-8 p-6 bg-red-500/20 border-2 border-red-400/30 rounded-2xl shadow-2xl">
                                        <div className="flex items-center space-x-3 text-red-300">
                                            <AlertCircle className="h-6 w-6 animate-pulse" />
                                            <span className="font-bold text-lg">{error}</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                            
                            {/* Декоративные элементы по краям */}
                            <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 opacity-60 animate-pulse rounded-b-3xl"></div>
                            <div className="absolute bottom-0 left-0 right-0 h-2 bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 rounded-b-3xl"></div>
                        </div>
                    </div>

                    {/* Текущая информация о файле с эффектами */}
                    {currentFile && !loading && (
                        <div className={`transform transition-all duration-700 ${
                            animateIn ? 'translate-y-0 opacity-100' : 'translate-y-5 opacity-0'
                        }`}>
                            <div className="relative overflow-hidden bg-white/20 backdrop-blur-xl border-2 border-emerald-300/30 rounded-3xl p-6 shadow-2xl">
                                <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-blue-500/10"></div>
                                
                                <div className="relative flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-16 h-16 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl animate-pulse">
                                            {getFileIcon(currentFile)}
                                        </div>
                                        <div>
                                            <p className="text-white font-bold text-xl truncate max-w-48 drop-shadow-lg">{currentFile.name}</p>
                                            <p className="text-emerald-200 text-lg font-semibold drop-shadow-lg">{(currentFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={resetAnalysis}
                                        className="p-4 bg-white/20 hover:bg-white/30 rounded-2xl transition-all duration-300 transform hover:scale-110 hover:rotate-180 shadow-xl border border-white/30"
                                    >
                                        <RefreshCw className="w-6 h-6 text-white drop-shadow-lg" />
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