import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../api';

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';
  const [reasoningOpen, setReasoningOpen] = useState(false);

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
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
