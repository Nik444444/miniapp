import React, { useContext, useState, useCallback, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import TelegramMainMenu from './TelegramMainMenu';
import TelegramDocumentAnalysis from './TelegramDocumentAnalysis';
import TelegramLetterComposer from './TelegramLetterComposer';
import TelegramApiKeySetup from './TelegramApiKeySetup';
import TelegramComingSoon from './TelegramComingSoon';
import TelegramJobSearch from './TelegramJobSearch';
import TelegramLanguageSelector from './TelegramLanguageSelector';
import SpectacularDocumentAnalysis from './SpectacularDocumentAnalysis';
import SpectacularAnalysisResult from './SpectacularAnalysisResult';
import { 
    Edit, 
    Home, 
    Briefcase, 
    ShoppingCart,
    FileText,
    Key
} from 'lucide-react';
import { 
    isTelegramWebApp, 
    getTelegramWebApp, 
    hapticFeedback 
} from '../utils/telegramWebApp';

const TelegramMainApp = () => {
    const { user } = useContext(AuthContext);
    const [currentView, setCurrentView] = useState('menu');
    const [currentTool, setCurrentTool] = useState(null);

    // Telegram WebApp specific setup
    useEffect(() => {
        if (isTelegramWebApp()) {
            const tg = getTelegramWebApp();
            if (tg) {
                tg.ready();
                tg.expand();
                tg.setHeaderColor('#0f0f23');
                tg.setBackgroundColor('#0f0f23');
            }
        }
    }, []);

    const handleNavigation = (toolId) => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        
        setCurrentTool(toolId);
        
        if (toolId === 'document-analysis') {
            setCurrentView('document-analysis');
        } else if (toolId === 'letter-composer') {
            setCurrentView('letter-composer');
        } else if (toolId === 'housing-search') {
            setCurrentView('housing-search');
        } else if (['job-search', 'marketplace'].includes(toolId)) {
            setCurrentView('coming-soon');
        }
    };

    const handleApiKeySetup = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        setCurrentView('api-key-setup');
    };

    const handleLanguageSelection = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        setCurrentView('language-selector');
    };

    const handleBackToMenu = () => {
        if (isTelegramWebApp()) {
            hapticFeedback('light');
        }
        setCurrentView('menu');
        setCurrentTool(null);
    };

    const getToolInfo = (toolId) => {
        const toolsInfo = {
            'letter-composer': {
                id: 'letter-composer',
                title: 'Составление писем',
                subtitle: 'Генерация официальных писем',
                icon: Edit,
                gradient: 'from-orange-500 via-red-500 to-pink-500',
                bgGradient: 'from-orange-500/20 to-pink-500/20'
            },
            'housing-search': {
                id: 'housing-search',
                title: 'Поиск жилья',
                subtitle: 'Поиск квартир и домов',
                icon: Home,
                gradient: 'from-cyan-500 via-blue-500 to-purple-500',
                bgGradient: 'from-cyan-500/20 to-purple-500/20'
            },
            'job-search': {
                id: 'job-search',
                title: 'Поиск работы',
                subtitle: 'Поиск вакансий',
                icon: Briefcase,
                gradient: 'from-violet-500 via-purple-500 to-fuchsia-500',
                bgGradient: 'from-violet-500/20 to-fuchsia-500/20'
            },
            'marketplace': {
                id: 'marketplace',
                title: 'Маркетплейс',
                subtitle: 'Покупка и продажа',
                icon: ShoppingCart,
                gradient: 'from-yellow-500 via-orange-500 to-red-500',
                bgGradient: 'from-yellow-500/20 to-red-500/20'
            }
        };
        return toolsInfo[toolId] || {};
    };

    // Routing based on current view
    if (currentView === 'document-analysis') {
        return <TelegramDocumentAnalysis onBack={handleBackToMenu} />;
    }
    
    if (currentView === 'letter-composer') {
        return <TelegramLetterComposer onBack={handleBackToMenu} />;
    }
    
    if (currentView === 'housing-search') {
        return <TelegramHousingSearch onBack={handleBackToMenu} />;
    }
    
    if (currentView === 'api-key-setup') {
        return <TelegramApiKeySetup onBack={handleBackToMenu} />;
    }
    
    if (currentView === 'language-selector') {
        return <TelegramLanguageSelector onBack={handleBackToMenu} />;
    }
    
    if (currentView === 'coming-soon') {
        return <TelegramComingSoon onBack={handleBackToMenu} toolInfo={getToolInfo(currentTool)} />;
    }
    
    // Default to main menu
    return (
        <TelegramMainMenu 
            onNavigate={handleNavigation} 
            onApiKeySetup={handleApiKeySetup}
            onLanguageSelection={handleLanguageSelection}
        />
    );
};

export default TelegramMainApp;