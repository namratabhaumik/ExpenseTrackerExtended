module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "react-app",
    "react-app/jest",
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: "module",
  },
  plugins: ["react", "react-hooks", "jsx-a11y"],
  rules: {
    "react/react-in-jsx-scope": "off", // Not needed in React 17+
    "react/prop-types": "warn", // Warn about missing prop types
    "no-unused-vars": "warn",
    "no-console": "warn", // Warn about console statements
    "prefer-const": "error",
    "no-var": "error",
    "object-shorthand": "error",
    "prefer-template": "error",
    "template-curly-spacing": "error",
    "arrow-spacing": "error",
    "comma-dangle": ["error", "always-multiline"],
    semi: ["error", "always"],
    quotes: ["error", "single"],
    indent: ["error", 2],
    "max-len": "off",
    "testing-library/no-unnecessary-act": "off", // Disable false positive warnings
  },
  settings: {
    react: {
      version: "detect",
    },
  },
};
