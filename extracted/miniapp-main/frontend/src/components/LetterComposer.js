import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    PencilSquareIcon,
    DocumentTextIcon, 
    SparklesIcon,
    ArrowDownTrayIcon,
    MagnifyingGlassIcon,
    ChatBubbleBottomCenterTextIcon,
    ClipboardDocumentListIcon,
    XMarkIcon,
    CheckIcon
} from '@heroicons/react/24/outline';

const LetterComposer = () => {
    const { user, token } = useContext(AuthContext);
    const [currentStep, setCurrentStep] = useState('method'); // method, categories, templates, compose, preview
    const [selectedMethod, setSelectedMethod] = useState(''); // template, custom
    const [categories, setCategories] = useState([]);
    const [templates, setTemplates] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    
    // Состояния для генерации писем
    const [userRequest, setUserRequest] = useState('');
    const [recipientType, setRecipientType] = useState('');
    const [templateData, setTemplateData] = useState({});
    const [senderInfo, setSenderInfo] = useState({
        name: user?.name || '',
        address: '',
        postal_code: '',
        city: '',
        phone: '',
        email: user?.email || ''
    });
    const [recipientInfo, setRecipientInfo] = useState({
        name: '',
        department: '',
        address: '',
        postal_code: '',
        city: ''
    });
    
    // Состояния результата
    const [generatedLetter, setGeneratedLetter] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    // Загрузка категорий при инициализации
    useEffect(() => {
        if (selectedMethod === 'template') {
            loadCategories();
        }
    }, [selectedMethod]);

    const loadCategories = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/letter-categories`);
            const data = await response.json();
            if (data.status === 'success') {
                setCategories(data.categories);
            }
        } catch (error) {
            console.error('Ошибка загрузки категорий:', error);
            setError('Ошибка загрузки категорий шаблонов');
        }
    };

    const loadTemplates = async (categoryKey) => {
        try {
            const response = await fetch(`${backendUrl}/api/letter-templates/${categoryKey}`);
            const data = await response.json();
            if (data.status === 'success') {
                setTemplates(data.templates);
                setSelectedCategory(categoryKey);
                setCurrentStep('templates');
            }
        } catch (error) {
            console.error('Ошибка загрузки шаблонов:', error);
            setError('Ошибка загрузки шаблонов');
        }
    };

    const loadTemplate = async (categoryKey, templateKey) => {
        try {
            const response = await fetch(`${backendUrl}/api/letter-template/${categoryKey}/${templateKey}`);
            const data = await response.json();
            if (data.status === 'success') {
                setSelectedTemplate(data.template);
                // Инициализируем поля для шаблона
                const initialData = {};
                data.template.variables.forEach(variable => {
                    initialData[variable] = '';
                });
                setTemplateData(initialData);
                setCurrentStep('compose');
            }
        } catch (error) {
            console.error('Ошибка загрузки шаблона:', error);
            setError('Ошибка загрузки шаблона');
        }
    };

    const generateCustomLetter = async () => {
        if (!userRequest.trim() || !recipientType.trim()) {
            setError('Пожалуйста, заполните описание письма и тип получателя');
            return;
        }

        setIsGenerating(true);
        setError('');

        try {
            const response = await fetch(`${backendUrl}/api/generate-letter`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_request: userRequest,
                    recipient_type: recipientType,
                    sender_info: senderInfo,
                    recipient_info: recipientInfo,
                    include_translation: true
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                setGeneratedLetter(data.letter);
                setCurrentStep('preview');
            } else {
                setError(data.error || 'Ошибка генерации письма');
            }
        } catch (error) {
            console.error('Ошибка генерации письма:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setIsGenerating(false);
        }
    };

    const generateTemplateLetter = async () => {
        if (!selectedTemplate) {
            setError('Шаблон не выбран');
            return;
        }

        // Проверяем заполненность обязательных полей
        const emptyFields = selectedTemplate.variables.filter(variable => 
            !templateData[variable] || !templateData[variable].trim()
        );

        if (emptyFields.length > 0) {
            setError(`Пожалуйста, заполните все поля: ${emptyFields.join(', ')}`);
            return;
        }

        setIsGenerating(true);
        setError('');

        try {
            const response = await fetch(`${backendUrl}/api/generate-letter-template`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    template_category: selectedTemplate.category,
                    template_key: selectedTemplate.key,
                    user_data: templateData,
                    sender_info: senderInfo,
                    recipient_info: recipientInfo,
                    include_translation: true
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                setGeneratedLetter(data.letter);
                setCurrentStep('preview');
            } else {
                setError(data.error || 'Ошибка генерации письма');
            }
        } catch (error) {
            console.error('Ошибка генерации письма из шаблона:', error);
            setError('Ошибка подключения к серверу');
        } finally {
            setIsGenerating(false);
        }
    };

    const downloadPDF = async () => {
        if (!generatedLetter) return;

        try {
            // Сначала сохраняем письмо
            const saveResponse = await fetch(`${backendUrl}/api/save-letter`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title: generatedLetter.subject || 'Официальное письмо',
                    content: generatedLetter.content,
                    content_german: generatedLetter.content,
                    translation: generatedLetter.translation,
                    translation_language: generatedLetter.translation_language,
                    subject: generatedLetter.subject,
                    recipient_type: recipientType,
                    template_category: selectedTemplate?.category,
                    template_key: selectedTemplate?.key,
                    letter_type: selectedMethod === 'template' ? 'template' : 'custom',
                    generation_method: selectedMethod === 'template' ? 'template_based' : 'ai_custom',
                    sender_info: senderInfo,
                    recipient_info: recipientInfo
                })
            });

            const saveData = await saveResponse.json();
            if (saveData.status !== 'success') {
                throw new Error('Ошибка сохранения письма');
            }

            // Генерируем PDF
            const pdfResponse = await fetch(`${backendUrl}/api/generate-letter-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    letter_id: saveData.letter_id,
                    include_translation: true
                })
            });

            const pdfData = await pdfResponse.json();
            
            if (pdfData.status === 'success') {
                // Создаем blob из base64 данных
                const byteCharacters = atob(pdfData.pdf_data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'application/pdf' });

                // Создаем ссылку для скачивания
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = pdfData.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            } else {
                setError(pdfData.errors?.join(', ') || 'Ошибка генерации PDF');
            }
        } catch (error) {
            console.error('Ошибка скачивания PDF:', error);
            setError('Ошибка скачивания PDF');
        }
    };

    const resetComposer = () => {
        setCurrentStep('method');
        setSelectedMethod('');
        setSelectedCategory(null);
        setSelectedTemplate(null);
        setUserRequest('');
        setRecipientType('');
        setTemplateData({});
        setGeneratedLetter(null);
        setError('');
        setSearchQuery('');
    };

    const renderMethodSelection = () => (
        <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                    ✉️ Составление официальных писем
                </h2>
                <p className="text-gray-600 text-lg">
                    Выберите способ создания письма
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Использование шаблонов */}
                <div 
                    className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-8 cursor-pointer transform hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-blue-300"
                    onClick={() => {
                        setSelectedMethod('template');
                        setCurrentStep('categories');
                    }}
                >
                    <div className="text-center">
                        <ClipboardDocumentListIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-800 mb-3">
                            📋 Использовать шаблон
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Выберите готовый шаблон для Job Center, BAMF, медицинских учреждений и других организаций
                        </p>
                        <div className="flex flex-wrap gap-2 justify-center">
                            <span className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">🏢 Job Center</span>
                            <span className="bg-purple-200 text-purple-800 px-3 py-1 rounded-full text-sm">🏛️ BAMF</span>
                            <span className="bg-green-200 text-green-800 px-3 py-1 rounded-full text-sm">🏥 Медицина</span>
                        </div>
                    </div>
                </div>

                {/* Создание с нуля */}
                <div 
                    className="bg-gradient-to-br from-purple-50 to-pink-100 rounded-2xl p-8 cursor-pointer transform hover:scale-105 transition-all duration-300 border-2 border-transparent hover:border-purple-300"
                    onClick={() => {
                        setSelectedMethod('custom');
                        setCurrentStep('compose');
                    }}
                >
                    <div className="text-center">
                        <PencilSquareIcon className="w-16 h-16 text-purple-600 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-800 mb-3">
                            ✨ Создать с AI
                        </h3>
                        <p className="text-gray-600 mb-4">
                            Опишите что вы хотите написать и кому - AI создаст профессиональное письмо на немецком языке
                        </p>
                        <div className="flex flex-wrap gap-2 justify-center">
                            <span className="bg-purple-200 text-purple-800 px-3 py-1 rounded-full text-sm">🤖 AI генерация</span>
                            <span className="bg-pink-200 text-pink-800 px-3 py-1 rounded-full text-sm">🌐 Перевод</span>
                            <span className="bg-indigo-200 text-indigo-800 px-3 py-1 rounded-full text-sm">✅ Проверка</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderCategories = () => (
        <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <button 
                    onClick={() => setCurrentStep('method')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    ← Назад к выбору способа
                </button>
                <h2 className="text-2xl font-bold text-gray-800">
                    Категории шаблонов
                </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {categories.map((category) => (
                    <div 
                        key={category.key}
                        className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg cursor-pointer transform hover:scale-105 transition-all duration-300 border"
                        onClick={() => loadTemplates(category.key)}
                    >
                        <div className="text-center">
                            <div className="text-4xl mb-3">{category.icon}</div>
                            <h3 className="font-bold text-gray-800 mb-2">
                                {category.name}
                            </h3>
                            <p className="text-sm text-gray-600">
                                {category.template_count} шаблонов
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderTemplates = () => (
        <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <button 
                    onClick={() => setCurrentStep('categories')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    ← Назад к категориям
                </button>
                <h2 className="text-2xl font-bold text-gray-800">
                    Шаблоны писем
                </h2>
            </div>

            <div className="space-y-4">
                {templates.map((template) => (
                    <div 
                        key={template.key}
                        className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg cursor-pointer border-l-4 border-blue-500 hover:border-blue-600 transition-all duration-300"
                        onClick={() => loadTemplate(selectedCategory, template.key)}
                    >
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-bold text-gray-800 text-lg mb-2">
                                    {template.name}
                                </h3>
                                <p className="text-gray-600">
                                    {template.description}
                                </p>
                            </div>
                            <DocumentTextIcon className="w-6 h-6 text-gray-400" />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderCompose = () => (
        <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <button 
                    onClick={() => selectedMethod === 'template' ? setCurrentStep('templates') : setCurrentStep('method')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    ← Назад
                </button>
                <h2 className="text-2xl font-bold text-gray-800">
                    {selectedMethod === 'template' ? 'Заполнение шаблона' : 'Создание письма с AI'}
                </h2>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <p className="text-red-600">{error}</p>
                </div>
            )}

            <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-6">
                    {selectedMethod === 'custom' ? (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    📝 Что вы хотите написать? *
                                </label>
                                <textarea
                                    value={userRequest}
                                    onChange={(e) => setUserRequest(e.target.value)}
                                    placeholder="Например: Хочу написать возражение против санкции от Job Center, которая была наложена несправедливо из-за пропуска встречи по болезни"
                                    className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    rows={4}
                                    required
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    🏢 Кому адресовано письмо? *
                                </label>
                                <input
                                    type="text"
                                    value={recipientType}
                                    onChange={(e) => setRecipientType(e.target.value)}
                                    placeholder="Например: Job Center, BAMF, врачу, школе, работодателю"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    required
                                />
                            </div>
                        </>
                    ) : (
                        selectedTemplate && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                                    📄 {selectedTemplate.name}
                                </h3>
                                <p className="text-gray-600 mb-4">
                                    {selectedTemplate.description}
                                </p>
                                
                                <div className="space-y-4">
                                    {selectedTemplate.variables.map((variable) => (
                                        <div key={variable}>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                {variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} *
                                            </label>
                                            <input
                                                type="text"
                                                value={templateData[variable] || ''}
                                                onChange={(e) => setTemplateData(prev => ({
                                                    ...prev,
                                                    [variable]: e.target.value
                                                }))}
                                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                                placeholder={`Введите ${variable.replace(/_/g, ' ')}`}
                                                required
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    )}
                </div>

                <div className="space-y-6">
                    {/* Информация об отправителе */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">
                            👤 Информация об отправителе
                        </h3>
                        <div className="space-y-3">
                            <input
                                type="text"
                                value={senderInfo.name}
                                onChange={(e) => setSenderInfo(prev => ({...prev, name: e.target.value}))}
                                placeholder="Полное имя"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <input
                                type="text"
                                value={senderInfo.address}
                                onChange={(e) => setSenderInfo(prev => ({...prev, address: e.target.value}))}
                                placeholder="Адрес"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <div className="grid grid-cols-2 gap-3">
                                <input
                                    type="text"
                                    value={senderInfo.postal_code}
                                    onChange={(e) => setSenderInfo(prev => ({...prev, postal_code: e.target.value}))}
                                    placeholder="PLZ"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                <input
                                    type="text"
                                    value={senderInfo.city}
                                    onChange={(e) => setSenderInfo(prev => ({...prev, city: e.target.value}))}
                                    placeholder="Stadt"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <input
                                type="tel"
                                value={senderInfo.phone}
                                onChange={(e) => setSenderInfo(prev => ({...prev, phone: e.target.value}))}
                                placeholder="Telefon"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <input
                                type="email"
                                value={senderInfo.email}
                                onChange={(e) => setSenderInfo(prev => ({...prev, email: e.target.value}))}
                                placeholder="E-Mail"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    {/* Информация о получателе */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">
                            🏢 Информация о получателе
                        </h3>
                        <div className="space-y-3">
                            <input
                                type="text"
                                value={recipientInfo.name}
                                onChange={(e) => setRecipientInfo(prev => ({...prev, name: e.target.value}))}
                                placeholder="Название организации"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <input
                                type="text"
                                value={recipientInfo.department}
                                onChange={(e) => setRecipientInfo(prev => ({...prev, department: e.target.value}))}
                                placeholder="Отдел (необязательно)"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <input
                                type="text"
                                value={recipientInfo.address}
                                onChange={(e) => setRecipientInfo(prev => ({...prev, address: e.target.value}))}
                                placeholder="Адрес"
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <div className="grid grid-cols-2 gap-3">
                                <input
                                    type="text"
                                    value={recipientInfo.postal_code}
                                    onChange={(e) => setRecipientInfo(prev => ({...prev, postal_code: e.target.value}))}
                                    placeholder="PLZ"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                <input
                                    type="text"
                                    value={recipientInfo.city}
                                    onChange={(e) => setRecipientInfo(prev => ({...prev, city: e.target.value}))}
                                    placeholder="Stadt"
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-8 text-center">
                <button
                    onClick={selectedMethod === 'template' ? generateTemplateLetter : generateCustomLetter}
                    disabled={isGenerating}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:transform-none flex items-center gap-2 mx-auto"
                >
                    {isGenerating ? (
                        <>
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            Генерирую письмо...
                        </>
                    ) : (
                        <>
                            <SparklesIcon className="w-5 h-5" />
                            Создать письмо
                        </>
                    )}
                </button>
            </div>
        </div>
    );

    const renderPreview = () => (
        <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <button 
                    onClick={() => setCurrentStep('compose')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    ← Редактировать
                </button>
                <div className="flex gap-3">
                    <button
                        onClick={downloadPDF}
                        className="bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 transform hover:scale-105 transition-all duration-300 flex items-center gap-2"
                    >
                        <ArrowDownTrayIcon className="w-5 h-5" />
                        Скачать PDF
                    </button>
                    <button
                        onClick={resetComposer}
                        className="bg-gray-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-700 transform hover:scale-105 transition-all duration-300"
                    >
                        Создать новое
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-8">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                        📄 Готовое письмо
                    </h2>
                    {generatedLetter?.subject && (
                        <p className="text-lg text-gray-600">
                            <strong>Тема:</strong> {generatedLetter.subject}
                        </p>
                    )}
                </div>

                {/* Немецкая версия */}
                <div className="border-l-4 border-blue-500 pl-6 mb-8">
                    <h3 className="text-lg font-semibold text-blue-800 mb-4">
                        🇩🇪 Письмо на немецком языке
                    </h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <pre className="whitespace-pre-wrap text-gray-800 font-sans leading-relaxed">
                            {generatedLetter?.content}
                        </pre>
                    </div>
                </div>

                {/* Перевод */}
                {generatedLetter?.translation && (
                    <div className="border-l-4 border-green-500 pl-6">
                        <h3 className="text-lg font-semibold text-green-800 mb-4">
                            📚 {generatedLetter.translation_language} (для ознакомления)
                        </h3>
                        <div className="bg-green-50 p-4 rounded-lg">
                            <pre className="whitespace-pre-wrap text-gray-800 font-sans leading-relaxed">
                                {generatedLetter.translation}
                            </pre>
                        </div>
                    </div>
                )}

                {/* Дополнительная информация */}
                {(generatedLetter?.key_points?.length > 0 || generatedLetter?.suggestions?.length > 0) && (
                    <div className="mt-8 p-6 bg-blue-50 rounded-lg">
                        {generatedLetter.key_points?.length > 0 && (
                            <div className="mb-4">
                                <h4 className="font-semibold text-blue-800 mb-2">
                                    🎯 Ключевые моменты:
                                </h4>
                                <ul className="list-disc list-inside space-y-1">
                                    {generatedLetter.key_points.map((point, index) => (
                                        <li key={index} className="text-blue-700">
                                            {point}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {generatedLetter.suggestions?.length > 0 && (
                            <div>
                                <h4 className="font-semibold text-blue-800 mb-2">
                                    💡 Рекомендации:
                                </h4>
                                <ul className="list-disc list-inside space-y-1">
                                    {generatedLetter.suggestions.map((suggestion, index) => (
                                        <li key={index} className="text-blue-700">
                                            {suggestion}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
            {currentStep === 'method' && renderMethodSelection()}
            {currentStep === 'categories' && renderCategories()}
            {currentStep === 'templates' && renderTemplates()}
            {currentStep === 'compose' && renderCompose()}
            {currentStep === 'preview' && renderPreview()}
        </div>
    );
};

export default LetterComposer;