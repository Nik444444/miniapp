import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(localStorage.getItem('authToken'));

    // Configure axios defaults
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    // Check if user is authenticated
    const isAuthenticated = () => {
        return !!token && !!user;
    };

    // Login with Google
    const loginWithGoogle = async (credential) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/auth/google/verify`, {
                credential: credential
            });

            const { access_token, user: userData } = response.data;

            // Store token and user data
            localStorage.setItem('authToken', access_token);
            setToken(access_token);
            setUser({...userData, token: access_token});

            return { success: true };
        } catch (error) {
            console.error('Google login failed:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось войти'
            };
        }
    };

    // Login with Telegram
    const loginWithTelegram = async (telegramUser, initData = null) => {
        console.log('AuthContext: Starting Telegram login for user:', telegramUser);
        console.log('AuthContext: initData:', initData);
        console.log('AuthContext: Backend URL:', BACKEND_URL);
        
        try {
            // Prepare authentication data
            const authData = {
                telegram_user: telegramUser
            };
            
            // Add initData if available
            if (initData) {
                authData.initData = initData;
            }
            
            // Also include user data in case backend needs it
            if (telegramUser) {
                authData.user = telegramUser;
            }
            
            console.log('AuthContext: Sending auth data:', authData);
            
            const response = await axios.post(`${BACKEND_URL}/api/auth/telegram/verify`, authData, {
                timeout: 10000  // 10 секунд таймаут
            });

            console.log('AuthContext: Telegram login response:', response.data);
            
            const { access_token, user: userData } = response.data;

            // Store token and user data
            localStorage.setItem('authToken', access_token);
            setToken(access_token);
            setUser({...userData, token: access_token});

            console.log('AuthContext: Telegram login successful, user data:', userData);
            return { success: true };
        } catch (error) {
            console.error('AuthContext: Telegram login failed:', error);
            console.error('AuthContext: Error response:', error.response?.data);
            
            // Более подробная обработка ошибок
            let errorMessage = 'Не удалось войти через Telegram';
            
            if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
                errorMessage = 'Превышено время ожидания. Проверьте подключение к интернету.';
            } else if (error.code === 'NETWORK_ERROR' || !error.response) {
                errorMessage = 'Сервер недоступен. Попробуйте позже.';
            } else if (error.response?.status === 400) {
                errorMessage = error.response.data?.detail || 'Неверные данные авторизации';
            } else if (error.response?.status === 500) {
                errorMessage = 'Ошибка сервера. Попробуйте позже.';
            }
            
            return {
                success: false,
                error: errorMessage
            };
        }
    };

    // Logout
    const logout = () => {
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    // Get user profile
    const fetchUserProfile = async () => {
        try {
            if (!token) return;

            const response = await axios.get(`${BACKEND_URL}/api/profile`);
            setUser({...response.data, token: token});
        } catch (error) {
            console.error('Failed to fetch user profile:', error);
            if (error.response?.status === 401) {
                logout();
            }
        }
    };

    // Update user profile
    const updateProfile = async (data) => {
        try {
            const response = await axios.put(`${BACKEND_URL}/api/profile`, data);
            setUser(response.data);
            return { success: true };
        } catch (error) {
            console.error('Failed to update profile:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось обновить профиль'
            };
        }
    };

    // Save API keys
    const saveApiKeys = async (apiKeys) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/api-keys`, apiKeys);

            // Update user object
            setUser(prev => ({ 
                ...prev, 
                has_api_key_1: !!(apiKeys.api_key_1 || prev.has_api_key_1),
                has_api_key_2: !!(apiKeys.api_key_2 || prev.has_api_key_2),
                has_api_key_3: !!(apiKeys.api_key_3 || prev.has_api_key_3)
            }));

            return { success: true, message: response.data.message };
        } catch (error) {
            console.error('Failed to save API keys:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось сохранить API ключи'
            };
        }
    };

    // Save Gemini API key (quick setup)
    const saveGeminiApiKey = async (apiKey) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/quick-gemini-setup`, {
                api_key: apiKey
            });

            // Немедленно обновляем состояние пользователя
            setUser(prev => ({ 
                ...prev, 
                has_gemini_api_key: true,
                has_api_key_1: true // Также обновляем для совместимости
            }));

            // НЕ вызываем fetchUserProfile(), чтобы не перезаписать оптимистичное обновление
            // Профиль обновится при следующей естественной перезагрузке

            return { success: true, message: response.data.message };
        } catch (error) {
            console.error('Failed to save Gemini API key:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось сохранить API ключ'
            };
        }
    };

    // Initialize authentication state
    useEffect(() => {
        const initAuth = async () => {
            if (token) {
                await fetchUserProfile();
            }
            setLoading(false);
        };

        initAuth();
    }, [token]);

    // Update user language
    const updateUserLanguage = async (language) => {
        try {
            const response = await axios.post(`${BACKEND_URL}/api/change-language`, {
                language: language
            });

            // Обновляем состояние пользователя
            setUser(prev => ({ 
                ...prev, 
                preferred_language: language
            }));

            return { success: true, message: response.data.message };
        } catch (error) {
            console.error('Failed to update language:', error);
            return {
                success: false,
                error: error.response?.data?.detail || 'Не удалось обновить язык'
            };
        }
    };

    const value = {
        user,
        token,
        loading,
        backendUrl: BACKEND_URL,
        isAuthenticated,
        loginWithGoogle,
        loginWithTelegram,
        logout,
        fetchUserProfile,
        updateProfile,
        saveApiKeys,
        saveGeminiApiKey,
        updateUserLanguage
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};