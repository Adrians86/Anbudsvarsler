import type {
  Kunngjoring,
  LeverandorProfil,
  Varsling,
  VarslingStatus,
  Kvalifikasjonssjekk,
  HealthResponse,
  SyncResponse,
  FirmaDokument,
  ReferanseProsjekt,
} from './types'

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${text || res.statusText}`)
  }
  return res.json() as Promise<T>
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health')
}

// ── Kunngjøringer ─────────────────────────────────────────────────────────────

export async function fetchKunngjøringer(params?: {
  cpv?: string
  region?: string
  fra?: string
}): Promise<Kunngjoring[]> {
  const qs = new URLSearchParams()
  if (params?.cpv) qs.set('cpv', params.cpv)
  if (params?.region) qs.set('region', params.region)
  if (params?.fra) qs.set('fra', params.fra)
  const query = qs.toString() ? `?${qs.toString()}` : ''
  return apiFetch<Kunngjoring[]>(`/kunngjoring${query}`)
}

export async function fetchKunngjøring(id: number): Promise<Kunngjoring> {
  return apiFetch<Kunngjoring>(`/kunngjoring/${id}`)
}

// ── Varsler ───────────────────────────────────────────────────────────────────

export async function fetchVarsler(profilId: number): Promise<Varsling[]> {
  return apiFetch<Varsling[]>(`/varsling?profil_id=${profilId}`)
}

export async function updateVarslingStatus(
  varslingId: number,
  status: VarslingStatus
): Promise<Varsling> {
  return apiFetch<Varsling>(
    `/varsling/${varslingId}/status?ny_status=${encodeURIComponent(status)}`,
    { method: 'PUT' }
  )
}

// ── Profil ────────────────────────────────────────────────────────────────────

export async function fetchProfil(profilId: number): Promise<LeverandorProfil> {
  return apiFetch<LeverandorProfil>(`/profil/${profilId}`)
}

export async function fetchProfileList(): Promise<LeverandorProfil[]> {
  return apiFetch<LeverandorProfil[]>('/profil')
}

export async function createProfil(
  data: Partial<LeverandorProfil>
): Promise<LeverandorProfil> {
  return apiFetch<LeverandorProfil>('/profil', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateProfil(
  profilId: number,
  data: Partial<LeverandorProfil>
): Promise<LeverandorProfil> {
  return apiFetch<LeverandorProfil>(`/profil/${profilId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// ── Kvalifikasjon ─────────────────────────────────────────────────────────────

export async function fetchKvalifikasjoner(params: {
  profilId?: number
  varslingId?: number
}): Promise<Kvalifikasjonssjekk[]> {
  const qs = new URLSearchParams()
  if (params.profilId) qs.set('profil_id', String(params.profilId))
  if (params.varslingId) qs.set('varsling_id', String(params.varslingId))
  return apiFetch<Kvalifikasjonssjekk[]>(`/kvalifikasjon?${qs.toString()}`)
}

export async function runKvalifikasjon(
  varslingId: number,
  profilId: number
): Promise<Kvalifikasjonssjekk> {
  return apiFetch<Kvalifikasjonssjekk>('/kvalifikasjon', {
    method: 'POST',
    body: JSON.stringify({ varsling_id: varslingId, profil_id: profilId }),
  })
}

// ── Dokumenter ────────────────────────────────────────────────────────────────

export async function fetchDokumenter(profilId: number): Promise<FirmaDokument[]> {
  return apiFetch<FirmaDokument[]>(`/dokument/${profilId}`)
}

// ── Dokumenter (write) ────────────────────────────────────────────────────────

export async function createDokument(
  data: Partial<FirmaDokument>
): Promise<FirmaDokument> {
  return apiFetch<FirmaDokument>('/dokument', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateDokument(
  dokId: number,
  data: Partial<FirmaDokument>
): Promise<FirmaDokument> {
  return apiFetch<FirmaDokument>(`/dokument/${dokId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteDokument(dokId: number): Promise<void> {
  await apiFetch<unknown>(`/dokument/${dokId}`, { method: 'DELETE' })
}

// ── Referanser ────────────────────────────────────────────────────────────────

export async function fetchReferanser(profilId: number): Promise<ReferanseProsjekt[]> {
  return apiFetch<ReferanseProsjekt[]>(`/referanse/${profilId}`)
}

export async function createReferanse(
  data: Partial<ReferanseProsjekt>
): Promise<ReferanseProsjekt> {
  return apiFetch<ReferanseProsjekt>('/referanse', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteReferanse(refId: number): Promise<void> {
  await apiFetch<unknown>(`/referanse/${refId}`, { method: 'DELETE' })
}

// ── Admin / Sync ──────────────────────────────────────────────────────────────

export async function triggerSync(): Promise<SyncResponse> {
  return apiFetch<SyncResponse>('/admin/sync', { method: 'POST' })
}
