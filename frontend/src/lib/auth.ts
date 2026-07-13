export interface User {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'doctor';
  avatar?: string;
}

interface LoginResponse {
  access_token: string;
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
          let errorBody: Partial<{ message: string }> = {};
          try {
            errorBody = await response.json();
          } catch {
            // ignore JSON parsing error
          }
          reject(new Error(errorBody.message || `登录失败: ${response.status}`));
          return;
        }
        const data = await response.json() as LoginResponse;
        setToken(data.access_token);
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
  localStorage.removeItem('user');
}

export function getToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null;
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

export function setUser(user: User): void {
  localStorage.setItem('user', JSON.stringify(user));
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}