import React from 'react';
import { motion } from 'framer-motion';

const Card = ({ 
  children, 
  className = '', 
  variant = 'default',
  glow = false,
  interactive = false,
  ...props 
}) => {
  const baseClasses = "relative rounded-2xl backdrop-blur-xl border transition-all duration-500";
  
  const variants = {
    default: "bg-white/5 border-white/10 hover:border-white/20",
    glass: "bg-white/10 border-white/20 hover:border-white/30",
    dark: "bg-black/20 border-gray-800/50 hover:border-gray-700/70",
    accent: "bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border-cyan-500/30 hover:border-cyan-400/50"
  };

  const interactiveClasses = interactive 
    ? "hover:scale-[1.02] hover:shadow-2xl cursor-pointer" 
    : "";

  const glowClasses = glow 
    ? "shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20" 
    : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      whileHover={interactive ? { y: -5 } : {}}
      className={`
        ${baseClasses} 
        ${variants[variant]} 
        ${interactiveClasses} 
        ${glowClasses} 
        ${className}
      `}
      {...props}
    >
      {/* Subtle inner glow effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  );
};

// Card Header Component
export const CardHeader = ({ children, className = '' }) => (
  <div className={`p-6 pb-4 ${className}`}>
    {children}
  </div>
);

// Card Body Component
export const CardBody = ({ children, className = '' }) => (
  <div className={`px-6 pb-6 ${className}`}>
    {children}
  </div>
);

// Card Footer Component
export const CardFooter = ({ children, className = '' }) => (
  <div className={`p-6 pt-4 border-t border-white/10 ${className}`}>
    {children}
  </div>
);

// Card Title Component
export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-xl font-semibold text-white/90 ${className}`}>
    {children}
  </h3>
);

// Card Description Component
export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-white/60 mt-2 ${className}`}>
    {children}
  </p>
);

export default Card;
