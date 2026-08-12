'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'profil_id'

interface ProfileContextValue {
  profilId: number | null
  setProfilId: (id: number | null) => void
  loaded: boolean
}

const ProfileContext = createContext<ProfileContextValue>({
  profilId: null,
  setProfilId: () => undefined,
  loaded: false,
})

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const [profilId, setProfilIdState] = useState<number | null>(null)
  const [loaded, setLoaded] = useState(false)

  // Read from sessionStorage on client mount only
  useEffect(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = parseInt(stored, 10)
      if (!isNaN(parsed)) {
        setProfilIdState(parsed)
      }
    }
    setLoaded(true)
  }, [])

  const setProfilId = useCallback((id: number | null) => {
    setProfilIdState(id)
    if (id === null) {
      sessionStorage.removeItem(STORAGE_KEY)
    } else {
      sessionStorage.setItem(STORAGE_KEY, String(id))
    }
  }, [])

  return (
    <ProfileContext.Provider value={{ profilId, setProfilId, loaded }}>
      {children}
    </ProfileContext.Provider>
  )
}

export function useProfile() {
  return useContext(ProfileContext)
}
