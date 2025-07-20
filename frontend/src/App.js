import React, { useContext } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Auth from './components/Auth';
import TelegramAuth from './components/TelegramAuth';
import SuperMainApp from './components/SuperMainApp';
import TelegramMainApp from './components/TelegramMainApp';
import AdminPanel from './components/AdminPanel';
import LanguageSelector from './components/LanguageSelector';
import EnvCheck from './components/EnvCheck';
import { isTelegramWebApp, setupTelegramWebApp } from './utils/telegramWebApp';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com';

function App() {
    // Настраиваем Telegram Web App при запуске
    React.useEffect(() => {
        if (isTelegramWebApp()) {
            setupTelegramWebApp();
        }
    }, []);

    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <LanguageProvider>
                <AuthProvider>
                    <AppContent />
                </AuthProvider>
            </LanguageProvider>
        </GoogleOAuthProvider>
    );
}

const AppContent = () => {
    const { isAuthenticated, loading } = useContext(AuthContext);
    const { isLanguageSelected, changeLanguage } = useLanguage();
    
    // Добавляем отладочную информацию
    const isTelegram = isTelegramWebApp();
    
    // Дополнительная проверка для обычных браузеров
    const isRegularBrowser = !isTelegram && typeof window !== 'undefined';
    
    console.log('Environment check:', {
        isTelegram,
        isRegularBrowser,
        hasWindow: typeof window !== 'undefined',
        hasTelegramAPI: !!(window.Telegram && window.Telegram.WebApp),
        userAgent: navigator.userAgent,
        isLanguageSelected,
        currentPath: window.location.pathname
    });

    // Если это Telegram среда, пропускаем выбор языка
    if (isTelegram && !isLanguageSelected) {
        console.log('Telegram environment detected, skipping language selection');
        changeLanguage('ru'); // Устанавливаем русский язык по умолчанию для Telegram
        return null; // Возвращаем null, чтобы дождаться установки языка
    }

    // Если язык не выбран и это не Telegram, показываем экран выбора языка
    if (!isLanguageSelected && !isTelegram) {
        return <LanguageSelector onLanguageSelect={changeLanguage} />;
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center relative overflow-hidden">
                {/* Background Pattern */}
                <div className="absolute inset-0 bg-dots-pattern opacity-30"></div>
                
                <div className="text-center relative z-10">
                    <div className="relative mb-8">
                        <div className="w-16 h-16 border-4 border-indigo-200 rounded-full animate-spin border-t-indigo-600 mx-auto"></div>
                        <div className="absolute inset-0 w-16 h-16 border-4 border-purple-200 rounded-full animate-ping mx-auto"></div>
                    </div>
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                        Загрузка...
                    </h3>
                    <p className="text-gray-600">Подготавливаем волшебство</p>
                </div>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <Routes>
                {/* Main route - автоматическое определение среды */}
                <Route path="/" element={
                    isAuthenticated() ? (
                        isTelegram ? <TelegramMainApp /> : <SuperMainApp />
                    ) : (
                        isTelegram ? <TelegramAuth /> : <Auth />
                    )
                } />
                
                {/* Веб версия - всегда показывает браузерную версию */}
                <Route path="/web" element={
                    isAuthenticated() ? <SuperMainApp /> : <Auth />
                } />
                
                {/* Telegram-specific route - принудительно показывает Telegram версию */}
                <Route path="/telegram" element={
                    isAuthenticated() ? <TelegramMainApp /> : <TelegramAuth />
                } />
                
                {/* Admin panel */}
                <Route path="/admin" element={<AdminPanel />} />
                
                {/* Environment check for debugging */}
                <Route path="/env-check" element={<EnvCheck />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
