import React, { useState } from 'react';
import { Zap, ExternalLink, CheckCircle, XCircle, Copy } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const QuickGeminiSetup = ({ onSuccess, onClose }) => {
    const [apiKey, setApiKey] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [step, setStep] = useState(1);

    const handleQuickSetup = async () => {
        if (!apiKey.trim()) {
            setError('Введите API ключ');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${BACKEND_URL}/api/quick-gemini-setup`, {
                api_key: apiKey
            });

            if (response.data.status === 'success') {
                onSuccess(response.data.message);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка при настройке Gemini API');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-500 to-blue-600 text-white p-6 rounded-t-2xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="h-12 w-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                                <Zap className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold">Подключить Gemini одним нажатием</h2>
                                <p className="text-purple-100 text-sm">Быстрая настройка за 2 минуты</p>
                            </div>
                        </div>
                        <button 
                            onClick={onClose}
                            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                        >
                            <XCircle className="h-6 w-6" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {step === 1 && (
                        <div className="space-y-4">
                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4">
                                <h3 className="font-semibold text-gray-900 mb-2">Шаг 1: Получите API ключ</h3>
                                <p className="text-sm text-gray-600 mb-3">
                                    Получите бесплатный API ключ от Google для использования Gemini AI
                                </p>
                                <div className="flex items-center space-x-2 mb-3">
                                    <span className="text-sm text-gray-600">Перейдите на:</span>
                                    <code className="px-2 py-1 bg-gray-100 rounded text-sm font-mono">
                                        ai.google.dev
                                    </code>
                                    <button
                                        onClick={() => copyToClipboard('https://ai.google.dev')}
                                        className="p-1 hover:bg-gray-200 rounded"
                                    >
                                        <Copy className="h-4 w-4 text-gray-500" />
                                    </button>
                                </div>
                                <a
                                    href="https://ai.google.dev"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    <ExternalLink className="h-4 w-4" />
                                    <span>Открыть Google AI Studio</span>
                                </a>
                            </div>

                            <div className="bg-yellow-50 rounded-xl p-4">
                                <h4 className="font-semibold text-yellow-800 mb-2">Инструкция:</h4>
                                <ol className="text-sm text-yellow-700 space-y-1">
                                    <li>1. Нажмите кнопку "Get API key"</li>
                                    <li>2. Войдите в Google аккаунт</li>
                                    <li>3. Создайте новый проект или выберите существующий</li>
                                    <li>4. Нажмите "Create API key"</li>
                                    <li>5. Скопируйте полученный ключ</li>
                                </ol>
                            </div>

                            <div className="flex justify-end">
                                <button
                                    onClick={() => setStep(2)}
                                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                                >
                                    У меня есть API ключ
                                </button>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-4">
                            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-4">
                                <h3 className="font-semibold text-gray-900 mb-2">Шаг 2: Введите API ключ</h3>
                                <p className="text-sm text-gray-600 mb-3">
                                    Вставьте скопированный API ключ в поле ниже
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Gemini API Key
                                </label>
                                <input
                                    type="password"
                                    placeholder="Вставьте ваш Gemini API ключ"
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                    autoFocus
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Формат: AIza...
                                </p>
                            </div>

                            {error && (
                                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                    <div className="flex items-center space-x-2">
                                        <XCircle className="h-4 w-4 text-red-500" />
                                        <span className="text-red-700 text-sm">{error}</span>
                                    </div>
                                </div>
                            )}

                            <div className="flex space-x-3">
                                <button
                                    onClick={() => setStep(1)}
                                    className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                                >
                                    Назад
                                </button>
                                <button
                                    onClick={handleQuickSetup}
                                    disabled={loading || !apiKey.trim()}
                                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    {loading ? (
                                        <>
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                            <span>Подключаю...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Zap className="h-4 w-4" />
                                            <span>Подключить Gemini</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Features */}
                    <div className="bg-gray-50 rounded-xl p-4">
                        <h4 className="font-semibold text-gray-900 mb-3">После подключения вы сможете:</h4>
                        <ul className="space-y-2 text-sm text-gray-700">
                            <li className="flex items-center space-x-2">
                                <CheckCircle className="h-4 w-4 text-green-500" />
                                <span>Анализировать документы с высокой точностью</span>
                            </li>
                            <li className="flex items-center space-x-2">
                                <CheckCircle className="h-4 w-4 text-green-500" />
                                <span>Обрабатывать изображения и PDF файлы</span>
                            </li>
                            <li className="flex items-center space-x-2">
                                <CheckCircle className="h-4 w-4 text-green-500" />
                                <span>Получать анализ на 3 языках</span>
                            </li>
                            <li className="flex items-center space-x-2">
                                <CheckCircle className="h-4 w-4 text-green-500" />
                                <span>Сохранять историю анализов</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QuickGeminiSetup;