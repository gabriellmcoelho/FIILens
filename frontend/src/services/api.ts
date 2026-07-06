import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const api = axios.create({
  baseURL: API_BASE_URL
})

export interface Fund {
  id: string
  ticker: string
  name: string
  cnpj: string
  segment: string
  manager: string
  administrator: string
  indicator?: Indicator | null
}

export interface Indicator {
  id: string
  dividendYield?: number
  pvp?: number
  liquidity?: number
  marketCap?: number
  netAssetValue?: number
  vacancy?: number
  price?: number
  volume?: number
  lastUpdate: string
}

export interface HistoricalPrice {
  id: string
  date: string
  price: number
  volume?: number
}

export interface Dividend {
  id: string
  paymentDate: string
  exDate: string
  value: number
}

export interface QualityScore {
  id: string
  completeness: number
  consistency: number
  accuracy: number
  uniqueness: number
  validity: number
  timeliness: number
  overallScore: number
  measuredAt: string
}

export interface Glossary {
  id: string
  term: string
  businessDefinition: string
  technicalDetails?: string
  example?: string
  category: string
}

export const fundsApi = {
  getAll: async (params?: {
    search?: string
    segment?: string
    manager?: string
    page?: number
    limit?: number
  }) => {
    const { data } = await api.get('/funds', { params })
    return data
  },

  getByTicker: async (ticker: string) => {
    const { data } = await api.get(`/funds/${ticker}`)
    return data
  },

  getHistory: async (ticker: string, days: number = 30) => {
    const { data } = await api.get(`/funds/${ticker}/history`, {
      params: { days }
    })
    return data
  },

  getDividends: async (ticker: string) => {
    const { data } = await api.get(`/funds/${ticker}/dividends`)
    return data
  },

  compare: async (tickers: string[]) => {
    const { data } = await api.get('/funds/compare/multiple', {
      params: { tickers: tickers.join(',') }
    })
    return data
  }
}

export const indicatorsApi = {
  getRankings: async (type: string, order: 'asc' | 'desc' = 'desc', limit: number = 10) => {
    const { data } = await api.get('/indicators/rankings', {
      params: { type, order, limit }
    })
    return data
  },

  getOverview: async () => {
    const { data } = await api.get('/indicators/overview')
    return data
  }
}

export const metadataApi = {
  getAll: async () => {
    const { data } = await api.get('/metadata')
    return data
  }
}

export const glossaryApi = {
  getAll: async () => {
    const { data } = await api.get('/glossary')
    return data
  }
}

export const qualityApi = {
  getAll: async () => {
    const { data } = await api.get('/quality')
    return data
  },

  getByTicker: async (ticker: string) => {
    const { data } = await api.get(`/quality/fund/${ticker}`)
    return data
  }
}

export default api
