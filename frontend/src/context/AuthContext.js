import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'

    useEffect(() => {
        // Check for token on initial load
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    // Verify token and get user profile
                    // Since we don't know the exact endpoint for "get current user",
                    // we'll assume there is one or imply it from successful requests.
                    // However, standard practice is GET /api/auth/me or similar.
                    // If not available, we might just trust the token (less secure) or assume the user is logged in
                    // if we have data.
                    // App.js used to set user from login response.
                    // It didn't seem to fetch user on load (based on my search failure).
                    // I will implement a check if possible, or just look for 'user' in localStorage if it was stored?
                    // Existing App.js didn't show 'user' in localStorage.

                    // Let's try to hit a protected endpoint or just proceed.
                    // For now, I'll rely on a valid token. 
                    // If possible, I'll decode the JWT to get user info if it's there?
                    // Or I'll set a placeholder user or fetch profile.

                    // Let's assume we can fetch profile. 
                    // const response = await api.get('/api/users/profile'); // Hypothetical
                    // setUser(response.data);

                    // Since I can't confirm the endpoint, I will leave it empty for now 
                    // and let the existing components handle scenarios where 'user' might be populated later.
                    // actually, without 'user', the UI shows 'Sign In'.
                    // So we NEED to restore 'user'.

                    // Let's look at `App.js` `handleAuth`. It sets `setUser(data.user)`.
                    // We should store `user` in localStorage too to persist it easily if there's no endpoint.
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        setUser(JSON.parse(storedUser));
                    }
                } catch (error) {
                    console.error('Auth verification failed', error);
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);

    const login = async (credentials) => {
        try {
            const response = await api.post('/api/auth/login', credentials);
            const { user, token } = response.data;

            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            setUser(user);
            setShowAuthModal(false);
            return { success: true };
        } catch (error) {
            console.error('Login failed', error);
            return {
                success: false,
                message: error.response?.data?.message || 'Login failed'
            };
        }
    };

    const register = async (endpoint, data) => {
        try {
            // Endpoint is passed because existing code uses different endpoints?
            // App.js used `/api/auth/complete-registration`
            const response = await api.post(endpoint, data);
            const { user, token } = response.data;

            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(user));
            setUser(user);
            setShowAuthModal(false);
            return { success: true };
        } catch (error) {
            console.error('Registration failed', error);
            return {
                success: false,
                message: error.response?.data?.message || 'Registration failed'
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setShowAuthModal(false);
    };

    const updateUser = (userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    };

    return (
        <AuthContext.Provider value={{
            user,
            updateUser,
            loading,
            login,
            register,
            logout,
            showAuthModal,
            setShowAuthModal,
            authMode,
            setAuthMode
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
