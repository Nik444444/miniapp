import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { User, Key, Shield, CheckCircle, XCircle, Save, X, Zap, Globe } from 'lucide-react';

const UserProfile = ({ onClose }) => {
    const { user, saveApiKeys } = useContext(AuthContext);
    const { currentLanguage, changeLanguage, t } = useLanguage();
    const [apiKeys, setApiKeys] = useState({
        api_key_1: '',
        api_key_2: '',
        api_key_3: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [languageLoading, setLanguageLoading] = useState(false);

    const languages = [
        { code: 'uk', name: 'Українська', flag: '🇺🇦' },
        { code: 'ru', name: 'Русский', flag: '🇷🇺' },
        { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
        { code: 'en', name: 'English', flag: '🇬🇧' }
    ];

    const handleLanguageChange = async (languageCode) => {
        setLanguageLoading(true);
        try {
            await changeLanguage(languageCode);
            setMessage(t('languageChanged'));
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            setMessage('Ошибка при смене языка');
        } finally {
            setLanguageLoading(false);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        setMessage('');

        // Фильтруем только непустые ключи
        const keysToSave = Object.fromEntries(
            Object.entries(apiKeys).filter(([_, value]) => value.trim() !== '')
        );

        if (Object.keys(keysToSave).length === 0) {
            setMessage('Введите хотя бы один API ключ');
            setLoading(false);
            return;
        }

        const result = await saveApiKeys(keysToSave);
        
        if (result.success) {
            setMessage(result.message);
            setApiKeys({ api_key_1: '', api_key_2: '', api_key_3: '' });
        } else {
            setMessage(result.error);
        }
        
        setLoading(false);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-t-xl">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="h-16 w-16 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
                                {user.picture ? (
                                    <img 
                                        src={user.picture} 
                                        alt={user.name} 
                                        className="h-14 w-14 rounded-full"
                                    />
                                ) : (
                                    <User className="h-8 w-8 text-white" />
                                )}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold">{user.name}</h2>
                                <p className="text-indigo-100">{user.email}</p>
                            </div>
                        </div>
                        <button 
                            onClick={onClose}
                            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                        >
                            <X className="h-6 w-6" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Profile Information */}
                    <div className="bg-gray-50 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                            <Shield className="h-5 w-5 mr-2 text-indigo-500" />
                            Информация о профиле
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-600">Провайдер аутентификации</p>
                                <p className="font-medium text-gray-900">{user.oauth_provider}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Дата регистрации</p>
                                <p className="font-medium text-gray-900">{formatDate(user.created_at)}</p>
                            </div>
                            {user.last_login && (
                                <div>
                                    <p className="text-sm text-gray-600">Последний вход</p>
                                    <p className="font-medium text-gray-900">{formatDate(user.last_login)}</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Language Settings */}
                    <div className="bg-white border rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                            <Globe className="h-5 w-5 mr-2 text-indigo-500" />
                            {t('languageSelection')}
                        </h3>
                        <p className="text-sm text-gray-600 mb-4">
                            {t('languageSelectionDescription')}
                        </p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {languages.map((language) => (
                                <button
                                    key={language.code}
                                    onClick={() => handleLanguageChange(language.code)}
                                    disabled={languageLoading}
                                    className={`p-3 rounded-lg border transition-all duration-200 ${
                                        currentLanguage === language.code
                                            ? 'bg-indigo-50 border-indigo-500 text-indigo-700'
                                            : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                                    } ${languageLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    <div className="text-center">
                                        <div className="text-2xl mb-1">{language.flag}</div>
                                        <div className="text-sm font-medium">{language.name}</div>
                                        {currentLanguage === language.code && (
                                            <div className="text-xs text-indigo-600 mt-1">✓ Активен</div>
                                        )}
                                    </div>
                                </button>
                            ))}
                        </div>
                        {user.preferred_language && (
                            <div className="mt-3 text-sm text-gray-600">
                                Текущий язык профиля: {user.preferred_language}
                            </div>
                        )}
                    </div>

                    {/* Add API Keys */}
                    <div className="bg-white border rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">
                            Добавить / Обновить API ключи
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    API ключ 1
                                </label>
                                <input
                                    type="password"
                                    placeholder="Введите API ключ"
                                    value={apiKeys.api_key_1}
                                    onChange={(e) => setApiKeys({...apiKeys, api_key_1: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    API ключ 2
                                </label>
                                <input
                                    type="password"
                                    placeholder="Введите API ключ"
                                    value={apiKeys.api_key_2}
                                    onChange={(e) => setApiKeys({...apiKeys, api_key_2: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    API ключ 3
                                </label>
                                <input
                                    type="password"
                                    placeholder="Введите API ключ"
                                    value={apiKeys.api_key_3}
                                    onChange={(e) => setApiKeys({...apiKeys, api_key_3: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </div>
                        </div>

                        {message && (
                            <div className={`mt-4 p-3 rounded-md ${
                                message.includes('успешно') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                            }`}>
                                {message}
                            </div>
                        )}

                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={handleSave}
                                disabled={loading}
                                className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                            >
                                {loading ? (
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                ) : (
                                    <Save className="h-4 w-4 mr-2" />
                                )}
                                {loading ? 'Сохранение...' : 'Сохранить'}
                            </button>
                        </div>
                    </div>

                    {/* Instructions */}
                    <div className="bg-blue-50 rounded-lg p-4">
                        <h4 className="font-semibold text-blue-900 mb-2">Как получить API ключи:</h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                            <li>• Посетите официальные сайты AI провайдеров</li>
                            <li>• Зарегистрируйтесь и создайте API ключи</li>
                            <li>• Добавьте ключи в соответствующие поля выше</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;