// components/ChatWindow.js
// ===================================
// Displays the scrollable chat message history.
// Auto-scrolls to the latest message.

import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';

function ChatWindow({ messages, isLoading }) {
  // Reference to the bottom of the chat — used for auto-scrolling
  const bottomRef = useRef(null);

  // Scroll to bottom whenever new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {/* Render each message */}
      {messages.map(message => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {/* Loading indicator — shown while waiting for bot response */}
      {isLoading && (
        <div className="message bot-message loading-message">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}

      {/* Invisible div at the bottom for auto-scroll target */}
      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;
