import React, { useState, forwardRef } from 'react';
import { motion } from 'framer-motion';

const Input = forwardRef(({ 
  label,
  placeholder,
  type = 'text',
  variant = 'default',
  size = 'md',
  disabled = false,
  error = false,
  helperText,
  className = '',
  icon,
  iconPosition = 'left',
  ...props 
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);

  const baseClasses = "w-full rounded-lg border transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black";
  
  const variants = {
    default: "bg-white/5 border-white/20 text-white placeholder-white/50 focus:border-cyan-400 focus:ring-cyan-400/50",
    glass: "bg-white/10 border-white/30 text-white placeholder-white/60 focus:border-cyan-400 focus:ring-cyan-400/50",
    dark: "bg-black/20 border-gray-700 text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-cyan-400/50"
  };

  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-3 text-base",
    lg: "px-5 py-4 text-lg"
  };

  const errorClasses = error 
    ? "border-red-400 focus:border-red-400 focus:ring-red-400/50" 
    : "";

  const disabledClasses = disabled 
    ? "opacity-50 cursor-not-allowed" 
    : "";

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-white/80">
          {label}
        </label>
      )}
      
      {/* Input Container */}
      <div className="relative">
        {/* Icon */}
        {icon && iconPosition === 'left' && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50">
            {icon}
          </div>
        )}
        
        {/* Input Field */}
        <motion.input
          ref={ref}
          type={type}
          placeholder={placeholder}
          disabled={disabled}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={`
            ${baseClasses} 
            ${variants[variant]} 
            ${sizes[size]} 
            ${errorClasses} 
            ${disabledClasses}
            ${icon && iconPosition === 'left' ? 'pl-10' : ''}
            ${icon && iconPosition === 'right' ? 'pr-10' : ''}
          `}
          {...props}
        />
        
        {/* Right Icon */}
        {icon && iconPosition === 'right' && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/50">
            {icon}
          </div>
        )}
        
        {/* Focus Glow Effect */}
        {isFocused && !disabled && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 pointer-events-none"
          />
        )}
      </div>
      
      {/* Helper Text */}
      {helperText && (
        <p className={`text-xs ${error ? 'text-red-400' : 'text-white/60'}`}>
          {helperText}
        </p>
      )}
    </div>
  );
});

// Textarea Component
export const Textarea = forwardRef(({ 
  label,
  placeholder,
  rows = 4,
  variant = 'default',
  disabled = false,
  error = false,
  helperText,
  className = '',
  ...props 
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);

  const baseClasses = "w-full rounded-lg border transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black resize-none";
  
  const variants = {
    default: "bg-white/5 border-white/20 text-white placeholder-white/50 focus:border-cyan-400 focus:ring-cyan-400/50",
    glass: "bg-white/10 border-white/30 text-white placeholder-white/60 focus:border-cyan-400 focus:ring-cyan-400/50",
    dark: "bg-black/20 border-gray-700 text-white placeholder-gray-400 focus:border-cyan-400 focus:ring-cyan-400/50"
  };

  const errorClasses = error 
    ? "border-red-400 focus:border-red-400 focus:ring-red-400/50" 
    : "";

  const disabledClasses = disabled 
    ? "opacity-50 cursor-not-allowed" 
    : "";

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-white/80">
          {label}
        </label>
      )}
      
      {/* Textarea Container */}
      <div className="relative">
        <motion.textarea
          ref={ref}
          placeholder={placeholder}
          rows={rows}
          disabled={disabled}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={`
            ${baseClasses} 
            ${variants[variant]} 
            ${errorClasses} 
            ${disabledClasses}
            px-4 py-3
          `}
          {...props}
        />
        
        {/* Focus Glow Effect */}
        {isFocused && !disabled && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500/10 to-purple-500/10 pointer-events-none"
          />
        )}
      </div>
      
      {/* Helper Text */}
      {helperText && (
        <p className={`text-xs ${error ? 'text-red-400' : 'text-white/60'}`}>
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
Textarea.displayName = 'Textarea';

export default Input;
