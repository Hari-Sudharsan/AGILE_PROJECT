// components/InputBar.js
// ===================================
// The message input area at the bottom of the chat.
// Handles keyboard shortcuts (Enter to send) and disabled state.

import React, { useState, useRef } from 'react';

function InputBar({ onSend, isLoading }) {
  const [inputText, setInputText] = useState('');
  const inputRef = useRef(null);

  // Handle form submission
  const handleSend = () => {
    const text = inputText.trim();
    if (!text || isLoading) return;

    onSend(text);
    setInputText('');         // Clear input after sending
    inputRef.current?.focus(); // Keep focus on input
  };

  // Allow pressing Enter to send (Shift+Enter for new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();  // Don't add a newline
      handleSend();
    }
  };

  return (
    <div className="input-bar">
      <textarea
        ref={inputRef}
        className="message-input"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message... (Enter to send)"
        disabled={isLoading}
        rows={1}
        maxLength={500}
      />

      {/* Character counter */}
      {inputText.length > 400 && (
        <span className="char-counter">{inputText.length}/500</span>
      )}

      {/* Send button */}
      <button
        className={`send-button ${isLoading ? 'loading' : ''}`}
        onClick={handleSend}
        disabled={isLoading || !inputText.trim()}
        title="Send message (Enter)"
      >
        {isLoading ? '⏳' : '➤'}
      </button>
    </div>
  );
}

export default InputBar;
