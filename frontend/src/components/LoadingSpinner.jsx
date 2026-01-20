import React from 'react';
import { Loader2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const LoadingSpinner = ({ size = 'md', message = 'Loading...' }) => {
    const { isDark } = useTheme();
    
    const sizes = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
        xl: 'h-16 w-16'
    };
    
    return (
        <div className="flex flex-col items-center justify-center p-8">
            <Loader2 
                className={`${sizes[size]} animate-spin ${
                    isDark ? 'text-purple-400' : 'text-emerald-600'
                }`}
            />
            {message && (
                <p className={`mt-4 text-sm ${
                    isDark ? 'text-neutral-400' : 'text-slate-600'
                }`}>
                    {message}
                </p>
            )}
        </div>
    );
};

export default LoadingSpinner;
