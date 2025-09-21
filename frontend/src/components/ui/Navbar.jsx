import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Navbar = ({ isConnected = false, onConnect }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <motion.nav 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className=" top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/20 border-b border-cyan-500/20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-3"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FS</span>
            </div>
            <span className="text-xl font-light text-white/90">Future Self</span>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#about">About</NavLink>
            <NavLink href="#contact">Contact</NavLink>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-cyan-400 shadow-lg shadow-cyan-400/50' : 'bg-gray-500'}`} />
              <span className="text-sm text-white/70">
                {isConnected ? 'Connected' : 'Offline'}
              </span>
            </div>

            {/* CTA Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onConnect}
              className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-cyan-500/25 transition-all duration-300"
            >
              Start Journey
            </motion.button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20"
            >
              <div className="w-6 h-6 flex flex-col justify-center space-y-1">
                <motion.div 
                  animate={{ rotate: isMenuOpen ? 45 : 0, y: isMenuOpen ? 6 : 0 }}
                  className="w-full h-0.5 bg-white rounded"
                />
                <motion.div 
                  animate={{ opacity: isMenuOpen ? 0 : 1 }}
                  className="w-full h-0.5 bg-white rounded"
                />
                <motion.div 
                  animate={{ rotate: isMenuOpen ? -45 : 0, y: isMenuOpen ? -6 : 0 }}
                  className="w-full h-0.5 bg-white rounded"
                />
              </div>
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ 
            opacity: isMenuOpen ? 1 : 0, 
            height: isMenuOpen ? 'auto' : 0 
          }}
          transition={{ duration: 0.3 }}
          className="md:hidden overflow-hidden"
        >
          <div className="py-4 space-y-4 border-t border-white/10">
            <NavLink href="#features" mobile>Features</NavLink>
            <NavLink href="#about" mobile>About</NavLink>
            <NavLink href="#contact" mobile>Contact</NavLink>
            <button
              onClick={onConnect}
              className="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-lg font-medium"
            >
              Start Journey
            </button>
          </div>
        </motion.div>
      </div>
    </motion.nav>
  );
};

const NavLink = ({ href, children, mobile = false }) => (
  <motion.a
    href={href}
    whileHover={{ x: 5 }}
    className={`block text-white/80 hover:text-white transition-colors duration-300 ${
      mobile ? 'px-4 py-2' : ''
    }`}
  >
    {children}
  </motion.a>
);

export default Navbar;
