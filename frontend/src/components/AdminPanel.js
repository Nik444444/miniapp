import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    Settings, 
    Edit3, 
    Save, 
    X, 
    Plus, 
    Trash2, 
    Eye, 
    EyeOff,
    Shield,
    Lock,
    Key,
    FileText,
    Globe,
    Layout,
    Type,
    AlertCircle,
    CheckCircle,
    Loader,
    Search,
    Filter,
    Crown,
    Sparkles,
    Wand2,
    Palette,
    Zap,
    Star,
    Heart,
    Rocket
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AdminPanel = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [texts, setTexts] = useState({});
    const [editingText, setEditingText] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [showAddModal, setShowAddModal] = useState(false);
    const [newText, setNewText] = useState({
        key_name: '',
        text_value: '',
        description: '',
        category: 'general'
    });

    const categoryIcons = {
        header: Crown,
        auth: Shield,
        main: Layout,
        sidebar: FileText,
        general: Type
    };

    const categoryColors = {
        header: 'from-purple-500 to-pink-500',
        auth: 'from-blue-500 to-indigo-500',
        main: 'from-green-500 to-teal-500',
        sidebar: 'from-orange-500 to-red-500',
        general: 'from-gray-500 to-gray-600'
    };

    const login = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await axios.post(`${BACKEND_URL}/api/admin/login`, {
                password: password
            });
            
            if (response.data.status === 'success') {
                setIsLoggedIn(true);
                setSuccess('Успешный вход в админку!');
                loadTexts();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка входа');
        } finally {
            setLoading(false);
        }
    };

    const loadTexts = async () => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/admin/texts`, {
                password: password
            });
            setTexts(response.data.texts);
        } catch (err) {
            setError('Ошибка загрузки текстов');
        }
    };

    const updateText = async (keyName, textValue, description) => {
        try {
            const response = await axios.put(`${BACKEND_URL}/api/admin/texts/${keyName}`, {
                text_value: textValue,
                description: description
            }, {
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    password: password
                }
            });

            if (response.data.status === 'success') {
                setSuccess('Текст обновлен!');
                loadTexts();
                setEditingText(null);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка обновления');
        }
    };

    const createText = async () => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/admin/texts/create`, {
                ...newText,
                password: password
            });

            if (response.data.status === 'success') {
                setSuccess('Новый текст создан!');
                loadTexts();
                setShowAddModal(false);
                setNewText({
                    key_name: '',
                    text_value: '',
                    description: '',
                    category: 'general'
                });
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка создания');
        }
    };

    const deleteText = async (keyName) => {
        if (!window.confirm('Удалить этот текст?')) return;

        try {
            const response = await axios.delete(`${BACKEND_URL}/api/admin/texts/${keyName}`, {
                data: {
                    password: password
                }
            });

            if (response.data.status === 'success') {
                setSuccess('Текст удален!');
                loadTexts();
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Ошибка удаления');
        }
    };

    const filteredTexts = () => {
        let filtered = {};
        
        Object.keys(texts).forEach(category => {
            if (selectedCategory === 'all' || selectedCategory === category) {
                const categoryTexts = texts[category].filter(text => 
                    text.key_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    text.text_value.toLowerCase().includes(searchTerm.toLowerCase())
                );
                if (categoryTexts.length > 0) {
                    filtered[category] = categoryTexts;
                }
            }
        });
        
        return filtered;
    };

    if (!isLoggedIn) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center p-4">
                {/* Анимированный фон */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
                    <div className="absolute bottom-1/4 left-1/3 w-48 h-48 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
                    
                    {/* Плавающие иконки */}
                    {[Shield, Lock, Key, Crown, Sparkles, Wand2, Palette, Zap, Star, Heart, Rocket].map((Icon, index) => (
                        <div
                            key={index}
                            className="absolute animate-float opacity-20"
                            style={{
                                left: `${10 + (index * 8)}%`,
                                top: `${20 + (index * 6)}%`,
                                animationDelay: `${index * 0.5}s`,
                                animationDuration: `${10 + (index * 2)}s`,
                            }}
                        >
                            <Icon className="w-6 h-6 text-white" />
                        </div>
                    ))}
                </div>

                <div className="relative z-10 max-w-md w-full">
                    <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
                        <div className="text-center mb-8">
                            <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                <Shield className="w-10 h-10 text-white" />
                            </div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                                Админская панель
                            </h1>
                            <p className="text-gray-600">
                                Управление текстами приложения
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                <input
                                    type={showPassword ? "text" : "password"}
                                    placeholder="Пароль админа"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                    onKeyPress={(e) => e.key === 'Enter' && login()}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>

                            <button
                                onClick={login}
                                disabled={loading || !password}
                                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg"
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center space-x-2">
                                        <Loader className="w-5 h-5 animate-spin" />
                                        <span>Вход...</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center space-x-2">
                                        <Key className="w-5 h-5" />
                                        <span>Войти</span>
                                    </div>
                                )}
                            </button>

                            {error && (
                                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                                    <div className="flex items-center space-x-2 text-red-700">
                                        <AlertCircle className="w-4 h-4" />
                                        <span className="text-sm">{error}</span>
                                    </div>
                                </div>
                            )}

                            {success && (
                                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                    <div className="flex items-center space-x-2 text-green-700">
                                        <CheckCircle className="w-4 h-4" />
                                        <span className="text-sm">{success}</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                                <Settings className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Админская панель</h1>
                                <p className="text-gray-600">Управление текстами приложения</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsLoggedIn(false)}
                            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                        >
                            Выйти
                        </button>
                    </div>
                </div>

                {/* Поиск и фильтры */}
                <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Поиск текстов..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            />
                        </div>
                        <div className="relative">
                            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="pl-12 pr-8 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            >
                                <option value="all">Все категории</option>
                                <option value="header">Заголовок</option>
                                <option value="auth">Авторизация</option>
                                <option value="main">Основное</option>
                                <option value="sidebar">Боковая панель</option>
                                <option value="general">Общее</option>
                            </select>
                        </div>
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="px-6 py-3 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-xl hover:from-green-600 hover:to-teal-600 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center space-x-2"
                        >
                            <Plus className="w-5 h-5" />
                            <span>Добавить текст</span>
                        </button>
                    </div>
                </div>

                {/* Уведомления */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
                        <div className="flex items-center space-x-2 text-red-700">
                            <AlertCircle className="w-5 h-5" />
                            <span>{error}</span>
                        </div>
                    </div>
                )}

                {success && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                        <div className="flex items-center space-x-2 text-green-700">
                            <CheckCircle className="w-5 h-5" />
                            <span>{success}</span>
                        </div>
                    </div>
                )}

                {/* Тексты по категориям */}
                <div className="space-y-6">
                    {Object.entries(filteredTexts()).map(([category, categoryTexts]) => {
                        const IconComponent = categoryIcons[category] || Type;
                        const colorClass = categoryColors[category] || 'from-gray-500 to-gray-600';

                        return (
                            <div key={category} className="bg-white rounded-2xl shadow-xl overflow-hidden">
                                <div className={`bg-gradient-to-r ${colorClass} p-6`}>
                                    <div className="flex items-center space-x-3 text-white">
                                        <IconComponent className="w-6 h-6" />
                                        <h2 className="text-xl font-bold capitalize">{category}</h2>
                                        <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                                            {categoryTexts.length} текстов
                                        </span>
                                    </div>
                                </div>
                                
                                <div className="p-6">
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        {categoryTexts.map((text) => (
                                            <div key={text.key_name} className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-shadow">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h3 className="font-semibold text-gray-900">{text.key_name}</h3>
                                                    <div className="flex items-center space-x-2">
                                                        <button
                                                            onClick={() => setEditingText(text)}
                                                            className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                                                        >
                                                            <Edit3 className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => deleteText(text.key_name)}
                                                            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </div>
                                                
                                                <div className="space-y-2">
                                                    <p className="text-sm text-gray-600 font-medium">Текст:</p>
                                                    <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                                                        {text.text_value}
                                                    </p>
                                                    
                                                    {text.description && (
                                                        <>
                                                            <p className="text-sm text-gray-600 font-medium">Описание:</p>
                                                            <p className="text-sm text-gray-500">
                                                                {text.description}
                                                            </p>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Модальное окно редактирования */}
                {editingText && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                            <div className="p-6 border-b border-gray-200">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-bold text-gray-900">
                                        Редактирование: {editingText.key_name}
                                    </h2>
                                    <button
                                        onClick={() => setEditingText(null)}
                                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                            
                            <div className="p-6">
                                <EditForm
                                    text={editingText}
                                    onSave={updateText}
                                    onCancel={() => setEditingText(null)}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Модальное окно добавления */}
                {showAddModal && (
                    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                            <div className="p-6 border-b border-gray-200">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-bold text-gray-900">
                                        Добавить новый текст
                                    </h2>
                                    <button
                                        onClick={() => setShowAddModal(false)}
                                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                            
                            <div className="p-6">
                                <AddForm
                                    newText={newText}
                                    setNewText={setNewText}
                                    onSave={createText}
                                    onCancel={() => setShowAddModal(false)}
                                />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Компонент формы редактирования
const EditForm = ({ text, onSave, onCancel }) => {
    const [textValue, setTextValue] = useState(text.text_value);
    const [description, setDescription] = useState(text.description || '');

    const handleSave = () => {
        onSave(text.key_name, textValue, description);
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Текст
                </label>
                <textarea
                    value={textValue}
                    onChange={(e) => setTextValue(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    rows="4"
                    placeholder="Введите текст..."
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Описание
                </label>
                <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Введите описание..."
                />
            </div>
            
            <div className="flex space-x-4">
                <button
                    onClick={handleSave}
                    className="flex-1 bg-gradient-to-r from-green-500 to-teal-500 text-white py-3 rounded-xl font-semibold hover:from-green-600 hover:to-teal-600 transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2"
                >
                    <Save className="w-5 h-5" />
                    <span>Сохранить</span>
                </button>
                <button
                    onClick={onCancel}
                    className="flex-1 bg-gray-500 text-white py-3 rounded-xl font-semibold hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2"
                >
                    <X className="w-5 h-5" />
                    <span>Отмена</span>
                </button>
            </div>
        </div>
    );
};

// Компонент формы добавления
const AddForm = ({ newText, setNewText, onSave, onCancel }) => {
    const handleSave = () => {
        if (newText.key_name && newText.text_value) {
            onSave();
        }
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ключ (key_name)
                </label>
                <input
                    type="text"
                    value={newText.key_name}
                    onChange={(e) => setNewText({...newText, key_name: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Введите ключ..."
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Текст
                </label>
                <textarea
                    value={newText.text_value}
                    onChange={(e) => setNewText({...newText, text_value: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    rows="4"
                    placeholder="Введите текст..."
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Описание
                </label>
                <input
                    type="text"
                    value={newText.description}
                    onChange={(e) => setNewText({...newText, description: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Введите описание..."
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Категория
                </label>
                <select
                    value={newText.category}
                    onChange={(e) => setNewText({...newText, category: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                    <option value="general">Общее</option>
                    <option value="header">Заголовок</option>
                    <option value="auth">Авторизация</option>
                    <option value="main">Основное</option>
                    <option value="sidebar">Боковая панель</option>
                </select>
            </div>
            
            <div className="flex space-x-4">
                <button
                    onClick={handleSave}
                    disabled={!newText.key_name || !newText.text_value}
                    className="flex-1 bg-gradient-to-r from-green-500 to-teal-500 text-white py-3 rounded-xl font-semibold hover:from-green-600 hover:to-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2"
                >
                    <Plus className="w-5 h-5" />
                    <span>Создать</span>
                </button>
                <button
                    onClick={onCancel}
                    className="flex-1 bg-gray-500 text-white py-3 rounded-xl font-semibold hover:bg-gray-600 transition-colors flex items-center justify-center space-x-2"
                >
                    <X className="w-5 h-5" />
                    <span>Отмена</span>
                </button>
            </div>
        </div>
    );
};

export default AdminPanel;