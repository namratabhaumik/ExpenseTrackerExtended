module.exports = {
  // Automatically clear mock calls and instances between every test
  clearMocks: true,

  // Indicates whether the coverage information should be collected while executing the test
  collectCoverage: true,

  // An array of glob patterns indicating a set of files for which coverage information should be collected
  collectCoverageFrom: [
    "src/**/*.{js,jsx}",
    "!src/index.js",
    "!src/reportWebVitals.js",
    "!src/setupTests.js",
    "!src/**/*.test.{js,jsx}",
    "!src/**/*.spec.{js,jsx}",
  ],

  // The directory where Jest should output its coverage files
  coverageDirectory: "coverage",

  // An array of file extensions your modules use
  moduleFileExtensions: ["js", "jsx", "json", "node"],

  // A map from regular expressions to module names that allow to stub out resources with a single module
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },

  // Transform configuration
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  
  // Don't ignore node_modules for transformation (needed for axios)
  transformIgnorePatterns: [
    '/node_modules/(?!(axios|@babel/runtime)/)',
  ],

  // The test environment that will be used for testing
  testEnvironment: "jsdom",

  // The glob patterns Jest uses to detect test files
  testMatch: [
    "<rootDir>/src/**/__tests__/**/*.{js,jsx}",
    "<rootDir>/src/**/*.{test,spec}.{js,jsx}",
  ],

  // An array of regexp pattern strings that are matched against all test paths, matched tests are skipped
  testPathIgnorePatterns: ["/node_modules/", "/build/", "/dist/"],

  // The regexp pattern or array of patterns that Jest uses to detect test files
  testRegex: "(/__tests__/.*|(\\.|/)(test|spec))\\.(jsx?|tsx?)$",

  // This option allows the use of a custom results processor
  // testResultsProcessor: "jest-sonar-reporter", // Commented out - package not installed

  // Indicates whether each individual test should be reported during the run
  verbose: true,

  // Setup files that will be run before each test
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.js"],

  // A list of paths to modules that run some code to configure or set up the testing framework before each test
  setupFiles: ["<rootDir>/src/setupTests.js"],

  // The maximum amount of workers used to run your tests
  maxWorkers: "50%",

  // Indicates whether the coverage information should be collected while executing the test
  collectCoverageFrom: [
    "src/**/*.{js,jsx}",
    "!src/index.js",
    "!src/reportWebVitals.js",
    "!src/setupTests.js",
    "!src/**/*.test.{js,jsx}",
    "!src/**/*.spec.{js,jsx}",
    "!src/**/__tests__/**",
  ],

  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
