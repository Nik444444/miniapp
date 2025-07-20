import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
    Upload, 
    FileText, 
    Image, 
    File, 
    Sparkles, 
    Wand2,
    Zap,
    Crown,
    Diamond,
    Gem,
    Star,
    Heart,
    Flame,
    Rocket,
    Palette,
    Eye,
    Globe,
    Cpu,
    Bot,
    Activity,
    TrendingUp,
    ArrowRight,
    CheckCircle,
    AlertCircle,
    Clock,
    Target,
    Shield,
    Award,
    Trophy,
    Medal
} from 'lucide-react';

const SpectacularDocumentAnalysis = ({ onFileSelect, loading, error, apiKeyConfigured }) => {
    const [dragActive, setDragActive] = useState(false);
    const [animateIn, setAnimateIn] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [filePreview, setFilePreview] = useState(null);
    const [processingStage, setProcessingStage] = useState('');

    useEffect(() => {
        const timer = setTimeout(() => setAnimateIn(true), 300);
        return () => clearTimeout(timer);
    }, []);

    // Simulate processing stages
    useEffect(() => {
        if (loading) {
            const stages = [
                'Анализ документа...',
                'Извлечение текста...',
                'Обработка содержимого...',
                'Создание анализа...',
                'Финализация результатов...'
            ];
            let currentStage = 0;
            
            const interval = setInterval(() => {
                setProcessingStage(stages[currentStage]);
                currentStage = (currentStage + 1) % stages.length;
            }, 1000);
            
            return () => clearInterval(interval);
        } else {
            setProcessingStage('');
        }
    }, [loading]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop: (acceptedFiles) => {
            const file = acceptedFiles[0];
            if (file) {
                setSelectedFile(file);
                
                // Create preview for images
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (e) => setFilePreview(e.target.result);
                    reader.readAsDataURL(file);
                } else {
                    setFilePreview(null);
                }
                
                onFileSelect(file);
            }
        },
        accept: {
            'application/pdf': ['.pdf'],
            'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
            'text/*': ['.txt']
        },
        maxFiles: 1,
        maxSize: 10485760, // 10MB
        disabled: loading || !apiKeyConfigured
    });

    const getFileIcon = (file) => {
        if (!file) return <FileText className="h-12 w-12" />;
        
        if (file.type.startsWith('image/')) {
            return <Image className="h-12 w-12" />;
        } else if (file.type === 'application/pdf') {
            return <FileText className="h-12 w-12" />;
        } else {
            return <File className="h-12 w-12" />;
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    if (!apiKeyConfigured) {
        return (
            <div className={`relative overflow-hidden rounded-3xl border-2 border-dashed border-gray-300 p-12 text-center transition-all duration-1000 ${
                animateIn ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
            }`}>
                {/* Animated Background */}
                <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 opacity-60"></div>
                
                {/* Floating Elements */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-4 right-4 animate-bounce">
                        <Shield className="h-8 w-8 text-blue-400" />
                    </div>
                    <div className="absolute bottom-4 left-4 animate-pulse">
                        <Star className="h-6 w-6 text-indigo-400" />
                    </div>
                </div>
                
                <div className="relative z-10 space-y-6">
                    <div className="mx-auto w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-2xl">
                        <Bot className="h-12 w-12 text-white" />
                    </div>
                    
                    <div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">
                            Настройка API ключа
                        </h3>
                        <p className="text-gray-600 text-lg">
                            Для начала анализа документов необходимо настроить API ключ
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`relative overflow-hidden rounded-3xl border-4 border-dashed transition-all duration-1000 ${
            animateIn ? 'scale-100 opacity-100 rotate-0' : 'scale-95 opacity-0 rotate-1'
        } ${
            isDragActive || dragActive 
                ? 'border-purple-500 bg-purple-50 shadow-2xl shadow-purple-500/50 transform scale-105' 
                : 'border-gray-300 bg-gradient-to-br from-white via-blue-50 to-purple-50'
        } ${loading ? 'pointer-events-none' : 'cursor-pointer hover:shadow-2xl hover:shadow-purple-500/30 hover:border-purple-400 hover:scale-105 hover:rotate-1'}`}>
            
            {/* Ultra Spectacular Background Effects */}
            <div className="absolute inset-0 opacity-40">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-200/50 to-transparent transform -skew-x-12 animate-pulse"></div>
                <div className="absolute inset-0 bg-gradient-to-l from-blue-200/30 via-transparent to-pink-200/30 transform skew-x-12 animate-pulse" style={{animationDelay: '0.5s'}}></div>
            </div>
            
            {/* Cosmic Particles */}
            <div className="absolute inset-0 pointer-events-none">
                {[...Array(40)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute animate-pulse"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 3}s`,
                            animationDuration: `${2 + Math.random() * 3}s`
                        }}
                    >
                        {i % 5 === 0 && '✨'}
                        {i % 5 === 1 && '⭐'}
                        {i % 5 === 2 && '💎'}
                        {i % 5 === 3 && '🔥'}
                        {i % 5 === 4 && '💫'}
                    </div>
                ))}
            </div>
            
            {/* Ultra Animated Corner Elements */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-4 right-4 animate-bounce">
                    <Star className="h-10 w-10 text-purple-500" />
                </div>
                <div className="absolute top-6 right-20 animate-pulse" style={{animationDelay: '0.5s'}}>
                    <Zap className="h-8 w-8 text-blue-500" />
                </div>
                <div className="absolute bottom-4 left-4 animate-pulse" style={{animationDelay: '1s'}}>
                    <Star className="h-12 w-12 text-indigo-500" />
                </div>
                <div className="absolute bottom-6 left-20 animate-bounce" style={{animationDelay: '1.5s'}}>
                    <Diamond className="h-7 w-7 text-pink-500" />
                </div>
                <div className="absolute top-1/2 right-1/4 animate-ping" style={{animationDelay: '2s'}}>
                    <Crown className="h-6 w-6 text-purple-500" />
                </div>
                <div className="absolute bottom-1/3 left-1/4 animate-bounce" style={{animationDelay: '2.5s'}}>
                    <Flame className="h-8 w-8 text-cyan-500" />
                </div>
                <div className="absolute top-1/4 left-1/3 animate-pulse" style={{animationDelay: '3s'}}>
                    <Rocket className="h-7 w-7 text-emerald-500" />
                </div>
                <div className="absolute top-3/4 right-1/3 animate-bounce" style={{animationDelay: '3.5s'}}>
                    <Sparkles className="h-6 w-6 text-teal-500" />
                </div>
                <div className="absolute top-1/3 right-2/3 animate-ping" style={{animationDelay: '4s'}}>
                    <Gem className="h-5 w-5 text-violet-500" />
                </div>
            </div>

            <div {...getRootProps()} className="relative z-10 p-12">
                <input {...getInputProps()} />
                
                {loading ? (
                    // Ultra Spectacular Loading State
                    <div className="space-y-8 text-center">
                        <div className="relative mx-auto w-40 h-40">
                            {/* Multiple Rotating Cosmic Rings */}
                            <div className="absolute inset-0 border-4 border-purple-200 rounded-full animate-spin"></div>
                            <div className="absolute inset-2 border-4 border-blue-300 rounded-full animate-spin reverse-spin"></div>
                            <div className="absolute inset-4 border-4 border-pink-400 rounded-full animate-spin" style={{animationDuration: '0.8s'}}></div>
                            <div className="absolute inset-6 border-4 border-cyan-500 rounded-full animate-spin reverse-spin" style={{animationDuration: '1.2s'}}></div>
                            
                            {/* Ultra Center Icon */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 rounded-full p-6 shadow-2xl animate-pulse">
                                    <Bot className="h-12 w-12 text-white animate-bounce" />
                                </div>
                            </div>
                            
                            {/* Floating Elements Around */}
                            <div className="absolute -top-4 -right-4 animate-bounce" style={{animationDelay: '0.5s'}}>
                                <Sparkles className="h-6 w-6 text-purple-400" />
                            </div>
                            <div className="absolute -bottom-4 -left-4 animate-pulse" style={{animationDelay: '1s'}}>
                                <Star className="h-8 w-8 text-blue-400" />
                            </div>
                            <div className="absolute -top-4 -left-4 animate-bounce" style={{animationDelay: '1.5s'}}>
                                <Diamond className="h-7 w-7 text-pink-400" />
                            </div>
                            <div className="absolute -bottom-4 -right-4 animate-pulse" style={{animationDelay: '2s'}}>
                                <Gem className="h-6 w-6 text-cyan-400" />
                            </div>
                        </div>
                        
                        <div className="space-y-6">
                            <h3 className="text-3xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent animate-pulse">
                                🚀 МАГИЯ АНАЛИЗА В ПРОЦЕССЕ
                            </h3>
                            
                            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 border-2 border-purple-200 shadow-2xl">
                                <p className="text-xl font-bold text-gray-700 animate-pulse">
                                    {processingStage}
                                </p>
                                <div className="mt-4 flex justify-center space-x-2">
                                    {[1, 2, 3, 4, 5].map((i) => (
                                        <div 
                                            key={i}
                                            className="w-3 h-3 bg-gradient-to-r from-purple-500 to-blue-600 rounded-full animate-bounce"
                                            style={{ animationDelay: `${i * 0.1}s` }}
                                        ></div>
                                    ))}
                                </div>
                            </div>
                            
                            {/* Ultra Processing Steps */}
                            <div className="grid grid-cols-5 gap-4 max-w-lg mx-auto">
                                {[
                                    { icon: Bot, label: 'AI Сканер' },
                                    { icon: Eye, label: 'Распознавание' },
                                    { icon: Cpu, label: 'Обработка' },
                                    { icon: Wand2, label: 'Анализ' },
                                    { icon: Sparkles, label: 'Результат' }
                                ].map(({ icon: Icon, label }, index) => (
                                    <div key={index} className="text-center">
                                        <div className={`p-4 rounded-2xl transition-all duration-500 shadow-lg ${
                                            index < 3 ? 'bg-gradient-to-r from-purple-500 to-blue-600 text-white transform scale-110' : 
                                            'bg-gray-200 text-gray-400'
                                        }`}>
                                            <Icon className="h-6 w-6 mx-auto" />
                                        </div>
                                        <p className="text-xs font-semibold mt-2 text-gray-600">{label}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : selectedFile ? (
                    // Ultra File Selected State
                    <div className="space-y-8 text-center">
                        <div className="mx-auto w-32 h-32 bg-gradient-to-r from-emerald-400 via-green-500 to-teal-600 rounded-full flex items-center justify-center shadow-2xl animate-pulse transform hover:scale-110 transition-transform duration-300">
                            <CheckCircle className="h-16 w-16 text-white" />
                        </div>
                        
                        <div className="space-y-6">
                            <h3 className="text-3xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                                ✅ ФАЙЛ ГОТОВ К ВОЛШЕБНОМУ АНАЛИЗУ
                            </h3>
                            
                            <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 border-2 border-green-200 max-w-md mx-auto shadow-2xl">
                                <div className="flex items-center space-x-6">
                                    <div className="flex-shrink-0 text-green-600 animate-bounce">
                                        {getFileIcon(selectedFile)}
                                    </div>
                                    <div className="flex-grow text-left">
                                        <p className="font-black text-gray-900 truncate text-lg">
                                            {selectedFile.name}
                                        </p>
                                        <p className="text-sm text-gray-500 font-semibold">
                                            {formatFileSize(selectedFile.size)}
                                        </p>
                                    </div>
                                </div>
                                
                                {filePreview && (
                                    <div className="mt-6">
                                        <img 
                                            src={filePreview} 
                                            alt="Preview" 
                                            className="max-w-full max-h-40 rounded-xl shadow-xl mx-auto border-2 border-green-200"
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ) : (
                    // Ultra Default Upload State
                    <div className="space-y-10 text-center">
                        <div className="relative mx-auto w-40 h-40">
                            <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 rounded-full animate-pulse shadow-2xl"></div>
                            <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center shadow-inner">
                                <Upload className="h-20 w-20 text-transparent bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text animate-bounce" />
                            </div>
                            
                            {/* Orbiting Elements */}
                            <div className="absolute inset-0 animate-spin" style={{animationDuration: '10s'}}>
                                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                                    <Sparkles className="h-6 w-6 text-purple-500" />
                                </div>
                                <div className="absolute top-1/2 -right-2 transform -translate-y-1/2">
                                    <Star className="h-5 w-5 text-blue-500" />
                                </div>
                                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                                    <Diamond className="h-7 w-7 text-pink-500" />
                                </div>
                                <div className="absolute top-1/2 -left-2 transform -translate-y-1/2">
                                    <Gem className="h-6 w-6 text-cyan-500" />
                                </div>
                            </div>
                        </div>
                        
                        <div className="space-y-6">
                            <h3 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent">
                                🚀 МАГИЧЕСКИЙ АНАЛИЗ ДОКУМЕНТОВ
                            </h3>
                            
                            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 border-2 border-purple-200 shadow-2xl">
                                <p className="text-xl text-gray-700 mb-6 font-semibold">
                                    {isDragActive 
                                        ? "✨ Отпустите файл для начала волшебства ✨" 
                                        : "🎯 Перетащите файл сюда или нажмите для выбора"
                                    }
                                </p>
                                
                                <div className="grid grid-cols-3 gap-6 max-w-lg mx-auto">
                                    <div className="flex flex-col items-center space-y-4 p-6 bg-blue-50 rounded-2xl hover:bg-blue-100 transition-colors shadow-lg transform hover:scale-105">
                                        <FileText className="h-12 w-12 text-blue-600" />
                                        <span className="text-base font-black text-blue-900">PDF</span>
                                        <span className="text-xs text-blue-700">Документы</span>
                                    </div>
                                    <div className="flex flex-col items-center space-y-4 p-6 bg-purple-50 rounded-2xl hover:bg-purple-100 transition-colors shadow-lg transform hover:scale-105">
                                        <Image className="h-12 w-12 text-purple-600" />
                                        <span className="text-base font-black text-purple-900">Фото</span>
                                        <span className="text-xs text-purple-700">Изображения</span>
                                    </div>
                                    <div className="flex flex-col items-center space-y-4 p-6 bg-green-50 rounded-2xl hover:bg-green-100 transition-colors shadow-lg transform hover:scale-105">
                                        <File className="h-12 w-12 text-green-600" />
                                        <span className="text-base font-black text-green-900">Текст</span>
                                        <span className="text-xs text-green-700">Документы</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-4 border border-purple-200">
                                <p className="text-sm text-gray-600 font-semibold flex items-center justify-center space-x-2">
                                    <Shield className="h-4 w-4 text-green-500" />
                                    <span>Максимальный размер файла: 10MB</span>
                                    <Shield className="h-4 w-4 text-green-500" />
                                </p>
                            </div>
                        </div>
                    </div>
                )}
                
                {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl">
                        <div className="flex items-center space-x-2 text-red-700">
                            <AlertCircle className="h-5 w-5" />
                            <span className="font-medium">{error}</span>
                        </div>
                    </div>
                )}
            </div>
            
            {/* Bottom Ultra Decorative Elements */}
            <div className="absolute bottom-0 left-0 right-0 h-3 bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 opacity-60 animate-pulse"></div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400"></div>
        </div>
    );
};

export default SpectacularDocumentAnalysis;