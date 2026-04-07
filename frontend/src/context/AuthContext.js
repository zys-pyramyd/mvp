import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    // Verify token by fetching user profile from server
                    const response = await api.get('/api/user/profile');
                    const serverUser = response.data;
                    setUser(serverUser);
                    localStorage.setItem('user', JSON.stringify(serverUser));
                } catch (error) {
                    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                        // Token is invalid or expired — log out
                        console.warn('Token expired or invalid, logging out');
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                    } else {
                        // Server unreachable — fall back to cached user data
                        const storedUser = localStorage.getItem('user');
                        if (storedUser) {
                            setUser(JSON.parse(storedUser));
                        }
                    }
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
