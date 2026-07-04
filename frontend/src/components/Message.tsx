import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../api';

interface Props {
  message: Message;
  skills?: string[];
}

export function MessageBubble({ message, skills }: Props) {
  const isUser = message.role === 'user';
  const [reasoningOpen, setReasoningOpen] = useState(false);
  const [skillsOpen, setSkillsOpen] = useState(false);

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        {!isUser && skills && skills.length > 0 && (
          <div className="skills-indicator">
            <span
              className="skills-icon"
              onMouseEnter={() => setSkillsOpen(true)}
              onMouseLeave={() => setSkillsOpen(false)}
              title={skills.join(', ')}
            >
              🧰
            </span>
            {skillsOpen && (
              <div className="skills-tooltip">
                {skills.map((s) => (
                  <span key={s} className="skill-tag">{s}</span>
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
