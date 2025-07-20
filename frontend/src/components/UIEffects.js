import React, { useEffect, useState } from 'react';

const FloatingParticles = () => {
    const [particles, setParticles] = useState([]);

    useEffect(() => {
        const newParticles = [];
        for (let i = 0; i < 20; i++) {
            newParticles.push({
                id: i,
                x: Math.random() * 100,
                y: Math.random() * 100,
                size: Math.random() * 4 + 2,
                animationDelay: Math.random() * 5,
                animationDuration: Math.random() * 10 + 15
            });
        }
        setParticles(newParticles);
    }, []);

    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
            {particles.map((particle) => (
                <div
                    key={particle.id}
                    className="absolute rounded-full bg-gradient-to-r from-blue-400/10 to-purple-400/10 animate-float"
                    style={{
                        left: `${particle.x}%`,
                        top: `${particle.y}%`,
                        width: `${particle.size}px`,
                        height: `${particle.size}px`,
                        animationDelay: `${particle.animationDelay}s`,
                        animationDuration: `${particle.animationDuration}s`
                    }}
                />
            ))}
        </div>
    );
};

const GlassCard = ({ children, className = "", ...props }) => {
    return (
        <div 
            className={`backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-[1.02] ${className}`}
            {...props}
        >
            {children}
        </div>
    );
};

const GradientText = ({ children, className = "" }) => {
    return (
        <span className={`bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent font-bold ${className}`}>
            {children}
        </span>
    );
};

const NeomorphismCard = ({ children, className = "", pressed = false, ...props }) => {
    const shadowClass = pressed 
        ? "shadow-inner-neu" 
        : "shadow-neu hover:shadow-neu-lg";
    
    return (
        <div 
            className={`bg-gray-100 rounded-2xl transition-all duration-300 hover:scale-[1.02] ${shadowClass} ${className}`}
            {...props}
        >
            {children}
        </div>
    );
};

const AnimatedCounter = ({ value, duration = 2000 }) => {
    const [count, setCount] = useState(0);

    useEffect(() => {
        let startTime;
        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            
            setCount(Math.floor(progress * value));
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }, [value, duration]);

    return <span>{count}</span>;
};

const PulsingDot = ({ className = "", size = "w-3 h-3" }) => {
    return (
        <div className={`${size} ${className} relative`}>
            <div className="w-full h-full bg-current rounded-full animate-ping absolute opacity-75"></div>
            <div className="w-full h-full bg-current rounded-full relative"></div>
        </div>
    );
};

const FloatingElement = ({ children, delay = 0, amplitude = 20 }) => {
    return (
        <div 
            className="animate-float-smooth"
            style={{
                animationDelay: `${delay}s`,
                '--float-amplitude': `${amplitude}px`
            }}
        >
            {children}
        </div>
    );
};

const ShimmerEffect = ({ className = "" }) => {
    return (
        <div className={`relative overflow-hidden ${className}`}>
            <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
        </div>
    );
};

const GradientBorder = ({ children, className = "", borderWidth = 2 }) => {
    return (
        <div className={`relative ${className}`} style={{ padding: borderWidth }}>
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 animate-gradient-x"></div>
            <div className="relative bg-white rounded-2xl h-full w-full">
                {children}
            </div>
        </div>
    );
};

const MagneticElement = ({ children, strength = 0.3 }) => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isHovered, setIsHovered] = useState(false);

    const handleMouseMove = (e) => {
        if (!isHovered) return;
        
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        setPosition({ 
            x: x * strength, 
            y: y * strength 
        });
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        setPosition({ x: 0, y: 0 });
    };

    return (
        <div
            className="transition-transform duration-300 ease-out"
            style={{
                transform: `translate(${position.x}px, ${position.y}px)`
            }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            {children}
        </div>
    );
};

export {
    FloatingParticles,
    GlassCard,
    GradientText,
    NeomorphismCard,
    AnimatedCounter,
    PulsingDot,
    FloatingElement,
    ShimmerEffect,
    GradientBorder,
    MagneticElement
};