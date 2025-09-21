import React from 'react';
import { motion } from 'framer-motion';

const Button = ({ 
  children, 
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  onClick,
  ...props 
}) => {
  const baseClasses = "relative inline-flex items-center justify-center font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black";
  
  const variants = {
    primary: "bg-gradient-to-r from-cyan-500 to-purple-600 text-white hover:from-cyan-400 hover:to-purple-500 focus:ring-cyan-500/50 shadow-lg hover:shadow-cyan-500/25",
    secondary: "bg-white/10 text-white border border-white/20 hover:bg-white/20 hover:border-white/30 focus:ring-white/50",
    ghost: "text-white/80 hover:text-white hover:bg-white/10 focus:ring-white/50",
    danger: "bg-gradient-to-r from-red-500 to-pink-600 text-white hover:from-red-400 hover:to-pink-500 focus:ring-red-500/50 shadow-lg hover:shadow-red-500/25",
    success: "bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-400 hover:to-emerald-500 focus:ring-green-500/50 shadow-lg hover:shadow-green-500/25"
  };

  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg",
    xl: "px-10 py-5 text-xl"
  };

  const disabledClasses = disabled 
    ? "opacity-50 cursor-not-allowed" 
    : "";

  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.05 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
      onClick={disabled ? undefined : onClick}
      className={`
        ${baseClasses} 
        ${variants[variant]} 
        ${sizes[size]} 
        ${disabledClasses} 
        ${className}
      `}
      {...props}
    >
      {/* Glow effect for primary variant */}
      {variant === 'primary' && !disabled && (
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-600 opacity-0 hover:opacity-20 blur-sm transition-opacity duration-300" />
      )}
      
      {/* Loading spinner */}
      {loading && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full mr-2"
        />
      )}
      
      {/* Button content */}
      <span className="relative z-10">
        {children}
      </span>
    </motion.button>
  );
};

// Icon Button Component
export const IconButton = ({ 
  icon, 
  variant = 'ghost',
  size = 'md',
  className = '',
  ...props 
}) => {
  const sizes = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12"
  };

  return (
    <Button
      variant={variant}
      className={`${sizes[size]} p-0 ${className}`}
      {...props}
    >
      {icon}
    </Button>
  );
};

// Button Group Component
export const ButtonGroup = ({ children, className = '' }) => (
  <div className={`flex space-x-2 ${className}`}>
    {children}
  </div>
);

export default Button;
