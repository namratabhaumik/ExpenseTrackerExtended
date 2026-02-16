/**
 * Ensure index boots without error and calls reportWebVitals
 */
import React from 'react';

// create a root element that index.js expects
beforeEach(() => {
  const root = document.createElement('div');
  root.setAttribute('id', 'root');
  document.body.appendChild(root);
});

afterEach(() => {
  document.body.innerHTML = '';
  jest.resetModules();
});

jest.mock('./reportWebVitals', () => jest.fn());

test('index renders App and calls reportWebVitals', () => {
  // require the module after mocking
  require('./index');
  const reportWebVitals = require('./reportWebVitals');
  expect(reportWebVitals).toHaveBeenCalled();
});
