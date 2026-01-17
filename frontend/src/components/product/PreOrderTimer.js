
import React, { useState, useEffect } from 'react';

const PreOrderTimer = ({ availableDate, endDate }) => {
    const [timeLeft, setTimeLeft] = useState('');
    const [status, setStatus] = useState('loading'); // upcoming, active, ended

    useEffect(() => {
        const calculateTime = () => {
            const now = new Date();
            const start = new Date(availableDate);
            const end = endDate ? new Date(endDate) : null;

            if (now < start) {
                // Countdown to start
                const diff = start - now;
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
                const minutes = Math.floor((diff / (1000 * 60)) % 60);
                const seconds = Math.floor((diff / 1000) % 60);
                setTimeLeft(`${days}d ${hours}h ${minutes}m ${seconds}s`);
                setStatus('upcoming');
            } else if (end && now < end) {
                // Countdown to end
                const diff = end - now;
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
                setTimeLeft(`${days}d ${hours}h left`);
                setStatus('active');
            } else if (end && now >= end) {
                setTimeLeft('Pre-order Ended');
                setStatus('ended');
            } else {
                // Started but no end date defined, or just available
                setTimeLeft('Available Now');
                setStatus('active');
            }
        };

        calculateTime();
        const timer = setInterval(calculateTime, 1000);

        return () => clearInterval(timer);
    }, [availableDate, endDate]);

    if (status === 'ended' || !availableDate) return null;

    return (
        <div className={`rounded-lg p-2 text-center border mb-3 ${status === 'upcoming' ? 'bg-orange-50 border-orange-200 text-orange-700' :
                'bg-emerald-50 border-emerald-200 text-emerald-700'
            }`}>
            <div className="text-[10px] font-bold uppercase tracking-wider mb-0.5 opacity-80">
                {status === 'upcoming' ? '⏰ Pre-Order Starts In' : '🔥 Pre-Order Live'}
            </div>
            <div className="text-base font-bold font-mono leading-tight">
                {timeLeft}
            </div>
            {endDate && status === 'active' && (
                <div className="text-[10px] mt-0.5 opacity-75">
                    Ends {new Date(endDate).toLocaleDateString()}
                </div>
            )}
            {status === 'upcoming' && (
                <div className="text-[10px] mt-0.5 opacity-75">
                    Available {new Date(availableDate).toLocaleDateString()}
                </div>
            )}
        </div>
    );
};

export default PreOrderTimer;
