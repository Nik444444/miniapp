import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Briefcase, Search, MapPin, Filter, Bell, Star, 
    Zap, Globe, CheckCircle, AlertCircle, Clock,
    User, FileText, MessageCircle, TrendingUp, 
    Building2, Euro, Languages, Target, ArrowRight,
    BookOpen, Brain, Award, MessageSquare, Sparkles,
    ChevronDown, X
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    hapticFeedback, 
    telegramWebApp,
    showBackButton,
    hideBackButton 
} from '../utils/telegramWebApp';

const TelegramJobSearch = ({ onBack }) => {
    const { user, backendUrl } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('main'); // main, search, resume-analysis, interview-prep
    const [loading, setLoading] = useState(false);
    const [jobs, setJobs] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    const [searchFilters, setSearchFilters] = useState({
        search_query: '',
        location: '',
        remote: null,
        visa_sponsorship: null,
        language_level: '',
        category: ''
    });
    const [resumeText, setResumeText] = useState('');
    const [targetPosition, setTargetPosition] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [interviewType, setInterviewType] = useState('behavioral');
    const [jobDescription, setJobDescription] = useState('');
    const [coachingResult, setCoachingResult] = useState(null);
    
    // City search state
    const [cities, setCities] = useState([]);
    const [showCityDropdown, setShowCityDropdown] = useState(false);
    const [citySearchInput, setCitySearchInput] = useState('');

    const languageLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    const jobCategories = ['tech', 'marketing', 'finance', 'sales', 'design', 'management', 'healthcare', 'education', 'other'];
    const interviewTypes = {
        'behavioral': 'Поведенческое интервью',
        'technical': 'Техническое интервью',
        'case_study': 'Кейс-интервью',
        'cultural_fit': 'Культурное соответствие',
        'phone_screening': 'Телефонный скрининг',
        'final_round': 'Финальное интервью'
    };

    useEffect(() => {
        try {
            console.log('TelegramJobSearch mounted');
            console.log('Backend URL:', backendUrl);
            console.log('Is Telegram WebApp:', isTelegramWebApp());
            
            if (isTelegramWebApp()) {
                if (currentView !== 'main') {
                    showBackButton(handleBackClick);
                } else {
                    hideBackButton();
                }
            }
            
            // Load subscriptions if user is authenticated
            if (user) {
                loadSubscriptions();
            }
            
            // Load popular cities
            loadPopularCities();
            
            // Initialize city search input with current location filter
            const currentLocation = searchFilters.location || '';
            if (currentLocation !== citySearchInput) {
                console.log('Initializing city search with:', currentLocation);
                setCitySearchInput(currentLocation);
            }
        } catch (error) {
            console.error('Error in TelegramJobSearch useEffect:', error);
        }
    }, [currentView, user, searchFilters.location]);

    // Search cities when user types
    useEffect(() => {
        const delayDebounce = setTimeout(() => {
            try {
                const input = citySearchInput || '';
                console.log('City search useEffect triggered with input:', input);
                
                if (input.length >= 2) {
                    console.log('Triggering city search for:', input);
                    searchCities(input);
                } else if (input.length === 0) {
                    console.log('Input empty, loading popular cities');
                    loadPopularCities();
                } else {
                    // При вводе менее 2 символов загружаем популярные города
                    console.log('Input too short, loading popular cities');
                    loadPopularCities();
                }
            } catch (error) {
                console.error('Error in city search useEffect:', error);
                setCities([]);
            }
        }, 300);

        return () => clearTimeout(delayDebounce);
    }, [citySearchInput, backendUrl]);

    const handleBackClick = () => {
        if (currentView === 'main') {
            onBack();
        } else {
            setCurrentView('main');
        }
    };

    const loadPopularCities = async () => {
        try {
            const url = `${backendUrl}/api/cities/popular`;
            console.log('Loading popular cities from:', url);
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Popular cities response:', data);
            
            if (data.status === 'success' && data.data && data.data.cities) {
                setCities(data.data.cities);
                console.log('Popular cities loaded:', data.data.cities.length);
            } else {
                console.warn('Popular cities returned unexpected format:', data);
                setCities([]);
            }
        } catch (error) {
            console.error('Error loading popular cities:', error);
            setCities([]);
        }
    };

    const searchCities = async (query) => {
        // Валидация и очистка query - перенесена наружу для доступности в catch
        const cleanQuery = query ? query.trim() : '';
        let safeQuery = '';
        
        try {
            if (cleanQuery.length < 2) {
                console.log('Query too short, loading popular cities instead');
                loadPopularCities();
                return;
            }
            
            // УЛУЧШЕННАЯ валидация и очистка запроса
            safeQuery = cleanQuery
                .replace(/[^\w\säöüÄÖÜß\-]/g, '') // Убираем все кроме букв, цифр, пробелов и немецких символов
                .substring(0, 50); // Ограничиваем длину
            
            if (!safeQuery || safeQuery.length < 2) {
                console.log('Query became invalid after cleaning, loading popular cities');
                loadPopularCities();
                return;
            }
            
            // Безопасное построение URL
            const encodedQuery = encodeURIComponent(safeQuery);
            const url = `${backendUrl}/api/cities/search?q=${encodedQuery}&limit=10`;
            
            console.log('🏙️ Cities Search Debug:');
            console.log('Original query:', cleanQuery);
            console.log('Safe query:', safeQuery);
            console.log('Encoded query:', encodedQuery);
            console.log('Cities search URL:', url);
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('✅ Cities Response Info:');
            console.log('Status:', response.status);
            console.log('OK:', response.ok);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Cities API Error:', {
                    status: response.status,
                    statusText: response.statusText,
                    responseText: errorText
                });
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('✅ Cities search response:', data);
            
            if (data.status === 'success' && data.cities) {
                setCities(data.cities);
                console.log('Cities search result:', data.cities.length, 'cities found');
            } else {
                console.warn('Cities search returned unexpected format:', data);
                setCities([]);
            }
        } catch (error) {
            console.error('❌ Cities Search Error:');
            console.error('Error Type:', error.constructor.name);
            console.error('Error Message:', error.message);
            console.error('Error Stack:', error.stack);
            console.error('Cities search error details:', {
                message: error.message,
                stack: error.stack,
                query: cleanQuery,
                safeQuery: safeQuery || 'undefined'
            });
            
            setCities([]);
            
            // Показываем ошибку только если это реальная сетевая ошибка
            if (error.message && (error.message.includes('NetworkError') || error.message.includes('fetch'))) {
                console.error('🚨 NETWORK ERROR IN CITIES SEARCH:', error.message);
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert(`⚠️ Ошибка сети. Проверьте подключение к интернету.`);
                }
            }
        }
    };

    const handleCitySelect = (cityName) => {
        try {
            // Валидация названия города
            if (!cityName || typeof cityName !== 'string') {
                console.warn('Invalid city name:', cityName);
                return;
            }
            
            const cleanCityName = cityName.trim();
            if (cleanCityName.length === 0) {
                console.warn('Empty city name after trim');
                return;
            }
            
            console.log('Selecting city:', cleanCityName);
            
            // ИСПРАВЛЕНИЕ: Устанавливаем город в оба места - в input И в фильтры поиска
            setCitySearchInput(cleanCityName);
            setSearchFilters(prev => ({...prev, location: cleanCityName}));
            setShowCityDropdown(false);
            
            if (isTelegramWebApp()) hapticFeedback('light');
        } catch (error) {
            console.error('Error selecting city:', error);
        }
    };

    const loadSubscriptions = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/job-subscriptions`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setSubscriptions(data.data || []);
            }
        } catch (error) {
            console.error('Error loading subscriptions:', error);
        }
    };

    const searchJobs = async () => {
        setLoading(true);
        if (isTelegramWebApp()) hapticFeedback('light');

        try {
            // Проверка минимальных требований: город и уровень немецкого ОБЯЗАТЕЛЬНЫ
            const requiredFields = [];
            
            if (!searchFilters.location || searchFilters.location.trim() === '') {
                requiredFields.push('Город');
            }
            
            if (!searchFilters.language_level || searchFilters.language_level.trim() === '') {
                requiredFields.push('Уровень немецкого языка');
            }
            
            if (requiredFields.length > 0) {
                const errorMessage = `Пожалуйста, заполните обязательные поля: ${requiredFields.join(', ')}`;
                
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert(`❌ ${errorMessage}`);
                } else {
                    alert(`❌ ${errorMessage}`);
                }
                setLoading(false);
                return;
            }

            // Валидация и очистка параметров поиска
            const cleanFilters = {};
            Object.entries(searchFilters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    // Особая обработка строковых значений
                    if (typeof value === 'string') {
                        const cleanValue = value.trim();
                        if (cleanValue.length > 0) {
                            cleanFilters[key] = cleanValue;
                        }
                    } else {
                        cleanFilters[key] = value;
                    }
                }
            });

            // УЛУЧШЕННОЕ построение URL с более безопасным encoding
            let url = `${backendUrl}/api/job-search`;
            const paramParts = [];
            
            Object.entries(cleanFilters).forEach(([key, value]) => {
                try {
                    // Дополнительная валидация специальных символов
                    const safeValue = String(value).replace(/[^\w\säöüÄÖÜß\-+.,]/g, '');
                    paramParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(safeValue)}`);
                    console.log(`Encoded parameter: ${key} = "${value}" -> "${safeValue}"`);
                } catch (encodeError) {
                    console.warn('Failed to encode parameter:', key, value, encodeError);
                    // Fallback с еще более безопасным encoding
                    const safeFallback = String(value).replace(/[^\w\s]/g, '');
                    paramParts.push(`${key}=${safeFallback}`);
                }
            });

            if (paramParts.length > 0) {
                url += '?' + paramParts.join('&');
            }

            console.log('🔍 Job Search Debug Info:');
            console.log('Original filters:', searchFilters);
            console.log('Clean filters:', cleanFilters);
            console.log('Backend URL:', backendUrl);
            console.log('Full API URL:', url);
            console.log('Request headers:', {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            });

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('✅ Response Info:');
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            console.log('OK:', response.ok);
            console.log('Headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Response Error Details:');
                console.error('Status:', response.status);
                console.error('Status Text:', response.statusText);
                console.error('Response Text:', errorText);
                
                throw new Error(`HTTP ${response.status}: ${response.statusText}${errorText ? ' - ' + errorText : ''}`);
            }
            
            const data = await response.json();
            console.log('✅ Response data:', data);

            if (data.status === 'success') {
                const jobsData = data.jobs || [];  // Исправление: прямой путь к jobs
                console.log('Jobs found:', jobsData.length);
                
                setJobs(jobsData);
                const totalFound = data.total_found || jobsData.length;
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert(`✅ Найдено ${totalFound} вакансий!`);
                } else {
                    alert(`✅ Найдено ${totalFound} вакансий!`);
                }
            } else {
                console.error('API returned non-success status:', data);
                const errorMessage = data.message || 'Неизвестная ошибка сервера';
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert(`❌ ${errorMessage}`);
                } else {
                    alert(`❌ ${errorMessage}`);
                }
            }
        } catch (error) {
            console.error('❌ Job Search Error:');
            console.error('Error Type:', error.constructor.name);
            console.error('Error Message:', error.message);
            console.error('Error Stack:', error.stack);
            console.error('Full Error Object:', error);
            
            let errorMessage = 'Ошибка поиска работы';
            
            if (error.message) {
                if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                    errorMessage = '🌐 Ошибка сетевого соединения. Проверьте интернет-соединение.';
                } else if (error.message.includes('HTTP 400') || error.message.includes('Bad Request')) {
                    errorMessage = '⚠️ Ошибка валидации параметров поиска. Пожалуйста, проверьте введенные данные.';
                } else if (error.message.includes('HTTP 500')) {
                    errorMessage = '🔧 Ошибка сервера. Попробуйте позже.';
                } else {
                    // Включаем исходное сообщение об ошибке для отладки (но убираем ложные pattern errors)
                    errorMessage = `🔍 ${error.message}`;
                }
            }
            
            console.error('📢 User will see:', errorMessage);
            
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert(`❌ ${errorMessage}`);
            } else {
                alert(`❌ ${errorMessage}`);
            }
        } finally {
            setLoading(false);
        }
    };

    const createSubscription = async () => {
        if (isTelegramWebApp()) hapticFeedback('medium');

        try {
            const response = await fetch(`${backendUrl}/api/job-subscriptions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(searchFilters)
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert('Подписка создана! Уведомления будут приходить в Telegram');
                    hapticFeedback('success');
                }
                loadSubscriptions();
            }
        } catch (error) {
            console.error('Error creating subscription:', error);
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('Ошибка создания подписки');
            }
        }
    };

    const analyzeResume = async () => {
        if (!resumeText.trim()) {
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('Введите текст резюме для анализа');
            }
            return;
        }

        setLoading(true);
        if (isTelegramWebApp()) hapticFeedback('medium');

        try {
            const response = await fetch(`${backendUrl}/api/analyze-resume`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    resume_text: resumeText,
                    target_position: targetPosition,
                    language: 'ru'
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                setAnalysisResult(data);
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert('Анализ резюме завершен!');
                    hapticFeedback('success');
                }
            }
        } catch (error) {
            console.error('Error analyzing resume:', error);
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('Ошибка анализа резюме');
            }
        } finally {
            setLoading(false);
        }
    };

    const prepareInterview = async () => {
        if (!jobDescription.trim()) {
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('Введите описание вакансии для подготовки');
            }
            return;
        }

        setLoading(true);
        if (isTelegramWebApp()) hapticFeedback('medium');

        try {
            const response = await fetch(`${backendUrl}/api/prepare-interview`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    job_description: jobDescription,
                    resume_text: resumeText || undefined,
                    interview_type: interviewType,
                    language: 'ru'
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                setCoachingResult(data);
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert('Подготовка к собеседованию готова!');
                    hapticFeedback('success');
                }
            }
        } catch (error) {
            console.error('Error preparing interview:', error);
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('Ошибка подготовки к собеседованию');
            }
        } finally {
            setLoading(false);
        }
    };

    const renderJobCard = (job) => (
        <div key={job.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-3">
            <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-sm mb-1">{job.title}</h3>
                    <div className="flex items-center text-xs text-gray-600 mb-2">
                        <Building2 className="h-3 w-3 mr-1" />
                        <span className="mr-3">{job.company_name}</span>
                        <MapPin className="h-3 w-3 mr-1" />
                        <span>{job.location}</span>
                    </div>
                </div>
                {job.remote && (
                    <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                        Remote
                    </div>
                )}
            </div>

            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 text-xs">
                    {job.visa_sponsorship && (
                        <div className="flex items-center text-blue-600">
                            <Globe className="h-3 w-3 mr-1" />
                            <span>Visa</span>
                        </div>
                    )}
                    {job.estimated_salary && (
                        <div className="flex items-center text-green-600">
                            <Euro className="h-3 w-3 mr-1" />
                            <span>{job.estimated_salary.min_salary}k-{job.estimated_salary.max_salary}k</span>
                        </div>
                    )}
                </div>
                
                <button
                    onClick={() => {
                        if (isTelegramWebApp()) {
                            telegramWebApp.openLink(job.url || '#');
                        }
                    }}
                    className="text-blue-600 text-xs font-medium hover:text-blue-700"
                >
                    Подробнее →
                </button>
            </div>
        </div>
    );

    const renderMainView = () => (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white p-6 rounded-xl">
                <div className="flex justify-center mb-3">
                    <div className="bg-white/20 p-3 rounded-full">
                        <Briefcase className="h-6 w-6" />
                    </div>
                </div>
                <h1 className="text-xl font-bold mb-2">Поиск работы в Германии</h1>
                <p className="text-sm text-white/90">ИИ-помощник для карьеры с крутыми фишками</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-3">
                <div className="bg-white p-3 rounded-lg text-center shadow-sm">
                    <div className="text-lg font-bold text-violet-600">{jobs.length}</div>
                    <div className="text-xs text-gray-600">Найдено</div>
                </div>
                <div className="bg-white p-3 rounded-lg text-center shadow-sm">
                    <div className="text-lg font-bold text-green-600">{subscriptions.length}</div>
                    <div className="text-xs text-gray-600">Подписок</div>
                </div>
                <div className="bg-white p-3 rounded-lg text-center shadow-sm">
                    <div className="text-lg font-bold text-blue-600">AI</div>
                    <div className="text-xs text-gray-600">Готов</div>
                </div>
            </div>

            {/* Main Actions */}
            <div className="space-y-3">
                <button
                    onClick={() => {
                        setCurrentView('search');
                        if (isTelegramWebApp()) hapticFeedback('light');
                    }}
                    className="w-full bg-gradient-to-r from-violet-500 to-purple-600 text-white p-4 rounded-xl font-semibold flex items-center justify-between shadow-lg hover:shadow-xl transition-all"
                >
                    <div className="flex items-center">
                        <Search className="h-5 w-5 mr-3" />
                        <div className="text-left">
                            <div className="font-semibold">Поиск вакансий</div>
                            <div className="text-xs text-white/80">С ИИ-фильтрацией по языку</div>
                        </div>
                    </div>
                    <ArrowRight className="h-5 w-5" />
                </button>

                <button
                    onClick={() => {
                        setCurrentView('resume-analysis');
                        if (isTelegramWebApp()) hapticFeedback('light');
                    }}
                    className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 text-white p-4 rounded-xl font-semibold flex items-center justify-between shadow-lg hover:shadow-xl transition-all"
                >
                    <div className="flex items-center">
                        <FileText className="h-5 w-5 mr-3" />
                        <div className="text-left">
                            <div className="font-semibold">Анализ резюме</div>
                            <div className="text-xs text-white/80">ИИ улучшит ваше резюме</div>
                        </div>
                    </div>
                    <ArrowRight className="h-5 w-5" />
                </button>

                <button
                    onClick={() => {
                        setCurrentView('interview-prep');
                        if (isTelegramWebApp()) hapticFeedback('light');
                    }}
                    className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white p-4 rounded-xl font-semibold flex items-center justify-between shadow-lg hover:shadow-xl transition-all"
                >
                    <div className="flex items-center">
                        <MessageCircle className="h-5 w-5 mr-3" />
                        <div className="text-left">
                            <div className="font-semibold">Подготовка к собеседованию</div>
                            <div className="text-xs text-white/80">ИИ-коуч для интервью</div>
                        </div>
                    </div>
                    <ArrowRight className="h-5 w-5" />
                </button>
            </div>

            {/* Active Subscriptions */}
            {subscriptions.length > 0 && (
                <div className="bg-white p-4 rounded-xl shadow-sm">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900 flex items-center">
                            <Bell className="h-4 w-4 mr-2 text-green-600" />
                            Активные подписки
                        </h3>
                        <span className="text-xs text-gray-500">{subscriptions.length}</span>
                    </div>
                    <div className="space-y-2">
                        {subscriptions.slice(0, 2).map((sub, index) => (
                            <div key={index} className="bg-green-50 p-3 rounded-lg">
                                <div className="text-sm font-medium text-gray-900">
                                    {sub.search_query || sub.location || 'Все вакансии'}
                                </div>
                                <div className="text-xs text-gray-600 mt-1">
                                    {sub.language_level && `Уровень: ${sub.language_level} • `}
                                    Уведомления в Telegram
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Features */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-xl">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Sparkles className="h-4 w-4 mr-2 text-yellow-500" />
                    Крутые фишки
                </h3>
                <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="flex items-center text-gray-700">
                        <Languages className="h-3 w-3 mr-2 text-blue-500" />
                        Фильтр по уровню немецкого
                    </div>
                    <div className="flex items-center text-gray-700">
                        <Bell className="h-3 w-3 mr-2 text-green-500" />
                        Уведомления в Telegram
                    </div>
                    <div className="flex items-center text-gray-700">
                        <Brain className="h-3 w-3 mr-2 text-purple-500" />
                        ИИ-анализ резюме
                    </div>
                    <div className="flex items-center text-gray-700">
                        <Target className="h-3 w-3 mr-2 text-red-500" />
                        ИИ-коучинг интервью
                    </div>
                </div>
            </div>
        </div>
    );

    const renderSearchView = () => (
        <div className="space-y-4">
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-500 to-purple-600 text-white p-4 rounded-xl">
                <h2 className="font-bold text-lg mb-1 flex items-center justify-between">
                    Поиск вакансий 
                    <span className="text-xs bg-white/20 px-2 py-1 rounded-full">v2.0 🔥</span>
                </h2>
                <p className="text-sm text-white/90">Найдите идеальную работу с ИИ-фильтрами + автодополнение городов</p>
            </div>

            {/* Search Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
                <div>
                    <input
                        type="text"
                        placeholder="Поиск по должности (необязательно)..."
                        value={searchFilters.search_query}
                        onChange={(e) => setSearchFilters(prev => ({...prev, search_query: e.target.value}))}
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-1">💡 Оставьте пустым для поиска всех вакансий</p>
                </div>

                <div className="relative">
                    <input
                        type="text"
                        placeholder="Поиск города (например, Berlin) - ОБЯЗАТЕЛЬНО"
                        value={citySearchInput || ''}
                        onChange={(e) => {
                            try {
                                const value = e.target.value || '';
                                console.log('City input changed to:', value);
                                setCitySearchInput(value);
                                // ИСПРАВЛЕНИЕ: Также обновляем location в searchFilters при прямом вводе
                                setSearchFilters(prev => ({...prev, location: value}));
                                setShowCityDropdown(true);
                            } catch (error) {
                                console.error('Error handling city input change:', error);
                            }
                        }}
                        onFocus={() => {
                            console.log('City input focused, loading cities...');
                            setShowCityDropdown(true);
                            // Загружаем популярные города если поле пустое
                            if (!citySearchInput || citySearchInput.length < 2) {
                                loadPopularCities();
                            }
                        }}
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent pr-10"
                        required
                    />
                    <MapPin className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
                    
                    {/* ИСПРАВЛЕНИЕ: Показываем dropdown когда есть города ИЛИ при focus */}
                    {showCityDropdown && (
                        <div className="absolute z-50 w-full bg-white border border-gray-300 rounded-lg shadow-xl mt-1 max-h-60 overflow-y-auto">
                            <div className="p-2 text-xs text-gray-500 font-medium bg-gray-50">
                                {(citySearchInput || '').length >= 2 ? 'Результаты поиска:' : 'Популярные города:'}
                            </div>
                            {cities.length > 0 ? (
                                cities.map((city, index) => (
                                    <button
                                        key={`${city.name}-${index}`}
                                        onClick={(e) => {
                                            e.preventDefault();
                                            e.stopPropagation();
                                            handleCitySelect(city.name);
                                        }}
                                        className="w-full text-left p-3 hover:bg-violet-50 border-t border-gray-100 first:border-t-0 flex items-center justify-between transition-colors"
                                    >
                                        <div>
                                            <div className="text-sm font-medium text-gray-900">{city.name || 'Неизвестный город'}</div>
                                            <div className="text-xs text-gray-500">
                                                {city.state || 'Неизвестный регион'} • {city.population ? `${(city.population / 1000).toFixed(0)}k жителей` : 'Население неизвестно'}
                                            </div>
                                        </div>
                                        {city.type === 'major' && (
                                            <Star className="h-3 w-3 text-yellow-500" />
                                        )}
                                    </button>
                                ))
                            ) : (
                                <div className="p-3 text-sm text-gray-500 text-center">
                                    {(citySearchInput || '').length >= 2 ? 'Городов не найдено...' : 'Загрузка городов...'}
                                </div>
                            )}
                        </div>
                    )}
                    
                    {/* Close dropdown when clicking outside - ИСПРАВЛЕНИЕ z-index */}
                    {showCityDropdown && (
                        <div 
                            className="fixed inset-0 z-30" 
                            onClick={() => {
                                console.log('Закрытие dropdown');
                                setShowCityDropdown(false);
                            }}
                        />
                    )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                    <select
                        value={searchFilters.language_level}
                        onChange={(e) => setSearchFilters(prev => ({...prev, language_level: e.target.value}))}
                        className="p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                        required
                    >
                        <option value="">Уровень немецкого - ОБЯЗАТЕЛЬНО</option>
                        {languageLevels.map(level => (
                            <option key={level} value={level}>{level}</option>
                        ))}
                    </select>

                    <select
                        value={searchFilters.category}
                        onChange={(e) => setSearchFilters(prev => ({...prev, category: e.target.value}))}
                        className="p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    >
                        <option value="">Категория (необязательно)</option>
                        {jobCategories.map(category => (
                            <option key={category} value={category}>
                                {category.charAt(0).toUpperCase() + category.slice(1)}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="flex space-x-3">
                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={searchFilters.remote === true}
                            onChange={(e) => setSearchFilters(prev => ({...prev, remote: e.target.checked ? true : null}))}
                            className="mr-2 text-violet-600"
                        />
                        <span className="text-sm text-gray-700">Удаленная работа</span>
                    </label>
                    <label className="flex items-center">
                        <input
                            type="checkbox"
                            checked={searchFilters.visa_sponsorship === true}
                            onChange={(e) => setSearchFilters(prev => ({...prev, visa_sponsorship: e.target.checked ? true : null}))}
                            className="mr-2 text-violet-600"
                        />
                        <span className="text-sm text-gray-700">Виза</span>
                    </label>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
                <button
                    onClick={searchJobs}
                    disabled={loading || !searchFilters.location || !searchFilters.language_level}
                    className="flex-1 bg-violet-600 text-white p-3 rounded-lg font-semibold flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                            Поиск...
                        </>
                    ) : (
                        <>
                            <Search className="h-4 w-4 mr-2" />
                            Найти
                        </>
                    )}
                </button>
                <button
                    onClick={createSubscription}
                    disabled={!searchFilters.location || !searchFilters.language_level}
                    className="bg-green-600 text-white p-3 rounded-lg flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Bell className="h-4 w-4" />
                </button>
                
                {/* Debug info button */}
                <button
                    onClick={() => {
                        console.log('DEBUG INFO:');
                        console.log('searchFilters:', searchFilters);
                        console.log('citySearchInput:', citySearchInput);
                        console.log('location valid:', !!searchFilters.location);
                        console.log('language_level valid:', !!searchFilters.language_level);
                        console.log('Button should be enabled:', !(!searchFilters.location || !searchFilters.language_level));
                        
                        alert(`DEBUG INFO:
Location: '${searchFilters.location}'
Language: '${searchFilters.language_level}'  
City Input: '${citySearchInput}'
Location Valid: ${!!searchFilters.location}
Language Valid: ${!!searchFilters.language_level}
Button Enabled: ${!(!searchFilters.location || !searchFilters.language_level)}`);
                    }}
                    className="px-4 py-3 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200"
                >
                    🔧
                </button>
            </div>

            {/* Required fields notice */}
            <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-xs text-blue-800">
                    <strong>Обязательные поля:</strong> Город и уровень немецкого языка. 
                    Поиск по должности необязателен - оставьте пустым для поиска всех вакансий.
                </p>
            </div>

            {/* Results */}
            {jobs.length > 0 && (
                <div>
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900">Найденные вакансии</h3>
                        <span className="text-sm text-gray-500">{jobs.length} из {jobs.length}</span>
                    </div>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {jobs.map(renderJobCard)}
                    </div>
                </div>
            )}
        </div>
    );

    const renderResumeAnalysisView = () => (
        <div className="space-y-4">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white p-4 rounded-xl">
                <h2 className="font-bold text-lg mb-1">Анализ резюме</h2>
                <p className="text-sm text-white/90">ИИ проанализирует и улучшит ваше резюме</p>
            </div>

            {/* Resume Input */}
            <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Текст резюме
                    </label>
                    <textarea
                        value={resumeText}
                        onChange={(e) => setResumeText(e.target.value)}
                        placeholder="Вставьте текст вашего резюме..."
                        rows={6}
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Целевая позиция (опционально)
                    </label>
                    <input
                        type="text"
                        value={targetPosition}
                        onChange={(e) => setTargetPosition(e.target.value)}
                        placeholder="Например: Senior Developer"
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>

                <button
                    onClick={analyzeResume}
                    disabled={loading || !resumeText.trim()}
                    className="w-full bg-blue-600 text-white p-3 rounded-lg font-semibold flex items-center justify-center disabled:opacity-50"
                >
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                            Анализирую...
                        </>
                    ) : (
                        <>
                            <Brain className="h-4 w-4 mr-2" />
                            Анализировать резюме
                        </>
                    )}
                </button>
            </div>

            {/* Analysis Results */}
            {analysisResult && analysisResult.status === 'success' && (
                <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center">
                        <Award className="h-4 w-4 mr-2 text-blue-600" />
                        Результаты анализа
                    </h3>

                    {/* Score */}
                    <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Общая оценка</span>
                            <span className="text-lg font-bold text-blue-600">
                                {analysisResult.analysis.overall_score}/100
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-blue-600 h-2 rounded-full transition-all"
                                style={{ width: `${analysisResult.analysis.overall_score}%` }}
                            ></div>
                        </div>
                    </div>

                    {/* Strengths */}
                    {analysisResult.analysis.strengths && analysisResult.analysis.strengths.length > 0 && (
                        <div>
                            <h4 className="font-medium text-green-800 mb-2 flex items-center">
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Сильные стороны
                            </h4>
                            <div className="space-y-1">
                                {analysisResult.analysis.strengths.map((strength, index) => (
                                    <div key={index} className="text-sm text-gray-700 bg-green-50 p-2 rounded">
                                        • {strength}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Improvements */}
                    {analysisResult.analysis.improvements && analysisResult.analysis.improvements.length > 0 && (
                        <div>
                            <h4 className="font-medium text-orange-800 mb-2 flex items-center">
                                <AlertCircle className="h-4 w-4 mr-1" />
                                Области для улучшения
                            </h4>
                            <div className="space-y-1">
                                {analysisResult.analysis.improvements.map((improvement, index) => (
                                    <div key={index} className="text-sm text-gray-700 bg-orange-50 p-2 rounded">
                                        • {improvement}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Action Items */}
                    {analysisResult.analysis.action_items && analysisResult.analysis.action_items.length > 0 && (
                        <div>
                            <h4 className="font-medium text-purple-800 mb-2 flex items-center">
                                <Clock className="h-4 w-4 mr-1" />
                                План действий
                            </h4>
                            <div className="space-y-2">
                                {analysisResult.analysis.action_items.map((item, index) => (
                                    <div key={index} className="bg-purple-50 p-3 rounded-lg">
                                        <div className="font-medium text-sm text-purple-900">{item.title}</div>
                                        <div className="text-xs text-purple-700 mt-1">{item.description}</div>
                                        {item.estimated_time && (
                                            <div className="text-xs text-purple-600 mt-1">
                                                ⏱️ {item.estimated_time}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    const renderInterviewPrepView = () => (
        <div className="space-y-4">
            {/* Header */}
            <div className="bg-gradient-to-r from-orange-500 to-red-600 text-white p-4 rounded-xl">
                <h2 className="font-bold text-lg mb-1">Подготовка к собеседованию</h2>
                <p className="text-sm text-white/90">ИИ-коуч поможет подготовиться к интервью</p>
            </div>

            {/* Interview Prep Input */}
            <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Описание вакансии
                    </label>
                    <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Вставьте описание вакансии..."
                        rows={4}
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Тип интервью
                    </label>
                    <select
                        value={interviewType}
                        onChange={(e) => setInterviewType(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    >
                        {Object.entries(interviewTypes).map(([key, label]) => (
                            <option key={key} value={key}>{label}</option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={prepareInterview}
                    disabled={loading || !jobDescription.trim()}
                    className="w-full bg-orange-600 text-white p-3 rounded-lg font-semibold flex items-center justify-center disabled:opacity-50"
                >
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                            Подготавливаю...
                        </>
                    ) : (
                        <>
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Подготовиться к интервью
                        </>
                    )}
                </button>
            </div>

            {/* Coaching Results */}
            {coachingResult && coachingResult.status === 'success' && (
                <div className="bg-white p-4 rounded-xl shadow-sm space-y-4">
                    <h3 className="font-semibold text-gray-900 flex items-center">
                        <MessageCircle className="h-4 w-4 mr-2 text-orange-600" />
                        Подготовка к собеседованию
                    </h3>

                    {/* Expected Questions */}
                    {coachingResult.coaching.expected_questions && coachingResult.coaching.expected_questions.length > 0 && (
                        <div>
                            <h4 className="font-medium text-orange-800 mb-2 flex items-center">
                                <MessageSquare className="h-4 w-4 mr-1" />
                                Ожидаемые вопросы
                            </h4>
                            <div className="space-y-2">
                                {coachingResult.coaching.expected_questions.map((q, index) => (
                                    <div key={index} className="bg-orange-50 p-3 rounded-lg">
                                        <div className="font-medium text-sm text-orange-900">{q.question}</div>
                                        <div className="text-xs text-orange-700 mt-1">
                                            {q.type} • {q.difficulty}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Questions for Employer */}
                    {coachingResult.coaching.questions_for_employer && coachingResult.coaching.questions_for_employer.length > 0 && (
                        <div>
                            <h4 className="font-medium text-blue-800 mb-2 flex items-center">
                                <MessageCircle className="h-4 w-4 mr-1" />
                                Вопросы работодателю
                            </h4>
                            <div className="space-y-1">
                                {coachingResult.coaching.questions_for_employer.map((question, index) => (
                                    <div key={index} className="text-sm text-gray-700 bg-blue-50 p-2 rounded">
                                        • {question}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Preparation Checklist */}
                    {coachingResult.preparation_checklist && coachingResult.preparation_checklist.length > 0 && (
                        <div>
                            <h4 className="font-medium text-purple-800 mb-2 flex items-center">
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Чеклист подготовки
                            </h4>
                            <div className="space-y-2">
                                {coachingResult.preparation_checklist.map((item, index) => (
                                    <div key={index} className="bg-purple-50 p-3 rounded-lg">
                                        <div className="font-medium text-sm text-purple-900">{item.task}</div>
                                        <div className="text-xs text-purple-700 mt-1">
                                            Приоритет: {item.priority} • {item.time_needed}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-md mx-auto">
                {currentView === 'main' && renderMainView()}
                {currentView === 'search' && renderSearchView()}
                {currentView === 'resume-analysis' && renderResumeAnalysisView()}
                {currentView === 'interview-prep' && renderInterviewPrepView()}
            </div>
        </div>
    );
};

export default TelegramJobSearch;