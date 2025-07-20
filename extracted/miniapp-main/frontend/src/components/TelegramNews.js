import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    MessageCircle, 
    ExternalLink, 
    Eye, 
    Clock, 
    TrendingUp,
    Heart,
    Share2,
    Bell,
    Users,
    Zap,
    Star,
    ChevronRight,
    Play,
    Image as ImageIcon,
    Video,
    FileText,
    Sparkles
} from 'lucide-react';
import { GlassCard, GradientText, FloatingElement, PulsingDot, MagneticElement } from './UIEffects';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const TelegramNews = ({ compact = false }) => {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [channelInfo, setChannelInfo] = useState(null);
    const [expandedNews, setExpandedNews] = useState(null);
    const [subscribing, setSubscribing] = useState(false);

    useEffect(() => {
        loadNews();
    }, []);

    const loadNews = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/telegram-news?limit=5`);
            setNews(response.data.news || []);
            setChannelInfo({
                name: response.data.channel_name,
                link: response.data.channel_link,
                count: response.data.count,
                status: response.data.status
            });
        } catch (error) {
            console.error('Error loading Telegram news:', error);
            // Fallback demo news
            setNews([
                {
                    id: 1,
                    text: '🇩🇪 Новые правила получения вида на жительство в Германии. Изменения коснутся всех категорий мигрантов.',
                    preview_text: '🇩🇪 Новые правила получения вида на жительство в Германии...',
                    formatted_date: '1 ч назад',
                    views: 1250,
                    has_media: false,
                    media_type: 'text',
                    link: 'https://t.me/germany_ua_news/1'
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubscribe = async () => {
        setSubscribing(true);
        setTimeout(() => {
            window.open(channelInfo?.link, '_blank');
            setSubscribing(false);
        }, 1000);
    };

    const getMediaIcon = (mediaType) => {
        switch (mediaType) {
            case 'photo': return <ImageIcon className="h-4 w-4" />;
            case 'video': return <Video className="h-4 w-4" />;
            case 'document': return <FileText className="h-4 w-4" />;
            default: return <MessageCircle className="h-4 w-4" />;
        }
    };

    const formatViews = (views) => {
        if (views > 1000000) return `${(views / 1000000).toFixed(1)}M`;
        if (views > 1000) return `${(views / 1000).toFixed(1)}K`;
        return views.toString();
    };

    if (loading) {
        return (
            <GlassCard className="p-6 h-full">
                <div className="animate-pulse space-y-4">
                    <div className="flex items-center space-x-3 mb-6">
                        <div className="w-12 h-12 bg-blue-200 rounded-full"></div>
                        <div className="flex-1">
                            <div className="h-4 bg-blue-200 rounded w-3/4 mb-2"></div>
                            <div className="h-3 bg-blue-200 rounded w-1/2"></div>
                        </div>
                    </div>
                    
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="border-b border-white/10 pb-4">
                            <div className="h-4 bg-blue-200 rounded w-full mb-2"></div>
                            <div className="h-4 bg-blue-200 rounded w-2/3 mb-2"></div>
                            <div className="flex space-x-4">
                                <div className="h-3 bg-blue-200 rounded w-16"></div>
                                <div className="h-3 bg-blue-200 rounded w-12"></div>
                            </div>
                        </div>
                    ))}
                </div>
            </GlassCard>
        );
    }

    return (
        <div className="space-y-4">
            {/* Compact mode for mobile */}
            {compact ? (
                <div className="space-y-2">
                    {news.slice(0, 3).map((item, index) => (
                        <div key={index} className="bg-white/50 p-3 rounded-lg border border-white/30">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-500">{item.formatted_date}</span>
                                <div className="flex items-center space-x-1 text-gray-400">
                                    <Eye className="h-3 w-3" />
                                    <span className="text-xs">{item.views}</span>
                                </div>
                            </div>
                            <p className="text-sm text-gray-700 line-clamp-2">{item.preview_text}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <>
                    {/* Full mode for desktop */}
                    <GlassCard className="p-6 bg-white/30 backdrop-blur-xl border border-white/30">
                        <div className="mb-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                                        <MessageCircle className="h-5 w-5 text-white" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold">
                                            <GradientText>Последние новости</GradientText>
                                        </h2>
                                        <p className="text-xs text-gray-600">
                                            {channelInfo?.name || 'Germany UA News'}
                                        </p>
                                    </div>
                                </div>

                        <div className="flex-shrink-0">
                            <button
                                onClick={handleSubscribe}
                                disabled={subscribing}
                                className="relative px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 disabled:opacity-70"
                            >
                                {subscribing ? (
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        <span>Открываю...</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center space-x-2">
                                        <Bell className="h-4 w-4" />
                                        <span>Подписаться</span>
                                        <ExternalLink className="h-4 w-4" />
                                    </div>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-white/10 rounded-xl backdrop-blur-sm">
                            <div className="flex items-center justify-center space-x-1 text-blue-600 mb-1">
                                <TrendingUp className="h-4 w-4" />
                                <span className="font-bold text-lg">{channelInfo?.count || news.length}</span>
                            </div>
                            <span className="text-xs text-gray-600">Новостей</span>
                        </div>
                        
                        <div className="text-center p-3 bg-white/10 rounded-xl backdrop-blur-sm">
                            <div className="flex items-center justify-center space-x-1 text-purple-600 mb-1">
                                <Users className="h-4 w-4" />
                                <span className="font-bold text-lg">15K+</span>
                            </div>
                            <span className="text-xs text-gray-600">Читателей</span>
                        </div>
                        
                        <div className="text-center p-3 bg-white/10 rounded-xl backdrop-blur-sm">
                            <div className="flex items-center justify-center space-x-1 text-pink-600 mb-1">
                                <Zap className="h-4 w-4" />
                                <span className="font-bold text-lg">Live</span>
                            </div>
                            <span className="text-xs text-gray-600">Онлайн</span>
                        </div>
                    </div>
                </div>
            </GlassCard>

            {/* News List */}
            <GlassCard className="p-6">
                <div className="flex items-center space-x-2 mb-6">
                    <Sparkles className="h-5 w-5 text-yellow-500" />
                    <h4 className="font-bold text-gray-900">Последние новости</h4>
                </div>
                
                <div className="space-y-4">
                    {news.map((item, index) => (
                        <div key={item.id} className="group relative p-4 rounded-xl bg-white/50 hover:bg-white/80 transition-all duration-300 hover:shadow-lg border border-white/20">
                            {/* News Content */}
                            <div className="flex items-start space-x-3">
                                {/* Media Icon */}
                                <div className="flex-shrink-0 mt-1">
                                    <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-lg flex items-center justify-center text-white">
                                        {getMediaIcon(item.media_type)}
                                    </div>
                                </div>
                                
                                {/* Text Content */}
                                <div className="flex-1 min-w-0">
                                    <p className="text-gray-800 text-sm leading-relaxed mb-3">
                                        {expandedNews === item.id ? item.text : item.preview_text}
                                    </p>
                                    
                                    {/* Actions */}
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                                            <div className="flex items-center space-x-1">
                                                <Clock className="h-3 w-3" />
                                                <span>{item.formatted_date}</span>
                                            </div>
                                            
                                            {item.views > 0 && (
                                                <div className="flex items-center space-x-1">
                                                    <Eye className="h-3 w-3" />
                                                    <span>{formatViews(item.views)}</span>
                                                </div>
                                            )}
                                            
                                            {item.has_media && (
                                                <div className="flex items-center space-x-1 text-blue-500">
                                                    <Play className="h-3 w-3" />
                                                    <span>Медиа</span>
                                                </div>
                                            )}
                                        </div>
                                        
                                        <div className="flex items-center space-x-2">
                                            {item.text !== item.preview_text && (
                                                <button
                                                    onClick={() => setExpandedNews(expandedNews === item.id ? null : item.id)}
                                                    className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                                                >
                                                    {expandedNews === item.id ? 'Свернуть' : 'Читать'}
                                                </button>
                                            )}
                                            
                                            <button
                                                onClick={() => window.open(item.link, '_blank')}
                                                className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                                            >
                                                <ExternalLink className="h-3 w-3" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            {/* Hover Effect */}
                            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                        </div>
                    ))}
                </div>
                
                {/* View All Button */}
                <div className="mt-6 text-center">
                    <button
                        onClick={() => window.open(channelInfo?.link, '_blank')}
                        className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 hover:scale-105"
                    >
                        <span>Смотреть все новости</span>
                        <ChevronRight className="h-4 w-4" />
                    </button>
                </div>
            </GlassCard>
                </>
            )}
        </div>
    );
};

export default TelegramNews;