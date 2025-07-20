import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    PencilSquareIcon,
    DocumentTextIcon, 
    SparklesIcon,
    ArrowDownTrayIcon,
    ClipboardDocumentListIcon,
    XMarkIcon,
    CheckIcon,
    ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback,
    showTelegramAlert 
} from '../utils/telegramWebApp';

const TelegramLetterComposer = ({ onBack }) => {
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

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    // Telegram WebApp specific setup
    useEffect(() => {
        if (isTelegramWebApp()) {
            const tg = getTelegramWebApp();
            if (tg) {
                tg.ready();
                tg.expand();
                // Set back button handler
                tg.BackButton.show();
                tg.BackButton.onClick(() => {
                    if (currentStep === 'method') {
                        onBack();
                    } else {
                        handleBackStep();
                    }
                });
            }
        }
        
        return () => {
            if (isTelegramWebApp()) {
                const tg = getTelegramWebApp();
                if (tg) {
                    tg.BackButton.hide();
                }
            }
        };
    }, [currentStep]);

    // Загрузка категорий при инициализации
    useEffect(() => {
        if (selectedMethod === 'template') {
            loadCategories();
        }
    }, [selectedMethod]);

    const handleBackStep = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        
        if (currentStep === 'preview') {
            setCurrentStep('compose');
        } else if (currentStep === 'compose') {
            setCurrentStep(selectedMethod === 'template' ? 'templates' : 'method');
        } else if (currentStep === 'templates') {
            setCurrentStep('categories');
        } else if (currentStep === 'categories') {
            setCurrentStep('method');
        } else {
            onBack();
        }
    };

    const handleHapticClick = (callback) => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        callback();
    };

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
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка загрузки категорий шаблонов');
            }
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
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка загрузки шаблонов');
            }
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
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка загрузки шаблона');
            }
        }
    };

    const generateCustomLetter = async () => {
        if (!userRequest.trim() || !recipientType.trim()) {
            setError('Пожалуйста, заполните описание письма и тип получателя');
            return;
        }

        setIsGenerating(true);
        setError('');

        if (isTelegramWebApp()) {
            hapticFeedback('medium');
        }

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
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                }
            } else {
                setError(data.error || 'Ошибка генерации письма');
                if (isTelegramWebApp()) {
                    showTelegramAlert(data.error || 'Ошибка генерации письма');
                }
            }
        } catch (error) {
            console.error('Ошибка генерации письма:', error);
            setError('Ошибка подключения к серверу');
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка подключения к серверу');
            }
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

        if (isTelegramWebApp()) {
            hapticFeedback('medium');
        }

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
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                }
            } else {
                setError(data.error || 'Ошибка генерации письма');
                if (isTelegramWebApp()) {
                    showTelegramAlert(data.error || 'Ошибка генерации письма');
                }
            }
        } catch (error) {
            console.error('Ошибка генерации письма из шаблона:', error);
            setError('Ошибка подключения к серверу');
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка подключения к серверу');
            }
        } finally {
            setIsGenerating(false);
        }
    };

    const downloadPDF = async () => {
        if (!generatedLetter) return;

        if (isTelegramWebApp()) {
            hapticFeedback('medium');
        }

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
                // В Telegram WebApp показываем сообщение об успехе
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                    showTelegramAlert(`PDF сохранен: ${pdfData.filename}`);
                } else {
                    // Создаем blob из base64 данных для обычного браузера
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
                }
            } else {
                setError(pdfData.errors?.join(', ') || 'Ошибка генерации PDF');
                if (isTelegramWebApp()) {
                    showTelegramAlert(pdfData.errors?.join(', ') || 'Ошибка генерации PDF');
                }
            }
        } catch (error) {
            console.error('Ошибка скачивания PDF:', error);
            setError('Ошибка скачивания PDF');
            if (isTelegramWebApp()) {
                showTelegramAlert('Ошибка скачивания PDF');
            }
        }
    };

    const resetComposer = () => {
        handleHapticClick(() => {
            setCurrentStep('method');
            setSelectedMethod('');
            setSelectedCategory(null);
            setSelectedTemplate(null);
            setUserRequest('');
            setRecipientType('');
            setTemplateData({});
            setGeneratedLetter(null);
            setError('');
        });
    };

    const renderMethodSelection = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-purple-900 text-white">
            <div className="container mx-auto px-4 py-8">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold mb-4">
                        ✉️ Составление официальных писем
                    </h2>
                    <p className="text-blue-100 text-lg">
                        Выберите способ создания письма
                    </p>
                </div>

                <div className="space-y-6">
                    {/* Использование шаблонов */}
                    <div 
                        className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 cursor-pointer transform active:scale-95 transition-all duration-300 border border-white/20"
                        onClick={() => handleHapticClick(() => {
                            setSelectedMethod('template');
                            setCurrentStep('categories');
                        })}
                    >
                        <div className="text-center">
                            <ClipboardDocumentListIcon className="w-16 h-16 text-blue-300 mx-auto mb-4" />
                            <h3 className="text-xl font-bold mb-3">
                                📋 Использовать шаблон
                            </h3>
                            <p className="text-blue-100 mb-4">
                                Выберите готовый шаблон для Job Center, BAMF, медицинских учреждений и других организаций
                            </p>
                            <div className="flex flex-wrap gap-2 justify-center">
                                <span className="bg-blue-500/30 text-blue-200 px-3 py-1 rounded-full text-sm">🏢 Job Center</span>
                                <span className="bg-purple-500/30 text-purple-200 px-3 py-1 rounded-full text-sm">🏛️ BAMF</span>
                                <span className="bg-green-500/30 text-green-200 px-3 py-1 rounded-full text-sm">🏥 Медицина</span>
                            </div>
                        </div>
                    </div>

                    {/* Создание с нуля */}
                    <div 
                        className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 cursor-pointer transform active:scale-95 transition-all duration-300 border border-white/20"
                        onClick={() => handleHapticClick(() => {
                            setSelectedMethod('custom');
                            setCurrentStep('compose');
                        })}
                    >
                        <div className="text-center">
                            <PencilSquareIcon className="w-16 h-16 text-purple-300 mx-auto mb-4" />
                            <h3 className="text-xl font-bold mb-3">
                                ✨ Создать с AI
                            </h3>
                            <p className="text-purple-100 mb-4">
                                Опишите что вы хотите написать и кому - AI создаст профессиональное письмо на немецком языке
                            </p>
                            <div className="flex flex-wrap gap-2 justify-center">
                                <span className="bg-purple-500/30 text-purple-200 px-3 py-1 rounded-full text-sm">🤖 AI генерация</span>
                                <span className="bg-pink-500/30 text-pink-200 px-3 py-1 rounded-full text-sm">🌐 Перевод</span>
                                <span className="bg-indigo-500/30 text-indigo-200 px-3 py-1 rounded-full text-sm">✅ Проверка</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderCategories = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-purple-900 text-white">
            <div className="container mx-auto px-4 py-8">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold">
                        Категории шаблонов
                    </h2>
                </div>

                <div className="space-y-4">
                    {categories.map((category) => (
                        <div 
                            key={category.key}
                            className="bg-white/10 backdrop-blur-lg rounded-xl p-6 cursor-pointer transform active:scale-95 transition-all duration-300 border border-white/20"
                            onClick={() => handleHapticClick(() => loadTemplates(category.key))}
                        >
                            <div className="text-center">
                                <div className="text-4xl mb-3">{category.icon}</div>
                                <h3 className="font-bold mb-2">
                                    {category.name}
                                </h3>
                                <p className="text-sm text-blue-100">
                                    {category.template_count} шаблонов
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderTemplates = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-purple-900 text-white">
            <div className="container mx-auto px-4 py-8">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold">
                        Шаблоны писем
                    </h2>
                </div>

                <div className="space-y-4">
                    {templates.map((template) => (
                        <div 
                            key={template.key}
                            className="bg-white/10 backdrop-blur-lg rounded-xl p-6 cursor-pointer border-l-4 border-blue-400 transform active:scale-95 transition-all duration-300"
                            onClick={() => handleHapticClick(() => loadTemplate(selectedCategory, template.key))}
                        >
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-bold text-lg mb-2">
                                        {template.name}
                                    </h3>
                                    <p className="text-blue-100">
                                        {template.description}
                                    </p>
                                </div>
                                <DocumentTextIcon className="w-6 h-6 text-blue-300" />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderCompose = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-purple-900 text-white">
            <div className="container mx-auto px-4 py-6">
                <div className="text-center mb-6">
                    <h2 className="text-xl font-bold">
                        {selectedMethod === 'template' ? 'Заполнение шаблона' : 'Создание письма с AI'}
                    </h2>
                </div>

                {error && (
                    <div className="bg-red-500/20 border border-red-400 rounded-lg p-4 mb-6">
                        <p className="text-red-200">{error}</p>
                    </div>
                )}

                <div className="space-y-6">
                    {selectedMethod === 'custom' ? (
                        <>
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    📝 Что вы хотите написать? *
                                </label>
                                <textarea
                                    value={userRequest}
                                    onChange={(e) => setUserRequest(e.target.value)}
                                    placeholder="Например: Хочу написать возражение против санкции от Job Center..."
                                    className="w-full p-4 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                                    rows={4}
                                    required
                                />
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    🏢 Кому адресовано письмо? *
                                </label>
                                <input
                                    type="text"
                                    value={recipientType}
                                    onChange={(e) => setRecipientType(e.target.value)}
                                    placeholder="Например: Job Center, BAMF, врачу..."
                                    className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                                    required
                                />
                            </div>
                        </>
                    ) : (
                        selectedTemplate && (
                            <div>
                                <h3 className="text-lg font-semibold mb-4">
                                    📄 {selectedTemplate.name}
                                </h3>
                                <p className="text-blue-100 mb-4">
                                    {selectedTemplate.description}
                                </p>
                                
                                <div className="space-y-4">
                                    {selectedTemplate.variables.map((variable) => (
                                        <div key={variable}>
                                            <label className="block text-sm font-medium mb-2">
                                                {variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} *
                                            </label>
                                            <input
                                                type="text"
                                                value={templateData[variable] || ''}
                                                onChange={(e) => setTemplateData(prev => ({
                                                    ...prev,
                                                    [variable]: e.target.value
                                                }))}
                                                className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                                                placeholder={`Введите ${variable.replace(/_/g, ' ')}`}
                                                required
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    )}

                    {/* Информация об отправителе (упрощенная для Telegram) */}
                    <div>
                        <h3 className="text-lg font-semibold mb-4">
                            👤 Информация об отправителе
                        </h3>
                        <div className="space-y-3">
                            <input
                                type="text"
                                value={senderInfo.name}
                                onChange={(e) => setSenderInfo(prev => ({...prev, name: e.target.value}))}
                                placeholder="Полное имя"
                                className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                            />
                            <input
                                type="text"
                                value={senderInfo.address}
                                onChange={(e) => setSenderInfo(prev => ({...prev, address: e.target.value}))}
                                placeholder="Адрес"
                                className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                            />
                            <div className="grid grid-cols-2 gap-3">
                                <input
                                    type="text"
                                    value={senderInfo.postal_code}
                                    onChange={(e) => setSenderInfo(prev => ({...prev, postal_code: e.target.value}))}
                                    placeholder="PLZ"
                                    className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                                />
                                <input
                                    type="text"
                                    value={senderInfo.city}
                                    onChange={(e) => setSenderInfo(prev => ({...prev, city: e.target.value}))}
                                    placeholder="Stadt"
                                    className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Информация о получателе (упрощенная для Telegram) */}
                    <div>
                        <h3 className="text-lg font-semibold mb-4">
                            🏢 Информация о получателе
                        </h3>
                        <div className="space-y-3">
                            <input
                                type="text"
                                value={recipientInfo.name}
                                onChange={(e) => setRecipientInfo(prev => ({...prev, name: e.target.value}))}
                                placeholder="Название организации"
                                className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                            />
                            <input
                                type="text"
                                value={recipientInfo.address}
                                onChange={(e) => setRecipientInfo(prev => ({...prev, address: e.target.value}))}
                                placeholder="Адрес организации"
                                className="w-full p-3 border border-white/20 rounded-lg bg-white/10 backdrop-blur-lg text-white placeholder-blue-200 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                            />
                        </div>
                    </div>
                </div>

                <div className="mt-8 text-center sticky bottom-6">
                    <button
                        onClick={() => handleHapticClick(selectedMethod === 'template' ? generateTemplateLetter : generateCustomLetter)}
                        disabled={isGenerating}
                        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-medium transform active:scale-95 transition-all duration-300 disabled:opacity-50 disabled:transform-none flex items-center justify-center gap-2"
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
        </div>
    );

    const renderPreview = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-700 to-purple-900 text-white">
            <div className="container mx-auto px-4 py-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold">
                        📄 Готовое письмо
                    </h2>
                    <div className="flex gap-2">
                        <button
                            onClick={() => handleHapticClick(downloadPDF)}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium transform active:scale-95 transition-all duration-300 flex items-center gap-2 text-sm"
                        >
                            <ArrowDownTrayIcon className="w-4 h-4" />
                            PDF
                        </button>
                        <button
                            onClick={() => handleHapticClick(resetComposer)}
                            className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transform active:scale-95 transition-all duration-300 text-sm"
                        >
                            Новое
                        </button>
                    </div>
                </div>

                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6">
                    {generatedLetter?.subject && (
                        <div className="mb-6">
                            <p className="text-lg text-blue-200">
                                <strong>Тема:</strong> {generatedLetter.subject}
                            </p>
                        </div>
                    )}

                    {/* Немецкая версия */}
                    <div className="border-l-4 border-blue-400 pl-4 mb-6">
                        <h3 className="text-lg font-semibold text-blue-200 mb-4">
                            🇩🇪 Письмо на немецком языке
                        </h3>
                        <div className="bg-white/5 p-4 rounded-lg">
                            <pre className="whitespace-pre-wrap text-white font-sans leading-relaxed text-sm">
                                {generatedLetter?.content}
                            </pre>
                        </div>
                    </div>

                    {/* Перевод */}
                    {generatedLetter?.translation && (
                        <div className="border-l-4 border-green-400 pl-4">
                            <h3 className="text-lg font-semibold text-green-200 mb-4">
                                📚 {generatedLetter.translation_language} (для ознакомления)
                            </h3>
                            <div className="bg-white/5 p-4 rounded-lg">
                                <pre className="whitespace-pre-wrap text-white font-sans leading-relaxed text-sm">
                                    {generatedLetter.translation}
                                </pre>
                            </div>
                        </div>
                    )}

                    {/* Дополнительная информация */}
                    {(generatedLetter?.key_points?.length > 0 || generatedLetter?.suggestions?.length > 0) && (
                        <div className="mt-6 p-4 bg-white/5 rounded-lg">
                            {generatedLetter.key_points?.length > 0 && (
                                <div className="mb-4">
                                    <h4 className="font-semibold text-blue-200 mb-2">
                                        🎯 Ключевые моменты:
                                    </h4>
                                    <ul className="list-disc list-inside space-y-1">
                                        {generatedLetter.key_points.map((point, index) => (
                                            <li key={index} className="text-blue-100 text-sm">
                                                {point}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {generatedLetter.suggestions?.length > 0 && (
                                <div>
                                    <h4 className="font-semibold text-blue-200 mb-2">
                                        💡 Рекомендации:
                                    </h4>
                                    <ul className="list-disc list-inside space-y-1">
                                        {generatedLetter.suggestions.map((suggestion, index) => (
                                            <li key={index} className="text-blue-100 text-sm">
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
        </div>
    );

    // Render appropriate step
    if (currentStep === 'method') return renderMethodSelection();
    if (currentStep === 'categories') return renderCategories();
    if (currentStep === 'templates') return renderTemplates();
    if (currentStep === 'compose') return renderCompose();
    if (currentStep === 'preview') return renderPreview();
    
    return renderMethodSelection();
};

export default TelegramLetterComposer;