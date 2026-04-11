// components/MessageBubble.js
// ===================================
// Renders a single chat message bubble.
// Different styling for user vs bot messages.

import React from 'react';

function MessageBubble({ message }) {
  const isUser = message.type === 'user';

  // Format timestamp for display
  const formatTime = (isoString) => {
    try {
      return new Date(isoString).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'} ${message.isError ? 'error-message' : ''}`}>

      {/* Bot avatar (only shown for bot messages) */}
      {!isUser && (
        <div className="message-avatar">🤖</div>
      )}

      {/* Message content */}
      <div className="message-content">
        <div className="message-bubble">
          {message.text}
        </div>

        {/* Metadata: time and response speed */}
        <div className="message-meta">
          <span className="message-time">{formatTime(message.timestamp)}</span>
          {message.responseTime && (
            <span className="message-speed">⚡ {message.responseTime}ms</span>
          )}
        </div>
      </div>

      {/* User avatar (only shown for user messages) */}
      {isUser && (
        <div className="message-avatar user-avatar">👤</div>
      )}
    </div>
  );
}

export default MessageBubble;
