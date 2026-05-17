import React, {createContext, useContext, useState, useEffect, ReactNode} from 'react';

/** In-memory only (no native persistence) — avoids AsyncStorage native build on Android. */
let persistedUserJson: string | null = null;

interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  walletBalance: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (name: string, email: string, phone: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  updateWalletBalance: (amount: number) => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({children}: {children: ReactNode}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserFromStorage();
  }, []);

  const loadUserFromStorage = async () => {
    try {
      const userData = persistedUserJson;
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      if (email && password.length >= 6) {
        const mockUser: User = {
          id: '1',
          name: 'Metro User',
          email: email,
          phone: '+92-300-1234567',
          walletBalance: 500,
        };
        
        persistedUserJson = JSON.stringify(mockUser);
        setUser(mockUser);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const signup = async (
    name: string,
    email: string,
    phone: string,
    password: string,
  ): Promise<boolean> => {
    try {
      if (name && email && phone && password.length >= 6) {
        const newUser: User = {
          id: Date.now().toString(),
          name,
          email,
          phone,
          walletBalance: 0,
        };
        
        persistedUserJson = JSON.stringify(newUser);
        setUser(newUser);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Signup error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      persistedUserJson = null;
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const updateWalletBalance = (amount: number) => {
    if (user) {
      const updatedUser = {...user, walletBalance: user.walletBalance + amount};
      setUser(updatedUser);
      persistedUserJson = JSON.stringify(updatedUser);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        login,
        signup,
        logout,
        updateWalletBalance,
        loading,
      }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
