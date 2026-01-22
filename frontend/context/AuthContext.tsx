'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { setAuthToken } from '@/lib/api'

interface User {
    username: string
}

interface AuthContextType {
    user: User | null
    login: (token: string, username: string) => void
    logout: () => void
    isAuthenticated: boolean
    isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()

    useEffect(() => {
        // Check for token in localStorage on mount
        const token = localStorage.getItem('token')
        const username = localStorage.getItem('username')

        if (token && username) {
            setAuthToken(token)
            setUser({ username })
        }
        setIsLoading(false)
    }, [])

    const login = (token: string, username: string) => {
        localStorage.setItem('token', token)
        localStorage.setItem('username', username)
        setAuthToken(token)
        setUser({ username })
        router.push('/dashboard')
    }

    const logout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        setAuthToken(null)
        setUser(null)
        router.push('/auth/login')
    }

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user, isLoading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
