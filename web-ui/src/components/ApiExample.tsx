import React, { useState, useEffect, useCallback } from 'react';
import '../styles/ApiExample.css';

const ApiExample: React.FC = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5秒超时
      
      const response = await fetch('/api', { 
        signal: controller.signal 
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage(data.message);
      setError('');
      setRetryCount(0); // 重置重试计数
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setMessage('');
      
      // 如果是网络错误且重试次数小于3，则自动重试
      if (err instanceof TypeError && err.message.includes('network') && retryCount < 3) {
        setRetryCount(prev => prev + 1);
        setTimeout(fetchData, 1000 * retryCount); // 指数退避重试
      }
    } finally {
      setIsLoading(false);
    }
  }, [retryCount]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="api-example">
      <h3>API Response:</h3>
      {isLoading ? (
        <div className="loading-spinner">Loading...</div>
      ) : error ? (
        <div className="error-message">
          Error: {error}
          {retryCount < 3 && (
            <button 
              className="retry-button" 
              onClick={() => setRetryCount(prev => prev + 1)}
            >
              重试
            </button>
          )}
        </div>
      ) : (
        <p className="success-message">{message}</p>
      )}
    </div>
  );
};

export default ApiExample;