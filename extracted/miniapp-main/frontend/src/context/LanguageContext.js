import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const LanguageContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};

// Переводы для интерфейса
const translations = {
    uk: {
        // Общие
        welcome: "Ласкаво просимо до Bürokrator AI!",
        documentAnalysis: "Аналіз документів",
        letterComposer: "Складання листів",
        housingSearch: "Пошук житла",
        jobSearch: "Пошук роботи",
        marketplace: "Маркетплейс",
        loading: "Завантаження...",
        error: "Помилка",
        success: "Успіх",
        close: "Закрити",
        back: "Назад",
        
        // Общие для всей экосистемы
        chooseYourLanguage: "Оберіть мову для всіх інструментів",
        languageChanged: "Мова успішно змінена",
        languageSelection: "Вибір мови",
        languageSelectionDescription: "Ця мова буде використовуватися для аналізу документів і інтерфейсу",
        
        // Анализ документов
        analyzeDocuments: "Аналіз документів",
        aiAnalysis: "AI-аналіз листів і документів",
        uploadDocument: "Завантажте документ",
        aiAnalysisInSeconds: "AI-аналіз за кілька секунд",
        dragFileOrClick: "Перетягніть файл або натисніть для вибору",
        selectFile: "Вибрати файл",
        analysisLanguage: "Мова аналізу",
        chooseLanguage: "Виберіть мову для результатів",
        analyzing: "Аналізуємо документ",
        analysisComplete: "Аналіз готовий",
        
        // Языки
        ukrainian: "Українська",
        russian: "Русский",
        german: "Deutsch",
        
        // Результаты анализа
        summary: "Резюме",
        details: "Деталі",
        response: "Відповідь",
        documentContent: "Зміст документа",
        sender: "Відправник",
        recipient: "Одержувач",
        mainTopic: "Основна тема",
        specificFacts: "Конкретні факти",
        requirements: "Вимоги/прохання",
        dates: "Дати та терміни",
        contactInfo: "Контактна інформація",
        signature: "Підпис та печатка",
        documentLanguage: "Мова документа",
        urgencyLevel: "Рівень терміновості",
        
        // Уровни срочности
        high: "ВИСОКИЙ",
        medium: "СЕРЕДНІЙ",
        low: "НИЗЬКИЙ",
        
        // Ошибки
        noApiKey: "Для аналізу файлів необхідний API ключ",
        analysisError: "Помилка аналізу",
        fileUploadError: "Помилка завантаження файлу",
        authError: "Помилка авторизації",
        connectionError: "Помилка з'єднання з сервером",
        
        // Сообщения
        apiKeyRequired: "Поверніться до головного меню та налаштуйте API ключ",
        analysisSuccess: "Аналіз завершено успішно! 🎉",
        copiedToClipboard: "Скопійовано в буфер обміну!",
        copyError: "Помилка копіювання"
    },
    
    ru: {
        // Общие
        welcome: "Добро пожаловать в Bürokrator AI!",
        documentAnalysis: "Анализ документов",
        letterComposer: "Составление писем",
        housingSearch: "Поиск жилья",
        jobSearch: "Поиск работы",
        marketplace: "Маркетплейс",
        loading: "Загрузка...",
        error: "Ошибка",
        success: "Успех",
        close: "Закрыть",
        back: "Назад",
        
        // Общие для всей экосистемы
        chooseYourLanguage: "Выберите язык для всех инструментов",
        languageChanged: "Язык успешно изменен",
        languageSelection: "Выбор языка",
        languageSelectionDescription: "Этот язык будет использоваться для анализа документов и интерфейса",
        
        // Анализ документов
        analyzeDocuments: "Анализ документов",
        aiAnalysis: "AI анализ писем и документов",
        uploadDocument: "Загрузите документ",
        aiAnalysisInSeconds: "AI анализ за несколько секунд",
        dragFileOrClick: "Перетащите файл или нажмите для выбора",
        selectFile: "Выбрать файл",
        analysisLanguage: "Язык анализа",
        chooseLanguage: "Выберите язык для результатов",
        analyzing: "Анализируем документ",
        analysisComplete: "Анализ готов",
        
        // Языки
        ukrainian: "Українська",
        russian: "Русский",
        german: "Deutsch",
        
        // Результаты анализа
        summary: "Резюме",
        details: "Детали",
        response: "Ответ",
        documentContent: "Содержание документа",
        sender: "Отправитель",
        recipient: "Получатель",
        mainTopic: "Основная тема",
        specificFacts: "Конкретные факты",
        requirements: "Требования/просьбы",
        dates: "Даты и сроки",
        contactInfo: "Контактная информация",
        signature: "Подпись и печать",
        documentLanguage: "Язык документа",
        urgencyLevel: "Уровень срочности",
        
        // Уровни срочности
        high: "ВЫСОКИЙ",
        medium: "СРЕДНИЙ",
        low: "НИЗКИЙ",
        
        // Ошибки
        noApiKey: "Для анализа файлов необходим API ключ",
        analysisError: "Ошибка анализа",
        fileUploadError: "Ошибка загрузки файла",
        authError: "Ошибка авторизации",
        connectionError: "Ошибка соединения с сервером",
        
        // Сообщения
        apiKeyRequired: "Вернитесь в главное меню и настройте API ключ",
        analysisSuccess: "Анализ завершен успешно! 🎉",
        copiedToClipboard: "Скопировано в буфер обмена!",
        copyError: "Ошибка копирования"
    },
    
    de: {
        // Общие
        welcome: "Willkommen bei Bürokrator AI!",
        documentAnalysis: "Dokumentenanalyse",
        letterComposer: "Brieferstellung",
        housingSearch: "Wohnungssuche",
        jobSearch: "Jobsuche",
        marketplace: "Marktplatz",
        loading: "Laden...",
        error: "Fehler",
        success: "Erfolg",
        close: "Schließen",
        back: "Zurück",
        
        // Общие для всей экосистемы
        chooseYourLanguage: "Wählen Sie eine Sprache für alle Werkzeuge",
        languageChanged: "Sprache erfolgreich geändert",
        languageSelection: "Sprachauswahl",
        languageSelectionDescription: "Diese Sprache wird für die Dokumentenanalyse und das Interface verwendet",
        
        // Анализ документов
        analyzeDocuments: "Dokumente analysieren",
        aiAnalysis: "AI-Analyse von Briefen und Dokumenten",
        uploadDocument: "Dokument hochladen",
        aiAnalysisInSeconds: "AI-Analyse in wenigen Sekunden",
        dragFileOrClick: "Datei hierher ziehen oder klicken zum Auswählen",
        selectFile: "Datei auswählen",
        analysisLanguage: "Analysesprache",
        chooseLanguage: "Sprache für Ergebnisse wählen",
        analyzing: "Dokument wird analysiert",
        analysisComplete: "Analyse fertig",
        
        // Языки
        ukrainian: "Українська",
        russian: "Русский",
        german: "Deutsch",
        
        // Результаты анализа
        summary: "Zusammenfassung",
        details: "Details",
        response: "Antwort",
        documentContent: "Dokumentinhalt",
        sender: "Absender",
        recipient: "Empfänger",
        mainTopic: "Hauptthema",
        specificFacts: "Konkrete Fakten",
        requirements: "Anforderungen/Bitten",
        dates: "Daten und Fristen",
        contactInfo: "Kontaktinformationen",
        signature: "Unterschrift und Siegel",
        documentLanguage: "Dokumentsprache",
        urgencyLevel: "Dringlichkeitsstufe",
        
        // Уровни срочности
        high: "HOCH",
        medium: "MITTEL",
        low: "NIEDRIG",
        
        // Ошибки
        noApiKey: "Für die Dateianalyse ist ein API-Schlüssel erforderlich",
        analysisError: "Analysefehler",
        fileUploadError: "Fehler beim Hochladen der Datei",
        authError: "Authentifizierungsfehler",
        connectionError: "Verbindungsfehler zum Server",
        
        // Сообщения
        apiKeyRequired: "Kehren Sie zum Hauptmenü zurück und konfigurieren Sie den API-Schlüssel",
        analysisSuccess: "Analyse erfolgreich abgeschlossen! 🎉",
        copiedToClipboard: "In die Zwischenablage kopiert!",
        copyError: "Kopierfehler"
    }
};

export const LanguageProvider = ({ children }) => {
    const [currentLanguage, setCurrentLanguage] = useState('ru'); // По умолчанию русский
    const [isLanguageSelected, setIsLanguageSelected] = useState(false);

    useEffect(() => {
        // Проверяем, был ли уже выбран язык
        const savedLanguage = localStorage.getItem('selectedLanguage');
        const languageSelected = localStorage.getItem('languageSelected');
        
        if (savedLanguage && languageSelected === 'true') {
            setCurrentLanguage(savedLanguage);
            setIsLanguageSelected(true);
        }
    }, []);

    // Функция для загрузки языка из профиля пользователя
    const loadUserLanguage = async () => {
        try {
            const token = localStorage.getItem('authToken');
            if (token) {
                const response = await axios.get(`${BACKEND_URL}/api/profile`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                
                const userLanguage = response.data.preferred_language;
                if (userLanguage) {
                    setCurrentLanguage(userLanguage);
                    localStorage.setItem('selectedLanguage', userLanguage);
                    localStorage.setItem('languageSelected', 'true');
                    setIsLanguageSelected(true);
                    console.log('Language loaded from backend:', userLanguage);
                }
            }
        } catch (error) {
            console.error('Error loading language from backend:', error);
        }
    };

    const changeLanguage = async (languageCode) => {
        setCurrentLanguage(languageCode);
        localStorage.setItem('selectedLanguage', languageCode);
        localStorage.setItem('languageSelected', 'true');
        setIsLanguageSelected(true);
        
        // Сохраняем язык в профиле пользователя на backend (если пользователь авторизован)
        try {
            const token = localStorage.getItem('authToken');
            if (token) {
                await axios.post(`${BACKEND_URL}/api/change-language`, {
                    language: languageCode
                }, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                console.log('Language saved to backend:', languageCode);
            }
        } catch (error) {
            console.error('Error saving language to backend:', error);
            // Не останавливаем работу, если backend недоступен
        }
    };

    const t = (key) => {
        return translations[currentLanguage]?.[key] || key;
    };

    const value = {
        currentLanguage,
        changeLanguage,
        loadUserLanguage,
        t,
        isLanguageSelected,
        setIsLanguageSelected
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
};

export default LanguageProvider;