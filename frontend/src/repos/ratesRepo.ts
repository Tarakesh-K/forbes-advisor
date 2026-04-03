const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'

export const RATE_ENDPOINTS = {
  LATEST: `${BASE_URL}/rates/latest/`,
  HISTORY: `${BASE_URL}/rates/history/`,
  INGESTION: `${BASE_URL}/rates/ingestion/`,
}