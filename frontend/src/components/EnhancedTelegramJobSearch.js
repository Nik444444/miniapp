import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import AIJobAssistant from './AIJobAssistant';
import RevolutionaryAIRecruiter from './RevolutionaryAIRecruiter';
import { 
    Briefcase, Search, MapPin, Filter, Bell, Star, 
    Zap, Globe, CheckCircle, AlertCircle, Clock,
    User, FileText, MessageCircle, TrendingUp, 
    Building2, Euro, Languages, Target, ArrowRight,
    BookOpen, Brain, Award, MessageSquare, Sparkles,
    ChevronDown, X, Navigation, Radar, Settings,
    Plus, Minus, RotateCcw, Smartphone, Wifi,
    Calendar, Briefcase as BriefcaseIcon, Home,
    Clock3, Coffee, Moon, Sun, Send, ExternalLink,
    Bot, Rocket
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    hapticFeedback, 
    telegramWebApp,
    showBackButton,
    hideBackButton 
} from '../utils/telegramWebApp';

const EnhancedTelegramJobSearch = ({ onBack }) => {
    const { user, backendUrl } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('main');
    const [loading, setLoading] = useState(false);
    const [jobs, setJobs] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    
    // Enhanced search filters with geolocation
    const [searchFilters, setSearchFilters] = useState({
        search_query: '',
        location: '',
        radius: 50,
        remote: null,
        visa_sponsorship: null,
        language_level: '',
        category: '',
        work_time: '',
        published_since: null,
        contract_type: null
    });
    
    // Geolocation state
    const [userLocation, setUserLocation] = useState(null);
    const [locationLoading, setLocationLoading] = useState(false);
    const [nearestCities, setNearestCities] = useState([]);
    const [radiusOptions, setRadiusOptions] = useState([]);
    
    // Enhanced UI state
    const [searchResults, setSearchResults] = useState(null);
    const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
    const [selectedJob, setSelectedJob] = useState(null);
    const [viewMode, setViewMode] = useState('grid');
    
    // City search state
    const [cities, setCities] = useState([]);
    const [showCityDropdown, setShowCityDropdown] = useState(false);
    const [citySearchInput, setCitySearchInput] = useState('');

    // Enhanced options
    const languageLevels = [
        { value: 'A1', label: 'A1 - Anfänger', description: 'Basic everyday expressions' },
        { value: 'A2', label: 'A2 - Grundlagen', description: 'Simple routine matters' },
        { value: 'B1', label: 'B1 - Mittelstufe', description: 'Work and study topics' },
        { value: 'B2', label: 'B2 - Gehobene Mittelstufe', description: 'Complex texts' },
        { value: 'C1', label: 'C1 - Fortgeschritten', description: 'Professional fluency' },
        { value: 'C2', label: 'C2 - Muttersprachlich', description: 'Native-like proficiency' }
    ];
    
    const workTimeOptions = [
        { value: 'vz', label: 'Vollzeit', icon: <Sun className="w-4 h-4" />, description: 'Full-time positions' },
        { value: 'tz', label: 'Teilzeit', icon: <Clock3 className="w-4 h-4" />, description: 'Part-time positions' },
        { value: 'ho', label: 'Homeoffice', icon: <Home className="w-4 h-4" />, description: 'Remote/home office work' },
        { value: 'mj', label: 'Minijob', icon: <Coffee className="w-4 h-4" />, description: 'Mini jobs (450€ basis)' },
        { value: 'snw', label: 'Schicht/Nacht/Wochenende', icon: <Moon className="w-4 h-4" />, description: 'Shift, night or weekend work' }
    ];
    
    const jobCategories = [
        { value: 'tech', label: '💻 Tech & IT', description: 'Software, Hardware, IT-Services' },
        { value: 'healthcare', label: '🏥 Gesundheitswesen', description: 'Medizin, Pflege, Pharma' },
        { value: 'finance', label: '💰 Finanzen', description: 'Banking, Versicherung, Controlling' },
        { value: 'marketing', label: '📈 Marketing', description: 'Digital Marketing, PR, Werbung' },
        { value: 'sales', label: '🤝 Vertrieb', description: 'Verkauf, Account Management' },
        { value: 'education', label: '📚 Bildung', description: 'Lehrer, Ausbildung, Training' },
        { value: 'construction', label: '🏗️ Bau & Handwerk', description: 'Bauwesen, Elektrik, Installation' },
        { value: 'logistics', label: '🚛 Logistik', description: 'Transport, Lagerwirtschaft' },
        { value: 'gastronomy', label: '🍽️ Gastronomie', description: 'Restaurant, Hotel, Küche' },
        { value: 'retail', label: '🛍️ Einzelhandel', description: 'Verkauf, Handel' },
        { value: 'other', label: '🔧 Sonstige', description: 'Andere Bereiche' }
    ];

    useEffect(() => {
        try {
            console.log('🔍 Enhanced TelegramJobSearch mounted');
            console.log('Backend URL:', backendUrl);
            
            if (!backendUrl) {
                console.error('❌ BACKEND URL НЕ ОПРЕДЕЛЕН');
                return;
            }
            
            if (isTelegramWebApp()) {
                if (currentView !== 'main') {
                    showBackButton(handleBackClick);
                } else {
                    hideBackButton();
                }
                telegramWebApp.ready();
            }
            
            if (user) {
                loadSubscriptions();
            }
            
            loadPopularCities();
            loadRadiusOptions();
            
        } catch (error) {
            console.error('❌ Error in Enhanced TelegramJobSearch useEffect:', error);
        }
    }, [currentView, user, backendUrl]);

    // Enhanced geolocation functions
    const getCurrentLocation = async () => {
        setLocationLoading(true);
        hapticFeedback('light');
        
        try {
            if (!navigator.geolocation) {
                throw new Error('Geolocation не поддерживается вашим браузером');
            }
            
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                });
            });
            
            const coordinates = {
                lat: position.coords.latitude,
                lon: position.coords.longitude
            };
            
            setUserLocation(coordinates);
            
            const response = await fetch(`${backendUrl}/api/user-location-info`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': user?.token ? `Bearer ${user.token}` : ''
                },
                body: JSON.stringify(coordinates)
            });
            
            if (response.ok) {
                const locationData = await response.json();
                setNearestCities(locationData.data.nearest_cities || []);
                
                if (locationData.data.nearest_cities?.length > 0) {
                    const nearestCity = locationData.data.nearest_cities[0];
                    if (nearestCity.distance < 50) {
                        setSearchFilters(prev => ({
                            ...prev,
                            location: nearestCity.name
                        }));
                        setCitySearchInput(nearestCity.name);
                    }
                }
                
                if (isTelegramWebApp()) {
                    telegramWebApp.showAlert(`📍 Standort gefunden: ${locationData.data.location_detected || 'Deutschland'}`);
                }
            }
            
            hapticFeedback('success');
            
        } catch (error) {
            console.error('❌ Geolocation error:', error);
            
            let errorMessage = 'Standort konnte nicht ermittelt werden';
            if (error.code === 1) {
                errorMessage = 'Standortzugriff verweigert. Bitte aktivieren Sie die Berechtigung.';
            } else if (error.code === 2) {  
                errorMessage = 'Standort nicht verfügbar. Bitte versuchen Sie es später erneut.';
            } else if (error.code === 3) {
                errorMessage = 'Standortabfrage Timeout. Bitte versuchen Sie es erneut.';
            }
            
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert(`❌ ${errorMessage}`);
            }
            
            hapticFeedback('error');
        } finally {
            setLocationLoading(false);
        }
    };

    const loadRadiusOptions = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/search-radius-options`);
            if (response.ok) {
                const data = await response.json();
                setRadiusOptions(data.data.radius_options || []);
            }
        } catch (error) {
            console.error('❌ Failed to load radius options:', error);
        }
    };

    const handleBackClick = () => {
        hapticFeedback('light');
        if (currentView === 'main') {
            onBack();
        } else {
            setCurrentView('main');
        }
    };

    const loadPopularCities = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/cities/popular`);
            if (response.ok) {
                const data = await response.json();
                setCities(data.data.cities || []);
            }
        } catch (error) {
            console.error('❌ Failed to load popular cities:', error);
        }
    };

    const searchCities = async (query) => {
        if (!query || query.length < 2) return;
        
        try {
            const response = await fetch(`${backendUrl}/api/cities/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const data = await response.json();
                setCities(data.data.cities || []);
            }
        } catch (error) {
            console.error('❌ City search failed:', error);
        }
    };

    const loadSubscriptions = async () => {
        try {
            const response = await fetch(`${backendUrl}/api/job-subscriptions`, {
                headers: {
                    'Authorization': `Bearer ${user.token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setSubscriptions(data.data || []);
            }
        } catch (error) {
            console.error('❌ Failed to load subscriptions:', error);
        }
    };

    const performEnhancedJobSearch = async () => {
        setLoading(true);
        hapticFeedback('light');
        
        try {
            const searchParams = {
                ...searchFilters,
                user_coordinates: userLocation
            };
            
            const response = await fetch(`${backendUrl}/api/job-search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': user?.token ? `Bearer ${user.token}` : ''
                },
                body: JSON.stringify(searchParams)
            });
            
            if (response.ok) {
                const data = await response.json();
                setSearchResults(data.data);
                setJobs(data.data.jobs || []);
                setCurrentView('results');
                hapticFeedback('success');
            } else {
                throw new Error('Search failed');
            }
            
        } catch (error) {
            console.error('❌ Enhanced job search failed:', error);
            hapticFeedback('error');
            
            if (isTelegramWebApp()) {
                telegramWebApp.showAlert('❌ Fehler bei der Stellensuche. Bitte versuchen Sie es erneut.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Enhanced main view with spectacular design
    const renderEnhancedMainView = () => (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Header with location info */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-b-3xl shadow-xl">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <Briefcase className="w-7 h-7" />
                            JobSuche
                        </h1>
                        <p className="text-blue-100 text-sm">Finden Sie Ihren Traumjob in Deutschland</p>
                    </div>
                    <div className="text-right">
                        {userLocation ? (
                            <div className="flex items-center gap-1 text-green-200 text-sm">
                                <Navigation className="w-4 h-4" />
                                Standort aktiv
                            </div>
                        ) : (
                            <button
                                onClick={getCurrentLocation}
                                disabled={locationLoading}
                                className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full text-sm hover:bg-white/30 transition-all"
                            >
                                {locationLoading ? (
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <MapPin className="w-4 h-4" />
                                )}
                                Standort
                            </button>
                        )}
                    </div>
                </div>
                
                {/* Quick stats */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/10 rounded-2xl p-3 text-center">
                        <div className="text-lg font-bold">{jobs.length || '0'}</div>
                        <div className="text-xs text-blue-100">Gefunden</div>
                    </div>
                    <div className="bg-white/10 rounded-2xl p-3 text-center">
                        <div className="text-lg font-bold">{searchFilters.radius}km</div>
                        <div className="text-xs text-blue-100">Radius</div>
                    </div>
                    <div className="bg-white/10 rounded-2xl p-3 text-center">
                        <div className="text-lg font-bold">{subscriptions.length || '0'}</div>
                        <div className="text-xs text-blue-100">Alerts</div>
                    </div>
                </div>
            </div>

            {/* Enhanced search section */}
            <div className="p-4 space-y-4">
                {/* Search input */}
                <div className="relative">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Suchbegriff (z.B. Software Developer, Marketing Manager...)"
                        value={searchFilters.search_query}
                        onChange={(e) => setSearchFilters(prev => ({ ...prev, search_query: e.target.value }))}
                        className="w-full pl-12 pr-4 py-4 bg-white rounded-2xl border-2 border-gray-100 focus:border-blue-500 focus:outline-none text-gray-800 placeholder-gray-400 shadow-lg"
                    />
                </div>

                {/* Location input with enhanced dropdown */}
                <div className="relative">
                    <div className="flex gap-2">
                        <div className="flex-1 relative">
                            <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Stadt oder PLZ (z.B. Berlin, 10115...)"
                                value={citySearchInput}
                                onChange={(e) => {
                                    setCitySearchInput(e.target.value);
                                    setShowCityDropdown(true);
                                    if (e.target.value.length >= 2) {
                                        searchCities(e.target.value);
                                    } else {
                                        loadPopularCities();
                                    }
                                }}
                                onFocus={() => setShowCityDropdown(true)}
                                className="w-full pl-12 pr-4 py-4 bg-white rounded-2xl border-2 border-gray-100 focus:border-blue-500 focus:outline-none text-gray-800 placeholder-gray-400 shadow-lg"
                            />
                        </div>
                        <button
                            onClick={getCurrentLocation}
                            disabled={locationLoading}
                            className="bg-blue-500 text-white p-4 rounded-2xl shadow-lg hover:bg-blue-600 transition-all disabled:opacity-50"
                        >
                            {locationLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Navigation className="w-5 h-5" />
                            )}
                        </button>
                    </div>

                    {/* Enhanced city dropdown */}
                    {showCityDropdown && cities.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-gray-100 max-h-60 overflow-y-auto z-50">
                            {cities.map((city, index) => (
                                <button
                                    key={index}
                                    onClick={() => {
                                        setSearchFilters(prev => ({ ...prev, location: city.name }));
                                        setCitySearchInput(city.name);
                                        setShowCityDropdown(false);
                                        hapticFeedback('light');
                                    }}
                                    className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors flex items-center justify-between border-b border-gray-50 last:border-b-0"
                                >
                                    <div>
                                        <div className="font-medium text-gray-800">{city.name}</div>
                                        <div className="text-sm text-gray-500">{city.state}</div>
                                    </div>
                                    {city.population && (
                                        <div className="text-xs text-gray-400">
                                            {Math.round(city.population / 1000)}k Einwohner
                                        </div>
                                    )}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Enhanced radius selector */}
                <div className="bg-white rounded-2xl p-4 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <Radar className="w-5 h-5 text-blue-500" />
                            <span className="font-medium text-gray-800">Suchradius</span>
                        </div>
                        <span className="text-sm text-gray-500">{searchFilters.radius} km</span>
                    </div>
                    <div className="grid grid-cols-6 gap-2">
                        {[5, 10, 25, 50, 100, 200].map(radius => (
                            <button
                                key={radius}
                                onClick={() => {
                                    setSearchFilters(prev => ({ ...prev, radius }));
                                    hapticFeedback('light');
                                }}
                                className={`py-2 px-3 rounded-xl text-sm font-medium transition-all ${
                                    searchFilters.radius === radius
                                        ? 'bg-blue-500 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                            >
                                {radius}km
                            </button>
                        ))}
                    </div>
                </div>

                {/* Enhanced filters toggle */}
                <button
                    onClick={() => {
                        setShowAdvancedFilters(!showAdvancedFilters);
                        hapticFeedback('light');
                    }}
                    className="w-full bg-white rounded-2xl p-4 shadow-lg flex items-center justify-between hover:bg-gray-50 transition-all"
                >
                    <div className="flex items-center gap-3">
                        <Filter className="w-5 h-5 text-blue-500" />
                        <span className="font-medium text-gray-800">Erweiterte Filter</span>
                    </div>
                    <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} />
                </button>

                {/* Advanced filters */}
                {showAdvancedFilters && (
                    <div className="space-y-4 bg-white rounded-2xl p-4 shadow-lg">
                        {/* Language level */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                                <Languages className="w-4 h-4" />
                                Deutschkenntnisse
                            </label>
                            <div className="grid grid-cols-3 gap-2">
                                {languageLevels.map(level => (
                                    <button
                                        key={level.value}
                                        onClick={() => {
                                            setSearchFilters(prev => ({ 
                                                ...prev, 
                                                language_level: prev.language_level === level.value ? '' : level.value 
                                            }));
                                            hapticFeedback('light');
                                        }}
                                        className={`py-2 px-3 rounded-xl text-sm font-medium transition-all ${
                                            searchFilters.language_level === level.value
                                                ? 'bg-green-500 text-white shadow-md'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                        title={level.description}
                                    >
                                        {level.value}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Work time */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Arbeitszeit
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                {workTimeOptions.map(option => (
                                    <button
                                        key={option.value}
                                        onClick={() => {
                                            setSearchFilters(prev => ({ 
                                                ...prev, 
                                                work_time: prev.work_time === option.value ? '' : option.value 
                                            }));
                                            hapticFeedback('light');
                                        }}
                                        className={`py-3 px-4 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                                            searchFilters.work_time === option.value
                                                ? 'bg-purple-500 text-white shadow-md'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                        title={option.description}
                                    >
                                        {option.icon}
                                        <span className="truncate">{option.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Job category */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                                <Building2 className="w-4 h-4" />
                                Branche
                            </label>
                            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                                {jobCategories.map(category => (
                                    <button
                                        key={category.value}
                                        onClick={() => {
                                            setSearchFilters(prev => ({ 
                                                ...prev, 
                                                category: prev.category === category.value ? '' : category.value 
                                            }));
                                            hapticFeedback('light');
                                        }}
                                        className={`py-2 px-3 rounded-xl text-sm font-medium transition-all text-left ${
                                            searchFilters.category === category.value
                                                ? 'bg-orange-500 text-white shadow-md'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                        title={category.description}
                                    >
                                        <div className="truncate">{category.label}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Additional options */}
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => {
                                    setSearchFilters(prev => ({ ...prev, remote: prev.remote === true ? null : true }));
                                    hapticFeedback('light');
                                }}
                                className={`py-3 px-4 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                                    searchFilters.remote === true
                                        ? 'bg-green-500 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                            >
                                <Wifi className="w-4 h-4" />
                                Remote
                            </button>
                            <button
                                onClick={() => {
                                    setSearchFilters(prev => ({ ...prev, visa_sponsorship: prev.visa_sponsorship === true ? null : true }));
                                    hapticFeedback('light');
                                }}
                                className={`py-3 px-4 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                                    searchFilters.visa_sponsorship === true
                                        ? 'bg-blue-500 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                            >
                                <Globe className="w-4 h-4" />
                                Visa Support
                            </button>
                        </div>
                    </div>
                )}

                {/* Enhanced search button */}
                <button
                    onClick={performEnhancedJobSearch}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-2xl font-semibold text-lg shadow-xl hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
                >
                    {loading ? (
                        <>
                            <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Suche läuft...
                        </>
                    ) : (
                        <>
                            <Search className="w-6 h-6" />
                            Jobs finden
                            <Sparkles className="w-5 h-5" />
                        </>
                    )}
                </button>

                {/* AI Assistant Button */}
                <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 shadow-xl">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                            <Brain className="w-7 h-7 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-xl font-bold text-white">AI-Рекрутер</h3>
                            <p className="text-emerald-100 text-sm">Персональный помощник для поиска работы</p>
                        </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                        <div className="flex items-center gap-2 text-emerald-100 text-sm">
                            <CheckCircle className="w-4 h-4" />
                            <span>Анализ совместимости с вакансиями</span>
                        </div>
                        <div className="flex items-center gap-2 text-emerald-100 text-sm">
                            <CheckCircle className="w-4 h-4" />
                            <span>Перевод вакансий на любой язык</span>
                        </div>
                        <div className="flex items-center gap-2 text-emerald-100 text-sm">
                            <CheckCircle className="w-4 h-4" />
                            <span>Генерация сопроводительных писем</span>
                        </div>
                        <div className="flex items-center gap-2 text-emerald-100 text-sm">
                            <CheckCircle className="w-4 h-4" />
                            <span>Уведомления прямо в Telegram</span>
                        </div>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-2">
                        <button
                            onClick={() => setCurrentView('ai-assistant')}
                            className="w-full bg-white text-emerald-600 py-3 px-6 rounded-xl font-semibold hover:bg-gray-50 transition-all flex items-center justify-center gap-2"
                        >
                            <Bot className="w-5 h-5" />
                            Запустить AI-Рекрутера
                            <ArrowRight className="w-4 h-4" />
                        </button>
                        
                        <button
                            onClick={() => setCurrentView('revolutionary-ai')}
                            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-6 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all flex items-center justify-center gap-2 shadow-lg"
                        >
                            <Rocket className="w-5 h-5" />
                            🎯 Идеальный AI
                            <Sparkles className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Nearby cities suggestion */}
                {nearestCities.length > 0 && (
                    <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <MapPin className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-green-800">Städte in Ihrer Nähe</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {nearestCities.slice(0, 5).map((city, index) => (
                                <button
                                    key={index}
                                    onClick={() => {
                                        setSearchFilters(prev => ({ ...prev, location: city.name }));
                                        setCitySearchInput(city.name);
                                        hapticFeedback('light');
                                    }}
                                    className="bg-white px-3 py-2 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-all shadow-sm flex items-center gap-1"
                                >
                                    {city.name}
                                    <span className="text-xs text-gray-500">({Math.round(city.distance)} km)</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );

    // Enhanced results view
    const renderEnhancedResults = () => (
        <div className="min-h-screen bg-gray-50">
            {/* Results header */}
            <div className="bg-white p-4 shadow-sm border-b border-gray-200">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xl font-bold text-gray-800">Suchergebnisse</h2>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">
                            {searchResults?.total_found || 0} von {searchResults?.total_available || 0}
                        </span>
                        <div className="flex bg-gray-100 rounded-lg p-1">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-2 rounded-md transition-all ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'text-gray-600'}`}
                            >
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                                </svg>
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-2 rounded-md transition-all ${viewMode === 'list' ? 'bg-blue-500 text-white' : 'text-gray-600'}`}
                            >
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Search summary */}
                <div className="flex flex-wrap gap-2 text-sm">
                    {searchFilters.search_query && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            "{searchFilters.search_query}"
                        </span>
                    )}
                    {searchFilters.location && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {searchFilters.location} ({searchFilters.radius}km)
                        </span>
                    )}
                    {searchFilters.language_level && (
                        <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                            {searchFilters.language_level}
                        </span>
                    )}
                    {searchFilters.work_time && (
                        <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                            {workTimeOptions.find(w => w.value === searchFilters.work_time)?.label}
                        </span>
                    )}
                </div>
            </div>

            {/* Jobs list */}
            <div className="p-4">
                {jobs.length === 0 ? (
                    <div className="text-center py-12">
                        <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-800 mb-2">Keine Stellenangebote gefunden</h3>
                        <p className="text-gray-600 mb-4">Versuchen Sie es mit anderen Suchkriterien</p>
                        <button
                            onClick={() => setCurrentView('main')}
                            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                        >
                            Neue Suche starten
                        </button>
                    </div>
                ) : (
                    <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : 'space-y-4'}>
                        {jobs.map((job, index) => (
                            <div
                                key={job.id || index}
                                onClick={() => {
                                    setSelectedJob(job);
                                    hapticFeedback('light');
                                }}
                                className="bg-white rounded-2xl p-4 shadow-sm hover:shadow-lg transition-all cursor-pointer border border-gray-100"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1">
                                        <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2">
                                            {job.title}
                                        </h3>
                                        <p className="text-gray-600 text-sm mb-2">
                                            {job.company_name}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        {job.match_score && (
                                            <div className={`text-xs px-2 py-1 rounded-full ${
                                                job.match_score >= 80 ? 'bg-green-100 text-green-800' :
                                                job.match_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-gray-100 text-gray-800'
                                            }`}>
                                                {job.match_score}% Match
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                                    {job.location?.city && (
                                        <div className="flex items-center gap-1">
                                            <MapPin className="w-4 h-4" />
                                            <span>{job.location.city}</span>
                                            {job.location.distance_km && (
                                                <span className="text-gray-500">
                                                    ({Math.round(job.location.distance_km)} km)
                                                </span>
                                            )}
                                        </div>
                                    )}
                                    {job.dates?.published && (
                                        <div className="flex items-center gap-1">
                                            <Calendar className="w-4 h-4" />
                                            <span>{new Date(job.dates.published).toLocaleDateString('de-DE')}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="flex flex-wrap gap-2 mb-3">
                                    {job.language_requirement?.level && (
                                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                                            Deutsch {job.language_requirement.level}
                                        </span>
                                    )}
                                    {job.remote_possible && (
                                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                                            Remote möglich
                                        </span>
                                    )}
                                    {job.work_time && (
                                        <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">
                                            {workTimeOptions.find(w => w.value === job.work_time)?.label || job.work_time}
                                        </span>
                                    )}
                                </div>

                                {job.salary_info?.available && (
                                    <div className="flex items-center gap-1 text-green-600 text-sm mb-2">
                                        <Euro className="w-4 h-4" />
                                        <span>
                                            {job.salary_info.range} {job.salary_info.currency}
                                            {job.salary_info.period === 'yearly' ? '/Jahr' : '/Monat'}
                                        </span>
                                    </div>
                                )}

                                <div className="flex items-center justify-between mb-3">
                                    <div className="text-sm text-gray-500">
                                        {job.profession}
                                    </div>
                                    <ArrowRight className="w-4 h-4 text-gray-400" />
                                </div>

                                {/* AI Actions */}
                                <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setSelectedJob(job);
                                            setCurrentView('ai-assistant');
                                            hapticFeedback('light');
                                        }}
                                        className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white py-2 px-3 rounded-lg text-xs font-medium hover:from-emerald-600 hover:to-teal-700 transition-all flex items-center justify-center gap-1"
                                    >
                                        <Brain className="w-4 h-4" />
                                        AI-Анализ
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setSelectedJob(job);
                                            setCurrentView('ai-assistant');
                                            hapticFeedback('light');
                                        }}
                                        className="flex-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-2 px-3 rounded-lg text-xs font-medium hover:from-blue-600 hover:to-indigo-700 transition-all flex items-center justify-center gap-1"
                                    >
                                        <Globe className="w-4 h-4" />
                                        Перевод
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Back to search button */}
            <div className="fixed bottom-4 right-4">
                <button
                    onClick={() => setCurrentView('main')}
                    className="bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition-all"
                >
                    <Search className="w-6 h-6" />
                </button>
            </div>
        </div>
    );

    // Job detail modal
    const renderJobDetailModal = () => {
        if (!selectedJob) return null;

        return (
            <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto">
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-800">Stellendetails</h2>
                            <button
                                onClick={() => setSelectedJob(null)}
                                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-all"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <h3 className="font-semibold text-gray-800 mb-2">{selectedJob.title}</h3>
                                <p className="text-gray-600">{selectedJob.company_name}</p>
                            </div>

                            {selectedJob.location && (
                                <div className="flex items-center gap-2 text-gray-600">
                                    <MapPin className="w-4 h-4" />
                                    <span>{selectedJob.location.city}, {selectedJob.location.state}</span>
                                    {selectedJob.location.distance_km && (
                                        <span className="text-gray-500">
                                            ({Math.round(selectedJob.location.distance_km)} km entfernt)
                                        </span>
                                    )}
                                </div>
                            )}

                            {selectedJob.description && (
                                <div>
                                    <h4 className="font-medium text-gray-800 mb-2">Beschreibung</h4>
                                    <p className="text-gray-600 text-sm whitespace-pre-line">
                                        {selectedJob.description}
                                    </p>
                                </div>
                            )}

                            {selectedJob.requirements?.length > 0 && (
                                <div>
                                    <h4 className="font-medium text-gray-800 mb-2">Anforderungen</h4>
                                    <ul className="text-gray-600 text-sm space-y-1">
                                        {selectedJob.requirements.map((req, index) => (
                                            <li key={index} className="flex items-start gap-2">
                                                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                {req}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {selectedJob.benefits?.length > 0 && (
                                <div>
                                    <h4 className="font-medium text-gray-800 mb-2">Vorteile</h4>
                                    <ul className="text-gray-600 text-sm space-y-1">
                                        {selectedJob.benefits.map((benefit, index) => (
                                            <li key={index} className="flex items-start gap-2">
                                                <Star className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                                                {benefit}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-2">
                                {selectedJob.language_requirement?.level && (
                                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                                        Deutsch {selectedJob.language_requirement.level}
                                    </span>
                                )}
                                {selectedJob.remote_possible && (
                                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                                        Remote möglich
                                    </span>
                                )}
                                {selectedJob.visa_sponsorship && (
                                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                                        Visa Support
                                    </span>
                                )}
                            </div>

                            {selectedJob.external_url && (
                                <button
                                    onClick={() => {
                                        if (isTelegramWebApp()) {
                                            telegramWebApp.openLink(selectedJob.external_url);
                                        } else {
                                            window.open(selectedJob.external_url, '_blank');
                                        }
                                        hapticFeedback('light');
                                    }}
                                    className="w-full bg-blue-500 text-white py-3 px-4 rounded-xl font-medium hover:bg-blue-600 transition-all flex items-center justify-center gap-2"
                                >
                                    <ExternalLink className="w-5 h-5" />
                                    Stellenanzeige öffnen
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {currentView === 'main' && renderEnhancedMainView()}
            {currentView === 'results' && renderEnhancedResults()}
            {currentView === 'ai-assistant' && (
                <AIJobAssistant 
                    onBack={() => setCurrentView('main')}
                    initialJob={selectedJob}
                />
            )}
            {currentView === 'revolutionary-ai' && (
                <RevolutionaryAIRecruiter 
                    onBack={() => setCurrentView('main')}
                    aiProfile={null}
                />
            )}
            {selectedJob && renderJobDetailModal()}
        </div>
    );
};

export default EnhancedTelegramJobSearch;