// Helper exported for easier testing. Keeps original behavior unchanged.
export function invokeWebVitalsHandlers(onPerfEntry, webVitals) {
  const { getCLS, getFID, getFCP, getLCP, getTTFB } = webVitals;
  getCLS(onPerfEntry);
  getFID(onPerfEntry);
  getFCP(onPerfEntry);
  getLCP(onPerfEntry);
  getTTFB(onPerfEntry);
}

const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then((mod) => invokeWebVitalsHandlers(onPerfEntry, mod));
  }
};

export default reportWebVitals;
