import React, { useState, useEffect, useContext } from 'react';
import { Download, X, Bell, Smartphone, Zap, Shield, Wifi, Clock, MessageCircle, Star, Settings, Globe } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const MobileOptimizations = () => {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [isInstallable, setIsInstallable] = useState(false);
    const [isInstalled, setIsInstalled] = useState(false);
    const [showInstallPrompt, setShowInstallPrompt] = useState(false);
    const [notificationPermission, setNotificationPermission] = useState('default');
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [isTelegram, setIsTelegram] = useState(false);
    const [telegramWebApp, setTelegramWebApp] = useState(null);
    const [networkType, setNetworkType] = useState('unknown');
    const [isLowPowerMode, setIsLowPowerMode] = useState(false);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        // Проверка установки PWA
        const checkInstallation = () => {
            if (window.matchMedia('(display-mode: standalone)').matches) {
                setIsInstalled(true);
            }
        };
        
        checkInstallation();

        // Проверка Telegram Web App
        if (window.Telegram && window.Telegram.WebApp) {
            setIsTelegram(true);
            const tg = window.Telegram.WebApp;
            setTelegramWebApp(tg);
            
            // Настройка Telegram Web App
            tg.ready();
            tg.expand();
            tg.enableClosingConfirmation();
            
            // Настройка цветовой схемы
            if (tg.themeParams) {
                applyTelegramTheme(tg.themeParams);
            }
            
            // Haptic feedback при запуске
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('light');
            }
        }

        // Обработка события установки PWA
        const handleBeforeInstallPrompt = (e) => {
            e.preventDefault();
            setDeferredPrompt(e);
            setIsInstallable(true);
        };

        // Обработка успешной установки
        const handleAppInstalled = () => {
            setIsInstalled(true);
            setIsInstallable(false);
            setShowInstallPrompt(false);
            console.log('PWA установлено!');
            
            // Telegram haptic feedback
            if (telegramWebApp && telegramWebApp.HapticFeedback) {
                telegramWebApp.HapticFeedback.notificationOccurred('success');
            }
        };

        // Обработка онлайн/оффлайн статуса
        const handleOnline = () => {
            setIsOnline(true);
            if (telegramWebApp && telegramWebApp.HapticFeedback) {
                telegramWebApp.HapticFeedback.impactOccurred('light');
            }
        };
        
        const handleOffline = () => {
            setIsOnline(false);
            if (telegramWebApp && telegramWebApp.HapticFeedback) {
                telegramWebApp.HapticFeedback.impactOccurred('heavy');
            }
        };

        // Обработка изменения сети
        const handleNetworkChange = () => {
            if (navigator.connection) {
                setNetworkType(navigator.connection.effectiveType || 'unknown');
            }
        };

        // Обработка низкого заряда батареи
        const handleBatteryChange = (battery) => {
            setIsLowPowerMode(battery.level < 0.2);
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        window.addEventListener('appinstalled', handleAppInstalled);
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        // Проверка сетевого соединения
        if (navigator.connection) {
            navigator.connection.addEventListener('change', handleNetworkChange);
            setNetworkType(navigator.connection.effectiveType || 'unknown');
        }

        // Проверка батареи
        if (navigator.getBattery) {
            navigator.getBattery().then(handleBatteryChange);
        }

        // Проверка разрешения на уведомления
        if ('Notification' in window) {
            setNotificationPermission(Notification.permission);
        }

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
            window.removeEventListener('appinstalled', handleAppInstalled);
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
            
            if (navigator.connection) {
                navigator.connection.removeEventListener('change', handleNetworkChange);
            }
        };
    }, [telegramWebApp]);

    const applyTelegramTheme = (themeParams) => {
        const root = document.documentElement;
        Object.entries(themeParams).forEach(([key, value]) => {
            root.style.setProperty(`--tg-theme-${key.replace(/_/g, '-')}`, value);
        });
    };

    const handleInstallClick = async () => {
        if (deferredPrompt) {
            // Haptic feedback
            if (telegramWebApp && telegramWebApp.HapticFeedback) {
                telegramWebApp.HapticFeedback.impactOccurred('medium');
            }
            
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                console.log('Пользователь согласился установить PWA');
                if (telegramWebApp && telegramWebApp.HapticFeedback) {
                    telegramWebApp.HapticFeedback.notificationOccurred('success');
                }
            } else {
                console.log('Пользователь отклонил установку PWA');
                if (telegramWebApp && telegramWebApp.HapticFeedback) {
                    telegramWebApp.HapticFeedback.notificationOccurred('error');
                }
            }
            
            setDeferredPrompt(null);
            setIsInstallable(false);
        }
    };

    const requestNotificationPermission = async () => {
        if ('Notification' in window) {
            // Haptic feedback
            if (telegramWebApp && telegramWebApp.HapticFeedback) {
                telegramWebApp.HapticFeedback.impactOccurred('light');
            }
            
            const permission = await Notification.requestPermission();
            setNotificationPermission(permission);
            
            if (permission === 'granted') {
                // Регистрация для push уведомлений
                if ('serviceWorker' in navigator) {
                    try {
                        const registration = await navigator.serviceWorker.ready;
                        const subscription = await registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: urlBase64ToUint8Array(
                                'BG1cL9jlPwV5-qCJ-1FnqCrYaQgvAqRhzR6pqY_BfCjOiYF_K2KBfVdZSPjPU-BpCHi_dGOlUGCQvGqKdZFaJRc'
                            )
                        });
                        
                        console.log('Push subscription:', subscription);
                        await sendSubscriptionToServer(subscription);
                        
                        // Haptic feedback для успеха
                        if (telegramWebApp && telegramWebApp.HapticFeedback) {
                            telegramWebApp.HapticFeedback.notificationOccurred('success');
                        }
                    } catch (error) {
                        console.error('Ошибка при подписке на push уведомления:', error);
                        if (telegramWebApp && telegramWebApp.HapticFeedback) {
                            telegramWebApp.HapticFeedback.notificationOccurred('error');
                        }
                    }
                }
            }
        }
    };

    const urlBase64ToUint8Array = (base64String) => {
        const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        
        return outputArray;
    };

    const sendSubscriptionToServer = async (subscription) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/push-subscription`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': user?.token ? `Bearer ${user.token}` : ''
                },
                body: JSON.stringify({
                    subscription,
                    telegram_user_id: telegramWebApp?.initDataUnsafe?.user?.id
                }),
            });
            
            if (!response.ok) {
                throw new Error('Ошибка при отправке подписки на сервер');
            }
        } catch (error) {
            console.error('Ошибка при отправке подписки:', error);
        }
    };

    const showInstallInstructions = () => {
        setShowInstallPrompt(true);
        
        // Haptic feedback
        if (telegramWebApp && telegramWebApp.HapticFeedback) {
            telegramWebApp.HapticFeedback.impactOccurred('light');
        }
    };

    const getNetworkStatus = () => {
        if (!isOnline) return { color: 'red', text: 'Оффлайн' };
        
        switch (networkType) {
            case 'slow-2g':
            case '2g':
                return { color: 'orange', text: 'Медленная сеть' };
            case '3g':
                return { color: 'yellow', text: '3G' };
            case '4g':
                return { color: 'green', text: '4G' };
            default:
                return { color: 'green', text: 'Онлайн' };
        }
    };

    const networkStatus = getNetworkStatus();

    return (
        <>
            {/* Статус соединения */}
            {!isOnline && (
                <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-2 text-center text-sm z-50">
                    <div className="flex items-center justify-center space-x-2">
                        <Wifi className="h-4 w-4" />
                        <span>Нет подключения к интернету</span>
                    </div>
                </div>
            )}

            {/* Telegram Web App индикатор */}
            {isTelegram && (
                <div className="fixed top-0 left-0 right-0 bg-gradient-to-r from-blue-500 to-purple-600 text-white p-2 text-center text-sm z-40">
                    <div className="flex items-center justify-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <MessageCircle className="h-4 w-4" />
                            <span>Telegram Web App</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${networkStatus.color === 'green' ? 'bg-green-400' : networkStatus.color === 'yellow' ? 'bg-yellow-400' : networkStatus.color === 'orange' ? 'bg-orange-400' : 'bg-red-400'}`}></div>
                            <span className="text-xs">{networkStatus.text}</span>
                        </div>
                        {isLowPowerMode && (
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                                <span className="text-xs">Энергосбережение</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Кнопка установки PWA (только не в Telegram) */}
            {isInstallable && !isInstalled && !isTelegram && (
                <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-auto z-50">
                    <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-xl shadow-lg telegram-slide-up">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-white/20 rounded-full">
                                    <Download className="h-5 w-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-sm">Установить приложение</h3>
                                    <p className="text-xs text-purple-100">
                                        Быстрый доступ с рабочего стола
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={handleInstallClick}
                                className="bg-white/20 hover:bg-white/30 p-2 rounded-lg transition-colors telegram-ripple"
                            >
                                <Download className="h-5 w-5" />
                            </button>
                        </div>
                        
                        <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                            <div className="flex items-center space-x-1">
                                <Zap className="h-3 w-3" />
                                <span>Быстрый запуск</span>
                            </div>
                            <div className="flex items-center space-x-1">
                                <Shield className="h-3 w-3" />
                                <span>Безопасность</span>
                            </div>
                            <div className="flex items-center space-x-1">
                                <Bell className="h-3 w-3" />
                                <span>Уведомления</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Запрос разрешения на уведомления */}
            {notificationPermission === 'default' && !isTelegram && (
                <div className="fixed top-20 left-4 right-4 md:left-auto md:right-4 md:w-80 z-40">
                    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-4 telegram-fade-in">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-100 rounded-full">
                                    <Bell className="h-5 w-5 text-blue-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-sm text-gray-900">
                                        Включить уведомления
                                    </h3>
                                    <p className="text-xs text-gray-600">
                                        Получайте уведомления о статусе анализа
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex space-x-2">
                            <button
                                onClick={requestNotificationPermission}
                                className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-lg text-sm hover:bg-blue-700 transition-colors telegram-ripple"
                            >
                                Разрешить
                            </button>
                            <button
                                onClick={() => setNotificationPermission('denied')}
                                className="flex-1 bg-gray-200 text-gray-800 py-2 px-3 rounded-lg text-sm hover:bg-gray-300 transition-colors"
                            >
                                Отклонить
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Telegram Web App специальные функции */}
            {isTelegram && telegramWebApp && (
                <div className="fixed top-16 left-4 right-4 z-30">
                    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 p-3 telegram-fade-in">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-100 rounded-full">
                                    <Smartphone className="h-4 w-4 text-blue-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-xs text-gray-900">
                                        Telegram Web App
                                    </h3>
                                    <p className="text-xs text-gray-600">
                                        Все функции доступны
                                    </p>
                                </div>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    onClick={() => {
                                        telegramWebApp.showAlert('Приложение German Letter AI работает в Telegram!');
                                        if (telegramWebApp.HapticFeedback) {
                                            telegramWebApp.HapticFeedback.impactOccurred('medium');
                                        }
                                    }}
                                    className="p-1 bg-blue-100 text-blue-600 rounded-md hover:bg-blue-200 transition-colors"
                                >
                                    <Settings className="h-4 w-4" />
                                </button>
                                <button
                                    onClick={() => {
                                        const url = window.location.href;
                                        const text = 'Попробуйте German Letter AI для анализа документов!';
                                        telegramWebApp.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`);
                                        if (telegramWebApp.HapticFeedback) {
                                            telegramWebApp.HapticFeedback.impactOccurred('medium');
                                        }
                                    }}
                                    className="p-1 bg-green-100 text-green-600 rounded-md hover:bg-green-200 transition-colors"
                                >
                                    <Globe className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Модальное окно с инструкциями по установке */}
            {showInstallPrompt && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl max-w-md w-full telegram-slide-up">
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-bold text-gray-900">
                                    Установить приложение
                                </h2>
                                <button
                                    onClick={() => setShowInstallPrompt(false)}
                                    className="p-2 hover:bg-gray-100 rounded-full telegram-ripple"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>
                            
                            <div className="space-y-4">
                                <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-xl">
                                    <h3 className="font-semibold text-purple-900 mb-2">
                                        Для iOS (Safari):
                                    </h3>
                                    <ol className="text-sm text-purple-800 space-y-1">
                                        <li>1. Нажмите кнопку «Поделиться»</li>
                                        <li>2. Выберите «Добавить на экран "Домой"»</li>
                                        <li>3. Нажмите «Добавить»</li>
                                    </ol>
                                </div>
                                
                                <div className="bg-gradient-to-r from-green-50 to-teal-50 p-4 rounded-xl">
                                    <h3 className="font-semibold text-green-900 mb-2">
                                        Для Android (Chrome):
                                    </h3>
                                    <ol className="text-sm text-green-800 space-y-1">
                                        <li>1. Нажмите меню (три точки)</li>
                                        <li>2. Выберите «Добавить на главный экран»</li>
                                        <li>3. Нажмите «Установить»</li>
                                    </ol>
                                </div>
                                
                                <div className="bg-gray-50 p-4 rounded-xl">
                                    <h3 className="font-semibold text-gray-900 mb-2">
                                        Преимущества:
                                    </h3>
                                    <ul className="text-sm text-gray-700 space-y-1">
                                        <li>• Быстрый доступ с рабочего стола</li>
                                        <li>• Работает без браузера</li>
                                        <li>• Push-уведомления</li>
                                        <li>• Увеличенная производительность</li>
                                        <li>• Автономная работа</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <button
                                onClick={() => setShowInstallPrompt(false)}
                                className="w-full mt-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-xl font-semibold hover:from-purple-700 hover:to-blue-700 transition-all telegram-ripple"
                            >
                                Понятно
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default MobileOptimizations;