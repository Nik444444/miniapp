// Utility functions for Telegram Web App detection and handling

export const isTelegramWebApp = () => {
    // Упрощенная и более надёжная проверка Telegram Web App API
    if (typeof window === 'undefined') return false;
    
    // Проверяем наличие Telegram Web App API (самый надежный способ)
    if (window.Telegram && window.Telegram.WebApp) {
        const webApp = window.Telegram.WebApp;
        
        // Более мягкая проверка - достаточно наличия API
        if (webApp.version || webApp.platform || webApp.initData !== undefined) {
            console.log('Telegram detected: WebApp API found');
            return true;
        }
    }
    
    // Проверяем URL параметры для Telegram
    const urlParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    
    // Проверяем наличие Telegram-специфических параметров
    if (urlParams.has('tgWebAppData') || hashParams.has('tgWebAppData') || 
        urlParams.has('tgWebAppVersion') || hashParams.has('tgWebAppVersion')) {
        console.log('Telegram detected: URL parameters found');
        return true;
    }
    
    // Проверяем User-Agent на наличие Telegram
    if (navigator.userAgent && navigator.userAgent.includes('Telegram')) {
        console.log('Telegram detected: User-Agent contains Telegram');
        return true;
    }
    
    // Проверяем наличие tgWebAppVersion в localStorage (может быть установлен Telegram)
    if (localStorage.getItem('tgWebAppVersion')) {
        console.log('Telegram detected: localStorage has tgWebAppVersion');
        return true;
    }
    
    // Если есть параметры в URL, похожие на Telegram
    const search = window.location.search;
    if (search.includes('tgWebApp') || search.includes('telegram') || search.includes('tg_id')) {
        console.log('Telegram detected: URL contains Telegram-related parameters');
        return true;
    }
    
    // Проверяем специфичные для Telegram заголовки или свойства
    if (window.TelegramWebviewProxy || window.TelegramGameProxy) {
        console.log('Telegram detected: Telegram proxy found');
        return true;
    }
    
    // Если мы на /telegram роуте, считаем это Telegram средой (для тестирования)
    if (window.location.pathname === '/telegram') {
        console.log('Telegram detected: /telegram route');
        return true;
    }
    
    console.log('Telegram NOT detected');
    return false;
};

export const getTelegramWebApp = () => {
    if (isTelegramWebApp()) {
        return window.Telegram.WebApp;
    }
    return null;
};

export const getTelegramUser = () => {
    const webApp = getTelegramWebApp();
    
    // Способ 1: Из initDataUnsafe (самый надежный)
    if (webApp && webApp.initDataUnsafe && webApp.initDataUnsafe.user) {
        return webApp.initDataUnsafe.user;
    }
    
    // Способ 2: Парсинг initData
    if (webApp && webApp.initData) {
        try {
            const urlParams = new URLSearchParams(webApp.initData);
            const userParam = urlParams.get('user');
            if (userParam) {
                return JSON.parse(decodeURIComponent(userParam));
            }
        } catch (e) {
            console.warn('Failed to parse Telegram user data from initData:', e);
        }
    }
    
    // Способ 3: Из URL параметров
    const urlParams = new URLSearchParams(window.location.search);
    const userParam = urlParams.get('user');
    if (userParam) {
        try {
            return JSON.parse(decodeURIComponent(userParam));
        } catch (e) {
            console.warn('Failed to parse user from URL params:', e);
        }
    }
    
    // Способ 4: Из localStorage (если была сохранена ранее)
    const savedUser = localStorage.getItem('telegram_user');
    if (savedUser) {
        try {
            return JSON.parse(savedUser);
        } catch (e) {
            console.warn('Failed to parse saved Telegram user:', e);
        }
    }
    
    // Способ 5: Для тестирования создаем mock пользователя
    if (window.location.pathname === '/telegram' || isTelegramWebApp()) {
        const mockUser = {
            id: Math.floor(Math.random() * 1000000),
            first_name: 'Telegram',
            last_name: 'User',
            username: 'telegramuser',
            language_code: 'ru',
            is_bot: false
        };
        
        // Сохраняем mock пользователя в localStorage
        localStorage.setItem('telegram_user', JSON.stringify(mockUser));
        return mockUser;
    }
    
    return null;
};

export const setupTelegramWebApp = () => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        // Расширяем приложение на весь экран
        webApp.expand();
        
        // Настраиваем тему
        webApp.setHeaderColor('bg_color');
        webApp.setBackgroundColor('#1a1a2e');
        
        // Скрываем кнопку Back, если она есть
        webApp.BackButton.hide();
        
        // Готовим приложение
        webApp.ready();
        
        return webApp;
    }
    return null;
};

export const showTelegramAlert = (message) => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.showAlert(message);
    } else {
        alert(message);
    }
};

export const showTelegramConfirm = (message, callback) => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.showConfirm(message, callback);
    } else {
        const result = confirm(message);
        callback(result);
    }
};

export const closeTelegramWebApp = () => {
    const webApp = getTelegramWebApp();
    if (webApp) {
        webApp.close();
    }
};

export const hapticFeedback = (type = 'light') => {
    const webApp = getTelegramWebApp();
    if (webApp && webApp.HapticFeedback) {
        switch (type) {
            case 'light':
                webApp.HapticFeedback.impactOccurred('light');
                break;
            case 'medium':
                webApp.HapticFeedback.impactOccurred('medium');
                break;
            case 'heavy':
                webApp.HapticFeedback.impactOccurred('heavy');
                break;
            case 'soft':
                webApp.HapticFeedback.impactOccurred('soft');
                break;
            case 'rigid':
                webApp.HapticFeedback.impactOccurred('rigid');
                break;
            case 'success':
                webApp.HapticFeedback.notificationOccurred('success');
                break;
            case 'warning':
                webApp.HapticFeedback.notificationOccurred('warning');
                break;
            case 'error':
                webApp.HapticFeedback.notificationOccurred('error');
                break;
            default:
                webApp.HapticFeedback.impactOccurred('light');
        }
    }
};

export const showBackButton = (callback) => {
    const webApp = getTelegramWebApp();
    if (webApp && webApp.BackButton) {
        webApp.BackButton.show();
        if (callback) {
            webApp.BackButton.onClick(callback);
        }
    }
};

export const hideBackButton = () => {
    const webApp = getTelegramWebApp();
    if (webApp && webApp.BackButton) {
        webApp.BackButton.hide();
    }
};

export const telegramWebApp = getTelegramWebApp();