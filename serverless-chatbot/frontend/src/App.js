// App.js - Main React Application
// ===================================
// This is the root component of our React chatbot frontend.
// It manages the overall application state and layout.

import React, { useState, useCallback } from 'react';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import './App.css';

// API base URL — reads from environment variable or defaults to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Generate a random session ID to group messages in a conversation
const generateSessionId = () => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

function App() {
  // ─── State ───────────────────────────────────────────────────
  const [messages, setMessages] = useState([
    // Welcome message shown when the app starts
    {
      id: 1,
      type: 'bot',
      text: "👋 Hello! I'm your AI chatbot. Ask me anything!",
      timestamp: new Date().toISOString(),
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);   // Show loading indicator
  const [error, setError] = useState(null);              // Show error messages
  const [sessionId] = useState(generateSessionId);       // Persist for this session
  const [modelVersion, setModelVersion] = useState('');  // Track model version

  // ─── Send Message Handler ────────────────────────────────────
  const sendMessage = useCallback(async (userText) => {
    if (!userText.trim() || isLoading) return;

    // Clear any previous error
    setError(null);

    // Add the user's message to the chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: userText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send request to our FastAPI backend
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userText,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Server error');
      }

      const data = await response.json();

      // Track model version for display
      if (data.model_version) setModelVersion(data.model_version);

      // Add bot's response to chat
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: data.response,
        timestamp: data.timestamp,
        responseTime: data.response_time_ms,
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      // Handle different types of errors
      let errorMsg = 'Something went wrong. Please try again.';

      if (err.message.includes('Failed to fetch')) {
        errorMsg = '⚠️ Cannot connect to server. Make sure the backend is running on port 8000.';
      } else if (err.message) {
        errorMsg = `❌ Error: ${err.message}`;
      }

      setError(errorMsg);

      // Add error message to chat as a bot message
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        text: errorMsg,
        timestamp: new Date().toISOString(),
        isError: true,
      }]);

    } finally {
      setIsLoading(false);  // Always hide loading indicator
    }
  }, [isLoading, sessionId]);

  // ─── Render ──────────────────────────────────────────────────
  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <div className="bot-avatar">🤖</div>
          <div className="header-info">
            <h1 className="app-title">Serverless Chatbot</h1>
            <span className="app-subtitle">MLOps-Powered AI Assistant</span>
          </div>
        </div>
        <div className="header-right">
          {modelVersion && (
            <div className="version-badge">
              v{modelVersion}
            </div>
          )}
          <div className="status-indicator">
            <span className="status-dot"></span>
            Online
          </div>
        </div>
      </header>

      {/* Chat area */}
      <main className="app-main">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
        />
      </main>

      {/* Error banner */}
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)} className="error-close">✕</button>
        </div>
      )}

      {/* Input area */}
      <footer className="app-footer">
        <InputBar
          onSend={sendMessage}
          isLoading={isLoading}
        />
        <p className="session-info">Session: {sessionId.slice(-8)}</p>
      </footer>
    </div>
  );
}

export default App;
