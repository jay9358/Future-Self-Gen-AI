# Future Self Advisor - Futuristic Frontend

A production-ready React application with a sleek, futuristic UI built with Tailwind CSS and Framer Motion.

## 🚀 Features

- **Futuristic Design**: Glassmorphism, gradients, neon glows, and smooth animations
- **Responsive Layout**: Mobile-first design that works on all devices
- **Interactive Components**: Hover effects, smooth transitions, and micro-interactions
- **Dark Mode First**: Optimized for dark themes with accent colors
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support

## 🎨 Design System

### Color Palette
- **Primary**: Cyan (#06b6d4) to Purple (#8b5cf6) gradients
- **Background**: Dark gradient from gray-900 to black
- **Glass**: Semi-transparent white overlays with backdrop blur
- **Accents**: Neon cyan, purple, and green for highlights

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300-800
- **Scale**: Responsive text sizing

### Components
- **Navbar**: Fixed header with glassmorphism
- **Cards**: Multiple variants (glass, dark, accent)
- **Buttons**: Primary, secondary, ghost variants with hover effects
- **Inputs**: Futuristic styling with focus states
- **ChatBox**: Real-time messaging interface
- **Progress**: Linear and circular progress indicators
- **Modals**: Overlay dialogs with backdrop blur
- **Badges**: Status indicators and skill tags

## 🛠️ Tech Stack

- **React 18**: Latest React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Axios**: HTTP client for API calls
- **React Scripts**: Build tooling

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🎯 Usage

### Basic Component Usage

```jsx
import { Card, Button, Input, ChatBox } from './components/ui';

// Card with glassmorphism
<Card variant="glass" glow>
  <CardHeader>
    <CardTitle>Future Insights</CardTitle>
  </CardHeader>
  <CardBody>
    Content goes here
  </CardBody>
</Card>

// Button with hover effects
<Button variant="primary" size="lg">
  Start Journey
</Button>

// Input with focus glow
<Input 
  label="Your Name"
  placeholder="Enter your name"
  variant="glass"
/>

// Chat interface
<ChatBox
  messages={messages}
  onSendMessage={handleSend}
  placeholder="Ask your future self..."
/>
```

### Animation Examples

```jsx
import { motion } from 'framer-motion';

// Fade in animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
>
  Content
</motion.div>

// Hover scale effect
<motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Interactive Element
</motion.div>
```

## 🎨 Customization

### Theme Colors
Edit `tailwind.config.js` to customize colors:

```javascript
colors: {
  'cyan': {
    500: '#06b6d4', // Your custom cyan
  },
  'purple': {
    500: '#8b5cf6', // Your custom purple
  }
}
```

### Component Variants
Add new variants in component files:

```jsx
const variants = {
  custom: "bg-gradient-to-r from-green-500 to-blue-600",
  // ... other variants
};
```

## 📱 Responsive Design

The UI is fully responsive with breakpoints:
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px  
- **Desktop**: > 1024px

## ♿ Accessibility

- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Color Contrast**: WCAG AA compliant color ratios
- **Reduced Motion**: Respects user's motion preferences

## 🚀 Performance

- **Code Splitting**: Automatic code splitting with React.lazy
- **Image Optimization**: Optimized images and lazy loading
- **Bundle Size**: Minimal bundle size with tree shaking
- **Animations**: Hardware-accelerated animations with Framer Motion

## 🔧 Development

### Project Structure
```
src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── FuturisticResumeUpload.jsx
│   ├── FuturisticChat.jsx
│   └── FuturisticDashboard.jsx
├── App.js            # Main application
├── App.css           # Global styles
└── index.css         # Tailwind imports
```

### Adding New Components

1. Create component in `src/components/ui/`
2. Export from `src/components/ui/index.js`
3. Import and use in your app

### Styling Guidelines

- Use Tailwind classes for styling
- Create custom components for repeated patterns
- Use Framer Motion for animations
- Follow the established design system

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or support, please open an issue on GitHub.