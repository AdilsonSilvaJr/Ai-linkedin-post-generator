# LinkedIn Post Generator Frontend

Modern React frontend for the LinkedIn Post Generator, built with TypeScript and Vite.

## 🚀 Features

- Modern React 19 with TypeScript
- Vite for fast development and building
- Type-safe API integration
- Material-UI components
- ESLint configuration with React plugin

## 🛠️ Technical Stack

- React 19
- TypeScript
- Vite
- Material-UI
- ESLint
- React Query

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/   # React components
│   ├── hooks/       # Custom React hooks
│   ├── pages/       # Page components
│   ├── services/    # API services
│   └── types/       # TypeScript types
├── public/          # Static assets
└── package.json     # Dependencies
```

## 📥 Installation

```bash
yarn install
```

## 🚀 Development

```bash
yarn dev
```

## 🔧 ESLint Configuration

Configure ESLint for type-aware linting:

```javascript
// filepath: eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  languageOptions: {
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
  settings: { 
    react: { version: '19.0' } 
  },
  plugins: {
    react,
  },
  rules: {
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```

## 📝 License

MIT License
