import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import { 
    Search, 
    MapPin, 
    Euro, 
    Home, 
    Filter, 
    Bell,
    BellRing,
    Heart,
    ArrowLeft,
    AlertTriangle,
    CheckCircle,
    XCircle,
    ExternalLink,
    Calculator,
    Bot,
    Shield,
    TrendingUp,
    Clock,
    Loader
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback,
    showTelegramAlert
} from '../utils/telegramWebApp';

const TelegramHousingSearch = ({ onBack }) => {
    const { user } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('search');
    const [searchParams, setSearchParams] = useState({
        city: '',
        max_price: '',
        property_type: 'wohnung',
        radius: ''
    });
    const [searchResults, setSearchResults] = useState([]);
    const [selectedListing, setSelectedListing] = useState(null);
    const [subscriptions, setSubscriptions] = useState([]);
    const [neighborhoodAnalysis, setNeighborhoodAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Popular German cities
    const popularCities = [
        'Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt',
        'Stuttgart', 'Düsseldorf', 'Dortmund', 'Leipzig', 'Dresden'
    ];

    // Telegram WebApp setup
    useEffect(() => {
        if (isTelegramWebApp()) {
            const tg = getTelegramWebApp();
            if (tg) {
                tg.ready();
                tg.BackButton.show();
                tg.BackButton.onClick(() => {
                    if (currentView !== 'search') {
                        setCurrentView('search');
                        setSelectedListing(null);
                    } else {
                        onBack();
                    }
                });
                
                tg.setHeaderColor('#1a1a2e');
                tg.setBackgroundColor('#1a1a2e');
            }
        }

        // Load subscriptions on mount
        loadSubscriptions();

        return () => {
            if (isTelegramWebApp()) {
                const tg = getTelegramWebApp();
                if (tg) {
                    tg.BackButton.hide();
                }
            }
        };
    }, [currentView, onBack]);

    const loadSubscriptions = async () => {
        try {
            const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
            const token = localStorage.getItem('token');
            
            const response = await fetch(`${backendUrl}/api/housing-subscriptions`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setSubscriptions(data.data?.subscriptions || []);
            }
        } catch (error) {
            console.error('Failed to load subscriptions:', error);
        }
    };

    const handleSearch = async () => {
        if (!searchParams.city.trim()) {
            setError('Пожалуйста, укажите город для поиска');
            return;
        }

        setIsLoading(true);
        setError(null);
        
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }

        try {
            const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
            const token = localStorage.getItem('token');
            
            const response = await fetch(`${backendUrl}/api/housing-search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    city: searchParams.city,
                    max_price: searchParams.max_price ? parseInt(searchParams.max_price) : null,
                    property_type: searchParams.property_type,
                    radius: searchParams.radius ? parseInt(searchParams.radius) : null
                })
            });

            if (response.ok) {
                const data = await response.json();
                setSearchResults(data.data?.listings || []);
                setCurrentView('results');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                    showTelegramAlert(`Найдено ${data.data?.total_found || 0} объявлений`);
                }
            } else {
                const errorData = await response.json();
                if (response.status === 401 || response.status === 403) {
                    throw new Error('Необходимо войти в систему для поиска жилья');
                } else if (errorData.detail) {
                    throw new Error(errorData.detail);
                } else {
                    throw new Error('Ошибка поиска');
                }
            }
        } catch (error) {
            setError('Ошибка поиска жилья. Попробуйте позже.');
            console.error('Search failed:', error);
            
            if (isTelegramWebApp()) {
                hapticFeedback('error');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubscribe = async () => {
        if (!searchParams.city.trim()) {
            setError('Укажите параметры для подписки');
            return;
        }

        try {
            const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
            const token = localStorage.getItem('token');
            
            const response = await fetch(`${backendUrl}/api/housing-subscriptions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    city: searchParams.city,
                    max_price: searchParams.max_price ? parseInt(searchParams.max_price) : null,
                    property_type: searchParams.property_type,
                    radius: searchParams.radius ? parseInt(searchParams.radius) : null
                })
            });

            if (response.ok) {
                const data = await response.json();
                loadSubscriptions();
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                    showTelegramAlert('Подписка создана! Вы получите уведомления о новых предложениях.');
                }
            } else {
                const errorData = await response.json();
                if (response.status === 401 || response.status === 403) {
                    throw new Error('Необходимо войти в систему для создания подписки');
                } else if (errorData.detail) {
                    throw new Error(errorData.detail);
                } else {
                    throw new Error('Ошибка создания подписки');
                }
            }
        } catch (error) {
            setError('Ошибка создания подписки');
            console.error('Subscription failed:', error);
        }
    };

    const handleNeighborhoodAnalysis = async (city, district = null) => {
        try {
            setIsLoading(true);
            const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
            const token = localStorage.getItem('token');
            
            const response = await fetch(`${backendUrl}/api/housing-neighborhood-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    city: city,
                    district: district
                })
            });

            if (response.ok) {
                const data = await response.json();
                setNeighborhoodAnalysis(data.data);
                setCurrentView('neighborhood');
                
                if (isTelegramWebApp()) {
                    hapticFeedback('success');
                }
            } else {
                throw new Error('Ошибка анализа района');
            }
        } catch (error) {
            setError('Ошибка анализа района');
            console.error('Neighborhood analysis failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getRiskColor = (scamScore) => {
        if (scamScore >= 50) return 'text-red-400';
        if (scamScore >= 25) return 'text-yellow-400';
        if (scamScore >= 10) return 'text-orange-400';
        return 'text-green-400';
    };

    const formatPrice = (price) => {
        return price ? `${price.toLocaleString()}€` : 'N/A';
    };

    const formatArea = (area) => {
        return area ? `${area}м²` : 'N/A';
    };

    // Search View
    if (currentView === 'search') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
                <div className="container mx-auto p-4 max-w-md">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Home className="h-8 w-8 text-white" />
                        </div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                            Поиск жилья в Германии
                        </h1>
                        <p className="text-slate-300 mt-2">AI-поиск с детектором мошенничества</p>
                    </div>

                    {/* Search Form */}
                    <div className="space-y-6">
                        {/* City Input */}
                        <div>
                            <label className="block text-sm font-medium mb-3 text-slate-300">
                                <MapPin className="inline w-4 h-4 mr-2" />
                                Город
                            </label>
                            <input
                                type="text"
                                value={searchParams.city}
                                onChange={(e) => setSearchParams({...searchParams, city: e.target.value})}
                                placeholder="Введите название города"
                                className="w-full p-4 bg-slate-800/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                            />
                            
                            {/* Popular Cities */}
                            <div className="mt-3">
                                <p className="text-xs text-slate-400 mb-2">Популярные города:</p>
                                <div className="flex flex-wrap gap-2">
                                    {popularCities.slice(0, 5).map(city => (
                                        <button
                                            key={city}
                                            onClick={() => setSearchParams({...searchParams, city})}
                                            className="px-3 py-1 bg-slate-700/50 rounded-lg text-xs text-slate-300 hover:bg-purple-600/30 transition-colors"
                                        >
                                            {city}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Max Price */}
                        <div>
                            <label className="block text-sm font-medium mb-3 text-slate-300">
                                <Euro className="inline w-4 h-4 mr-2" />
                                Максимальная цена
                            </label>
                            <input
                                type="number"
                                value={searchParams.max_price}
                                onChange={(e) => setSearchParams({...searchParams, max_price: e.target.value})}
                                placeholder="например, 800"
                                className="w-full p-4 bg-slate-800/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                            />
                        </div>

                        {/* Property Type */}
                        <div>
                            <label className="block text-sm font-medium mb-3 text-slate-300">
                                <Home className="inline w-4 h-4 mr-2" />
                                Тип жилья
                            </label>
                            <select
                                value={searchParams.property_type}
                                onChange={(e) => setSearchParams({...searchParams, property_type: e.target.value})}
                                className="w-full p-4 bg-slate-800/50 border border-slate-600 rounded-xl text-white focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                            >
                                <option value="wohnung">Квартира</option>
                                <option value="zimmer">Комната/WG</option>
                                <option value="haus">Дом</option>
                            </select>
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/20 border border-red-500 rounded-xl">
                                <p className="text-red-300 text-sm">{error}</p>
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className="space-y-3">
                            <button
                                onClick={handleSearch}
                                disabled={isLoading}
                                className="w-full p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                            >
                                {isLoading ? (
                                    <Loader className="animate-spin w-5 h-5 mr-2" />
                                ) : (
                                    <Search className="w-5 h-5 mr-2" />
                                )}
                                {isLoading ? 'Поиск...' : 'Найти жилье'}
                            </button>

                            <button
                                onClick={handleSubscribe}
                                className="w-full p-4 bg-slate-700/50 border border-slate-600 rounded-xl font-semibold hover:bg-slate-600/50 transition-colors flex items-center justify-center"
                            >
                                <Bell className="w-5 h-5 mr-2" />
                                Создать подписку
                            </button>
                        </div>

                        {/* Subscriptions */}
                        {subscriptions.length > 0 && (
                            <div className="mt-8">
                                <h3 className="text-lg font-semibold mb-4 flex items-center">
                                    <BellRing className="w-5 h-5 mr-2 text-yellow-400" />
                                    Активные подписки
                                </h3>
                                <div className="space-y-3">
                                    {subscriptions.slice(0, 3).map((sub) => (
                                        <div key={sub.id} className="p-4 bg-slate-800/30 border border-slate-700 rounded-xl">
                                            <p className="font-medium">{sub.city}</p>
                                            <p className="text-sm text-slate-400">
                                                до {formatPrice(sub.max_price)} • {sub.property_type}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    // Results View
    if (currentView === 'results') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
                <div className="container mx-auto p-4 max-w-md">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <button
                            onClick={() => setCurrentView('search')}
                            className="p-2 bg-slate-800/50 rounded-lg"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <h2 className="text-lg font-semibold">
                            Найдено: {searchResults.length}
                        </h2>
                        <button
                            onClick={() => handleNeighborhoodAnalysis(searchParams.city)}
                            className="p-2 bg-slate-800/50 rounded-lg"
                        >
                            <TrendingUp className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Results */}
                    <div className="space-y-4">
                        {searchResults.map((listing, index) => (
                            <div
                                key={index}
                                onClick={() => setSelectedListing(listing)}
                                className="p-4 bg-slate-800/30 border border-slate-700 rounded-xl hover:bg-slate-700/30 transition-colors cursor-pointer"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <h3 className="font-semibold text-sm line-clamp-2 flex-1">
                                        {listing.title}
                                    </h3>
                                    {listing.ai_analysis?.scam_detection && (
                                        <div className={`ml-2 ${getRiskColor(listing.ai_analysis.scam_detection.scam_score)}`}>
                                            <Shield className="w-4 h-4" />
                                        </div>
                                    )}
                                </div>

                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-4">
                                        <span className="text-green-400 font-bold">
                                            {formatPrice(listing.price)}
                                        </span>
                                        {listing.area && (
                                            <span className="text-slate-300 text-sm">
                                                {formatArea(listing.area)}
                                            </span>
                                        )}
                                    </div>
                                    <span className="text-xs text-slate-400 bg-slate-700/50 px-2 py-1 rounded">
                                        {listing.source}
                                    </span>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div className="flex items-center text-slate-400 text-sm">
                                        <MapPin className="w-3 h-3 mr-1" />
                                        {listing.location}
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        {listing.ai_analysis?.cost_calculation && (
                                            <Calculator className="w-4 h-4 text-blue-400" />
                                        )}
                                        <ExternalLink className="w-4 h-4 text-slate-400" />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    // Neighborhood Analysis View
    if (currentView === 'neighborhood') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
                <div className="container mx-auto p-4 max-w-md">
                    {/* Header */}
                    <div className="flex items-center mb-6">
                        <button
                            onClick={() => setCurrentView('results')}
                            className="p-2 bg-slate-800/50 rounded-lg mr-4"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <h2 className="text-lg font-semibold">Анализ района</h2>
                    </div>

                    {/* Analysis Content */}
                    {neighborhoodAnalysis && (
                        <div className="space-y-6">
                            <div className="p-4 bg-slate-800/30 border border-slate-700 rounded-xl">
                                <div className="flex items-center mb-3">
                                    <TrendingUp className="w-5 h-5 mr-2 text-blue-400" />
                                    <span className="font-semibold">AI Анализ района</span>
                                    {neighborhoodAnalysis.ai_powered && (
                                        <Bot className="w-4 h-4 ml-2 text-green-400" />
                                    )}
                                </div>
                                <div className="text-sm text-slate-300 whitespace-pre-line">
                                    {neighborhoodAnalysis.analysis}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return null;
};

export default TelegramHousingSearch;