import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../api';

interface Props {
  message: Message;
  toolsUsed?: string[];
}

export function MessageBubble({ message, toolsUsed }: Props) {
  const isUser = message.role === 'user';
  const [reasoningOpen, setReasoningOpen] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        {!isUser && toolsUsed && toolsUsed.length > 0 && (
          <div className="tools-indicator">
            <span
              className="tools-icon"
              onMouseEnter={() => setToolsOpen(true)}
              onMouseLeave={() => setToolsOpen(false)}
              title={toolsUsed.join(', ')}
            >
              🛠️ {toolsUsed.length}
            </span>
            {toolsOpen && (
              <div className="tools-tooltip">
                {toolsUsed.map((t) => (
                  <span key={t} className="tool-tag">{t}</span>
                ))}
              </div>
            )}
          </div>
        )}
        {!isUser && message.reasoning && (
          <details className="reasoning-block" open={reasoningOpen} onToggle={(e) => setReasoningOpen((e.target as HTMLDetailsElement).open)}>
            <summary className="reasoning-summary">🧠 Razonamiento</summary>
            <div className="reasoning-content">{message.reasoning}</div>
          </details>
        )}
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
}
