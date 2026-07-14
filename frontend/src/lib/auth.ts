export interface User {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'doctor';
  avatar?: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export function login(email: string, password: string, role: 'patient' | 'doctor'): Promise<{ token: string; user: User }> {
  return new Promise((resolve, reject) => {
    fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, role }),
    })
      .then(async (response) => {
        if (!response.ok) {
          let errorBody: Partial<{ detail: string; message: string }> = {};
          try {
            errorBody = await response.json();
          } catch {
            // ignore JSON parsing error
          }
          reject(new Error(errorBody.detail || errorBody.message || `登录失败: ${response.status}`));
          return;
        }
        const data = await response.json() as LoginResponse;
        setToken(data.access_token);
        setRefreshToken(data.refresh_token);
        setUser(data.user);
        resolve({ token: data.access_token, user: data.user });
      })
      .catch((error) => {
        reject(new Error(error.message || '网络错误'));
      });
  });
}

export function logout(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

export function getToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null;
}

export function getRefreshToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
}

export function getUser(): User | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    return null;
  }
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  localStorage.setItem('token', token);
}

export function setRefreshToken(token: string): void {
  localStorage.setItem('refresh_token', token);
}

export function setUser(user: User): void {
  localStorage.setItem('user', JSON.stringify(user));
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}

/**
 * Attempt to refresh the access token using the stored refresh token.
 * Returns the new access token on success, or null on failure.
 */
export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) return null;
    const data = await response.json() as { access_token: string };
    setToken(data.access_token);
    return data.access_token;
  } catch {
    return null;
  }
}