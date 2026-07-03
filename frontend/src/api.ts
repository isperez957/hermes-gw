const API_URL: string =
  import.meta.env.VITE_API_URL || '';

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

function getToken(): string | null {
  return localStorage.getItem('hermes_token');
}

function setToken(token: string): void {
  localStorage.setItem('hermes_token', token);
}

function clearToken(): void {
  localStorage.removeItem('hermes_token');
}

async function authFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.location.reload();
    throw new Error('Unauthorized');
  }

  return response;
}

export async function login(
  username: string,
  password: string
): Promise<boolean> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    return false;
  }

  const data = await response.json();
  setToken(data.token);
  return true;
}

export function logout(): void {
  clearToken();
  window.location.reload();
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export async function sendMessage(
  text: string,
  sessionId?: string
): Promise<ReadableStream<Uint8Array>> {
  const response = await authFetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: text,
      session_id: sessionId || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  return new ReadableStream({
    async start(controller) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          controller.close();
          break;
        }
        controller.enqueue(value);
      }
    },
  });
}

export async function listSessions(): Promise<Session[]> {
  const response = await authFetch('/api/sessions');
  if (!response.ok) {
    throw new Error('Failed to list sessions');
  }
  return response.json();
}

export async function getMessages(sessionId: string): Promise<Message[]> {
  const response = await authFetch(`/api/sessions/${sessionId}/messages`);
  if (!response.ok) {
    throw new Error('Failed to get messages');
  }
  return response.json();
}

export async function createSession(): Promise<Session> {
  const response = await authFetch('/api/sessions', {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to create session');
  }
  return response.json();
}
