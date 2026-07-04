import { useState, useEffect, useRef, useCallback } from 'react';
import {
  listSessions,
  getMessages,
  createSession,
  sendMessage,
  Session,
  Message,
} from '../api';
import { MessageBubble } from './Message';

export function Chat() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const streamContentRef = useRef('');

  // Keep ref in sync with state
  useEffect(() => {
    streamContentRef.current = streamContent;
  }, [streamContent]);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamContent]);

  const loadSessions = async () => {
    try {
      setLoadingSessions(true);
      const data = await listSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      setLoadingMessages(true);
      const data = await getMessages(sessionId);
      setMessages(data);
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setStreamContent('');
    setStreaming(false);
    loadMessages(sessionId);
    setSidebarOpen(false);
  };

  const handleNewChat = async () => {
    try {
      const session = await createSession();
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
      setStreamContent('');
      setStreaming(false);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;

    // Abort any ongoing stream
    if (abortRef.current) {
      abortRef.current.abort();
    }

    setInput('');
    setStreaming(true);
    setStreamContent('');
    streamContentRef.current = '';

    // Add user message optimistically
    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const abortController = new AbortController();
    abortRef.current = abortController;

    try {
      const stream = await sendMessage(text, activeSessionId || undefined);
      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let newSessionId = activeSessionId;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') continue;
            try {
              const data = JSON.parse(payload);

              // OpenAI-compatible format: choices[0].delta.content
              const delta = data.choices?.[0]?.delta;
              if (delta?.content) {
                streamContentRef.current += delta.content;
                setStreamContent((prev) => prev + delta.content);
              }

              // Track session if provided
              if (data.session_id) {
                newSessionId = data.session_id;
                setActiveSessionId(newSessionId);
                loadSessions();
              }
            } catch {
              // Ignore parse errors for partial chunks
            }
          }
        }
      }

      // Flush remaining buffer
      if (buffer.startsWith('data: ')) {
        const payload = buffer.slice(6).trim();
        if (payload !== '[DONE]') {
          try {
            const data = JSON.parse(payload);
            const delta = data.choices?.[0]?.delta;
            if (delta?.content) {
              streamContentRef.current += delta.content;
              setStreamContent((prev) => prev + delta.content);
            }
            if (data.session_id) {
              newSessionId = data.session_id;
              setActiveSessionId(newSessionId);
              loadSessions();
            }
          } catch { /* ignore */ }
        }
      }

      // Add assistant message using ref for final content
      const finalContent = streamContentRef.current || buffer;
      const assistantMsg: Message = {
        id: `temp-${Date.now()}-assistant`,
        session_id: newSessionId || '',
        role: 'assistant',
        content: finalContent || '(empty response)',
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setStreamContent('');

      // Reload messages from server for this session
      if (newSessionId) {
        loadMessages(newSessionId);
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        return;
      }
      console.error('Send failed:', err);
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [input, streaming, activeSessionId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize textarea
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  };

  return (
    <div className="chat-layout">
      {/* Mobile hamburger */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle sidebar"
        style={{
          display: 'none',
          position: 'absolute',
          top: 8,
          left: 8,
          zIndex: 30,
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          color: 'var(--text-primary)',
          borderRadius: 'var(--radius-sm)',
          padding: '6px 10px',
          cursor: 'pointer',
          fontSize: '18px',
        }}
      >
        ☰
      </button>

      {/* Sidebar */}
      <aside className={`chat-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={handleNewChat}>
            + New Chat
          </button>
        </div>
        <div className="sessions-list">
          {loadingSessions ? (
            <div className="loading-indicator">
              <div className="dot" />
              <div className="dot" />
              <div className="dot" />
            </div>
          ) : sessions.length === 0 ? (
            <div
              style={{
                padding: '16px',
                color: 'var(--text-muted)',
                fontSize: '13px',
                textAlign: 'center',
              }}
            >
              No sessions yet
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
                onClick={() => handleSelectSession(session.id)}
              >
                {session.title || `Chat ${session.id.slice(0, 8)}`}
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          style={{
            display: 'none',
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 15,
          }}
        />
      )}

      {/* Main Chat Area */}
      <div className="chat-area">
        <div className="chat-messages">
          {loadingMessages ? (
            <div className="empty-chat">
              <div className="loading-indicator">
                <div className="dot" />
                <div className="dot" />
                <div className="dot" />
              </div>
            </div>
          ) : messages.length === 0 && !streaming ? (
            <div className="empty-chat">
              <h2>Hermes Gateway</h2>
              <p>Start a conversation by typing a message below.</p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {streaming && (
                <div className="message-row assistant">
                  <div className="message-bubble streaming-cursor">
                    {streamContent || (
                      <div className="loading-indicator">
                        <div className="dot" />
                        <div className="dot" />
                        <div className="dot" />
                      </div>
                    )}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="chat-input-area">
          <div className="chat-input-container">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
              rows={1}
              disabled={streaming}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || streaming}
              aria-label="Send message"
            >
              ↑
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
