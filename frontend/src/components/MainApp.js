import React, { useContext, useState, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import UserProfile from './UserProfile';
import AnalysisResult from './AnalysisResult';
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
    X
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const MainApp = () => {
    const { user, logout } = useContext(AuthContext);
    const [showProfile, setShowProfile] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);
    const [showAnalysisResult, setShowAnalysisResult] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const [history, setHistory] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    // Drag and drop configuration
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            analyzeFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
            'application/pdf': ['.pdf']
        },
        maxFiles: 1
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
                    'Content-Type': 'multipart/form-data'
                }
            });

            setAnalysisResult(response.data);
            setShowAnalysisResult(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка анализа файла');
        } finally {
            setLoading(false);
        }
    };

    const loadHistory = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/analysis-history`);
            setHistory(response.data.analyses);
        } catch (err) {
            console.error('Ошибка загрузки истории:', err);
        }
    };

    const handleShowHistory = () => {
        if (!showHistory) {
            loadHistory();
        }
        setShowHistory(!showHistory);
    };


    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center space-x-4">
                            <div className="h-10 w-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                                <FileText className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-gray-900">German Letter AI</h1>
                                <p className="text-sm text-gray-500">Анализ немецких писем</p>
                            </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={handleShowHistory}
                                className="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-indigo-600 transition-colors"
                            >
                                <History className="h-5 w-5" />
                                <span>История</span>
                            </button>
                            
                            <button
                                onClick={() => setShowProfile(true)}
                                className="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-indigo-600 transition-colors"
                            >
                                <Settings className="h-5 w-5" />
                                <span>Настройки</span>
                            </button>

                            <div className="flex items-center space-x-3">
                                <div className="text-right">
                                    <p className="text-sm font-medium text-gray-900">{user.name}</p>
                                    <p className="text-xs text-gray-500">{user.email}</p>
                                </div>
                                {user.picture && (
                                    <img 
                                        src={user.picture} 
                                        alt={user.name} 
                                        className="h-8 w-8 rounded-full"
                                    />
                                )}
                                <button
                                    onClick={logout}
                                    className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                                >
                                    <LogOut className="h-5 w-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* File Upload */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                                <Upload className="h-5 w-5 mr-2 text-indigo-500" />
                                Загрузить документ
                            </h2>
                            
                            <div
                                {...getRootProps()}
                                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                                    isDragActive
                                        ? 'border-indigo-500 bg-indigo-50'
                                        : 'border-gray-300 hover:border-indigo-400'
                                }`}
                            >
                                <input {...getInputProps()} />
                                <div className="space-y-4">
                                    <div className="flex justify-center">
                                        <div className="bg-indigo-100 rounded-full p-3">
                                            <Upload className="h-8 w-8 text-indigo-600" />
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-lg font-medium text-gray-900">
                                            {isDragActive ? 'Отпустите файл здесь' : 'Перетащите файл сюда'}
                                        </p>
                                        <p className="text-gray-600">или нажмите для выбора</p>
                                    </div>
                                    <div className="flex justify-center space-x-4 text-sm text-gray-500">
                                        <span className="flex items-center">
                                            <FileText className="h-4 w-4 mr-1" />
                                            PDF
                                        </span>
                                        <span className="flex items-center">
                                            <Image className="h-4 w-4 mr-1" />
                                            JPG, PNG
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Loading State */}
                        {loading && (
                            <div className="bg-white rounded-xl shadow-sm p-6 text-center">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                                <p className="text-gray-600">Анализирую документ...</p>
                            </div>
                        )}

                        {/* Error */}
                        {error && (
                            <div className="bg-red-50 rounded-xl p-6">
                                <div className="flex items-center space-x-2">
                                    <AlertCircle className="h-5 w-5 text-red-600" />
                                    <p className="text-red-700">{error}</p>
                                </div>
                            </div>
                        )}

                        {/* Success Message */}
                        {analysisResult && !showAnalysisResult && (
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
                                <div className="flex items-center space-x-3">
                                    <div className="p-2 bg-green-500 rounded-full">
                                        <CheckCircle className="h-6 w-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-lg font-semibold text-green-900">
                                            Анализ завершен успешно!
                                        </h3>
                                        <p className="text-green-700">
                                            Файл "{analysisResult.file_name}" обработан успешно
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowAnalysisResult(true)}
                                        className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
                                    >
                                        Показать результат
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* API Status */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Статус</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-700">Gemini</span>
                                    {user.has_gemini_api_key ? (
                                        <CheckCircle className="h-5 w-5 text-green-500" />
                                    ) : (
                                        <AlertCircle className="h-5 w-5 text-red-500" />
                                    )}
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-700">OpenAI</span>
                                    {user.has_openai_api_key ? (
                                        <CheckCircle className="h-5 w-5 text-green-500" />
                                    ) : (
                                        <AlertCircle className="h-5 w-5 text-red-500" />
                                    )}
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm text-gray-700">Anthropic</span>
                                    {user.has_anthropic_api_key ? (
                                        <CheckCircle className="h-5 w-5 text-green-500" />
                                    ) : (
                                        <AlertCircle className="h-5 w-5 text-red-500" />
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-white rounded-xl shadow-sm p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => setShowProfile(true)}
                                    className="w-full flex items-center space-x-2 px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                                >
                                    <User className="h-4 w-4" />
                                    <span>Настройки профиля</span>
                                </button>
                                <button
                                    onClick={handleShowHistory}
                                    className="w-full flex items-center space-x-2 px-3 py-2 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                                >
                                    <History className="h-4 w-4" />
                                    <span>История анализов</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* History Modal */}
                {showHistory && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                            <div className="p-6 border-b">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-semibold text-gray-900">История анализов</h2>
                                    <button
                                        onClick={() => setShowHistory(false)}
                                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        <X className="h-5 w-5 text-gray-500" />
                                    </button>
                                </div>
                            </div>
                            
                            <div className="p-6">
                                {history.length === 0 ? (
                                    <div className="text-center py-8">
                                        <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                        <p className="text-gray-500">История анализов пуста</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {history.map((item, index) => (
                                            <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="font-medium text-gray-900">{item.file_name}</span>
                                                    <span className="text-sm text-gray-500">{formatDate(item.timestamp)}</span>
                                                </div>
                                                <div className="flex items-center space-x-4 text-sm text-gray-600">
                                                    <span>Тип: {item.file_type}</span>
                                                    <span>Язык: {item.analysis_language}</span>
                                                    <span>AI-анализ</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Profile Modal */}
            {showProfile && (
                <UserProfile onClose={() => setShowProfile(false)} />
            )}

            {/* Analysis Result Modal */}
            {showAnalysisResult && analysisResult && (
                <AnalysisResult 
                    analysisResult={analysisResult} 
                    onClose={() => setShowAnalysisResult(false)} 
                />
            )}
        </div>
    );
};

export default MainApp;