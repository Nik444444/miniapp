import React, { useEffect, useState, useContext } from 'react';
import { MessageCircle, ArrowLeft, Settings, Share2, Star, Smartphone, Shield, Bell, Zap } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const TelegramWebApp = ({ children }) => {
    const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);
    const [telegramUser, setTelegramUser] = useState(null);
    const [theme, setTheme] = useState('light');
    const [viewportHeight, setViewportHeight] = useState(window.innerHeight);
    const [isExpanded, setIsExpanded] = useState(false);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        // Проверка на Telegram Web App
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            setIsTelegramWebApp(true);
            
            // Настройка Telegram Web App
            tg.ready();
            tg.expand();
            tg.enableClosingConfirmation();
            
            // Получение данных пользователя
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                setTelegramUser(tg.initDataUnsafe.user);
            }
            
            // Настройка темы
            const currentTheme = tg.colorScheme || 'light';
            setTheme(currentTheme);
            
            // Обновление CSS переменных для темы
            const root = document.documentElement;
            if (currentTheme === 'dark') {
                root.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#1a1a1a');
                root.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#ffffff');
                root.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#8e8e93');
                root.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#6ab7ff');
                root.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#6ab7ff');
                root.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
                root.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#2c2c2e');
            } else {
                root.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
                root.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
                root.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#8e8e93');
                root.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#6ab7ff');
                root.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#6ab7ff');
                root.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
                root.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f2f2f2');
            }
            
            // Настройка главной кнопки (скрыта по умолчанию)
            tg.MainButton.hide();
            
            // Настройка back кнопки
            tg.BackButton.hide();
            
            // Настройка settings кнопки
            tg.SettingsButton.hide();
            
            // Обработка viewport изменений
            tg.onEvent('viewportChanged', () => {
                setViewportHeight(tg.viewportHeight);
                setIsExpanded(tg.isExpanded);
            });
            
            // Обработка изменения темы
            tg.onEvent('themeChanged', () => {
                setTheme(tg.colorScheme || 'light');
            });
            
            // Обработка событий кнопок (MainButton отключена)
            // tg.onEvent('mainButtonClicked', () => {
            //     handleMainButtonClick();
            // });
            
            tg.onEvent('backButtonClicked', () => {
                handleBackButtonClick();
            });
            
            tg.onEvent('settingsButtonClicked', () => {
                handleSettingsButtonClick();
            });
            
            // Настройка цветов header
            tg.setHeaderColor(tg.themeParams.secondary_bg_color || '#f8fafc');
            tg.setBackgroundColor(tg.themeParams.bg_color || '#ffffff');
            
            // Haptic feedback при запуске
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('light');
            }
            
            // Отправка данных о пользователе в приложение
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                sendTelegramUserData(tg.initDataUnsafe.user, tg.initData);
            }
        }
    }, []);

    const sendTelegramUserData = async (telegramUser, initData) => {
        try {
            // Отправляем данные пользователя на backend для верификации
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/telegram/auth`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user: telegramUser,
                    initData: initData
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Telegram user verified:', data);
            }
        } catch (error) {
            console.error('Error sending Telegram user data:', error);
        }
    };

    const handleMainButtonClick = () => {
        // Логика для главной кнопки
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.click();
        }
        
        // Haptic feedback
        if (window.Telegram && window.Telegram.WebApp.HapticFeedback) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
        }
    };

    const handleBackButtonClick = () => {
        // Логика для кнопки назад
        window.history.back();
    };

    const handleSettingsButtonClick = () => {
        // Логика для кнопки настроек
        console.log('Settings button clicked');
    };

    const handleShare = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            const url = window.location.href;
            const text = 'Попробуйте German Letter AI для анализа документов!';
            
            // Haptic feedback
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('light');
            }
            
            tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`);
        }
    };

    const handleRate = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            
            // Haptic feedback
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('medium');
            }
            
            tg.showPopup({
                title: 'Оценить приложение',
                message: 'Понравилось ли вам наше приложение?',
                buttons: [
                    {
                        id: 'rate_5',
                        type: 'default',
                        text: '⭐⭐⭐⭐⭐ Отлично!'
                    },
                    {
                        id: 'rate_4',
                        type: 'default',
                        text: '⭐⭐⭐⭐ Хорошо'
                    },
                    {
                        id: 'rate_3',
                        type: 'default',
                        text: '⭐⭐⭐ Неплохо'
                    },
                    {
                        id: 'feedback',
                        type: 'default',
                        text: '💬 Оставить отзыв'
                    },
                    {
                        id: 'cancel',
                        type: 'cancel'
                    }
                ]
            }, (buttonId) => {
                if (buttonId.startsWith('rate_')) {
                    tg.showAlert('Спасибо за оценку!');
                    // Haptic feedback
                    if (tg.HapticFeedback) {
                        tg.HapticFeedback.notificationOccurred('success');
                    }
                } else if (buttonId === 'feedback') {
                    tg.openTelegramLink('https://t.me/germanletterai_support');
                }
            });
        }
    };

    const showMainButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.MainButton.show();
        }
    };

    const hideMainButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.MainButton.hide();
        }
    };

    const showBackButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.BackButton.show();
        }
    };

    const hideBackButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.BackButton.hide();
        }
    };

    const showSettingsButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.SettingsButton.show();
        }
    };

    const hideSettingsButton = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.SettingsButton.hide();
        }
    };

    const sendData = (data) => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.sendData(JSON.stringify(data));
        }
    };

    const requestContact = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.requestContact((contact) => {
                console.log('Contact received:', contact);
            });
        }
    };

    const requestLocation = () => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.requestLocation((location) => {
                console.log('Location received:', location);
            });
        }
    };

    const showAlert = (message) => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.showAlert(message);
        }
    };

    const showConfirm = (message, callback) => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.showConfirm(message, callback);
        }
    };

    const openInvoice = (invoiceUrl) => {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.openInvoice(invoiceUrl);
        }
    };

    if (!isTelegramWebApp) {
        return children;
    }

    return (
        <div className={`telegram-web-app ${theme === 'dark' ? 'dark' : ''}`} style={{ height: viewportHeight }}>
            {/* Telegram Web App Header */}
            <div className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200 dark:bg-gray-800/80 dark:border-gray-700">
                <div className="flex items-center justify-between p-4">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-full">
                            <Smartphone className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                                German Letter AI
                            </h1>
                            {telegramUser && (
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Привет, {telegramUser.first_name}!
                                </p>
                            )}
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={handleShare}
                            className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 transition-colors"
                        >
                            <Share2 className="h-5 w-5" />
                        </button>
                        <button
                            onClick={handleRate}
                            className="p-2 text-gray-600 hover:text-yellow-600 dark:text-gray-400 dark:hover:text-yellow-400 transition-colors"
                        >
                            <Star className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Telegram-specific status bar */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-2 text-center text-sm">
                <div className="flex items-center justify-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span>Telegram Web App</span>
                    </div>
                    <div className="hidden sm:flex items-center space-x-2">
                        <Shield className="h-4 w-4" />
                        <span>Защищено</span>
                    </div>
                    <div className="hidden sm:flex items-center space-x-2">
                        <Zap className="h-4 w-4" />
                        <span>Быстро</span>
                    </div>
                </div>
            </div>

            {/* Telegram-specific optimizations */}
            <div className="telegram-content" style={{ paddingBottom: '80px' }}>
                {React.cloneElement(children, {
                    telegramUser,
                    isTelegramWebApp,
                    theme,
                    viewportHeight,
                    isExpanded,
                    showMainButton,
                    hideMainButton,
                    showBackButton,
                    hideBackButton,
                    showSettingsButton,
                    hideSettingsButton,
                    sendData,
                    requestContact,
                    requestLocation,
                    showAlert,
                    showConfirm,
                    openInvoice,
                    handleShare,
                    handleRate
                })}
            </div>

            {/* Telegram Web App Footer */}
            <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200 dark:bg-gray-800/95 dark:border-gray-700 p-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                        <MessageCircle className="h-4 w-4" />
                        <span>Работает в Telegram</span>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            <span>Онлайн</span>
                        </div>
                        {telegramUser && (
                            <div className="flex items-center space-x-2 text-sm">
                                <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs">
                                    {telegramUser.first_name?.[0] || 'U'}
                                </div>
                                <span className="text-gray-600 dark:text-gray-400">
                                    {telegramUser.first_name}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TelegramWebApp;