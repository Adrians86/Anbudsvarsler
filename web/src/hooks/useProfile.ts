'use client'

import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'profil_id'

export function useProfile() {
  const [profilId, setProfilIdState] = useState<number | null>(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = parseInt(stored, 10)
        if (!isNaN(parsed)) {
          setProfilIdState(parsed)
        }
      }
      setLoaded(true)
    }
  }, [])

  const setProfilId = useCallback((id: number | null) => {
    setProfilIdState(id)
    if (typeof window !== 'undefined') {
      if (id === null) {
        localStorage.removeItem(STORAGE_KEY)
      } else {
        localStorage.setItem(STORAGE_KEY, String(id))
      }
    }
  }, [])

  return { profilId, setProfilId, loaded }
}
