import { useState, useEffect } from 'react';
import { User, login, logout, getUser, isLoggedIn as checkLoggedIn } from '@/lib/auth';

interface UseAuthReturn {
  user: User | null;
  isLoggedIn: boolean;
  login: (email: string, password: string, role: 'patient' | 'doctor') => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = getUser();
    const loggedIn = checkLoggedIn();
    setUser(storedUser);
    setIsLoggedIn(loggedIn);
    setLoading(false);
  }, []);

  const handleLogin = async (email: string, password: string, role: 'patient' | 'doctor') => {
    setLoading(true);
    try {
      const result = await login(email, password, role);
      setUser(result.user);
      setIsLoggedIn(true);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setIsLoggedIn(false);
  };

  return {
    user,
    isLoggedIn,
    login: handleLogin,
    logout: handleLogout,
    loading,
  };
}