import React from 'react';
import { motion } from 'framer-motion';

const Badge = ({ 
  children, 
  variant = 'default',
  size = 'md',
  glow = false,
  className = ''
}) => {
  const baseClasses = "inline-flex items-center font-medium rounded-full transition-all duration-300";
  
  const variants = {
    default: "bg-white/10 text-white/80 border border-white/20",
    primary: "bg-gradient-to-r from-cyan-500 to-purple-600 text-white",
    success: "bg-gradient-to-r from-green-500 to-emerald-600 text-white",
    warning: "bg-gradient-to-r from-yellow-500 to-orange-600 text-white",
    danger: "bg-gradient-to-r from-red-500 to-pink-600 text-white",
    info: "bg-gradient-to-r from-blue-500 to-indigo-600 text-white",
    ghost: "bg-transparent text-white/60 border border-white/20"
  };

  const sizes = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base"
  };

  const glowClasses = glow 
    ? "shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40" 
    : "";

  return (
    <motion.span
      whileHover={{ scale: 1.05 }}
      className={`
        ${baseClasses} 
        ${variants[variant]} 
        ${sizes[size]} 
        ${glowClasses} 
        ${className}
      `}
    >
      {children}
    </motion.span>
  );
};

// Status Badge Component
export const StatusBadge = ({ 
  status, 
  size = 'md',
  className = ''
}) => {
  const statusConfig = {
    online: { variant: 'success', text: 'Online' },
    offline: { variant: 'default', text: 'Offline' },
    busy: { variant: 'warning', text: 'Busy' },
    away: { variant: 'info', text: 'Away' },
    error: { variant: 'danger', text: 'Error' }
  };

  const config = statusConfig[status] || statusConfig.offline;

  return (
    <Badge 
      variant={config.variant} 
      size={size} 
      className={className}
    >
      <div className={`w-2 h-2 rounded-full mr-2 ${
        status === 'online' ? 'bg-green-400' : 
        status === 'busy' ? 'bg-yellow-400' : 
        status === 'away' ? 'bg-blue-400' : 
        'bg-gray-400'
      }`} />
      {config.text}
    </Badge>
  );
};

// Skill Badge Component
export const SkillBadge = ({ 
  skill, 
  level = 'intermediate',
  size = 'md',
  className = ''
}) => {
  const levelConfig = {
    beginner: { variant: 'info', text: 'Beginner' },
    intermediate: { variant: 'primary', text: 'Intermediate' },
    advanced: { variant: 'success', text: 'Advanced' },
    expert: { variant: 'warning', text: 'Expert' }
  };

  const config = levelConfig[level] || levelConfig.intermediate;

  return (
    <Badge 
      variant={config.variant} 
      size={size} 
      glow={level === 'expert'}
      className={className}
    >
      {skill}
    </Badge>
  );
};

// Notification Badge Component
export const NotificationBadge = ({ 
  count, 
  max = 99,
  size = 'sm',
  className = ''
}) => {
  const displayCount = count > max ? `${max}+` : count.toString();

  return (
    <motion.span
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      className={`
        absolute -top-2 -right-2 bg-gradient-to-r from-red-500 to-pink-600 
        text-white text-xs font-bold rounded-full min-w-[20px] h-5 
        flex items-center justify-center px-1 shadow-lg
        ${className}
      `}
    >
      {displayCount}
    </motion.span>
  );
};

export default Badge;
