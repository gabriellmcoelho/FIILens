import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fundsApi, indicatorsApi } from '../services/api'
import { useState } from 'react'

export default function Dashboard() {
  const [search, setSearch] = useState('')
  const [segment, setSegment] = useState('')

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['overview'],
    queryFn: indicatorsApi.getOverview
  })

  const { data: fundsData, isLoading: fundsLoading } = useQuery({
    queryKey: ['funds', search, segment],
    queryFn: () => fundsApi.getAll({ search, segment, limit: 10 })
  })

  const { data: topDividendYield } = useQuery({
    queryKey: ['rankings', 'dividendYield'],
    queryFn: () => indicatorsApi.getRankings('dividendYield', 'desc', 5)
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard FIILens</h1>
        <p className="mt-2 text-gray-600">
          Plataforma de dados sobre Fundos de Investimento Imobiliário brasileiros
        </p>
      </div>

      {/* Overview Cards */}
      {!overviewLoading && overview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-600">Total de FIIs</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{overview.totalFunds}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-600">Dividend Yield Médio</p>
            <p className="text-3xl font-bold text-primary-600 mt-2">{overview.avgDividendYield}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-600">P/VP Médio</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{overview.avgPVP}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm text-gray-600">Market Cap Total</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              R$ {(parseFloat(overview.totalMarketCap) / 1000000).toFixed(0)}M
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Buscar FIIs</h2>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Buscar por ticker ou nome..."
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />

              <select
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                value={segment}
                onChange={(e) => setSegment(e.target.value)}
              >
                <option value="">Todos os segmentos</option>
                <option value="Logística">Logística</option>
                <option value="Lajes Corporativas">Lajes Corporativas</option>
                <option value="Shopping">Shopping</option>
                <option value="Híbrido">Híbrido</option>
                <option value="Tijolo">Tijolo</option>
                <option value="Papel">Papel</option>
              </select>
            </div>

            {fundsLoading ? (
              <div className="text-center py-8">Carregando...</div>
            ) : (
              <div className="mt-6 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticker</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Segmento</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">DY</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">P/VP</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Preço</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {fundsData?.data?.map((fund: any) => (
                      <tr key={fund.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <Link to={`/fund/${fund.ticker}`} className="text-primary-600 hover:underline font-medium">
                            {fund.ticker}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{fund.name}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{fund.segment}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {fund.indicator?.dividendYield?.toFixed(2)}%
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {fund.indicator?.pvp?.toFixed(2)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          R$ {fund.indicator?.price?.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Top 5 - Dividend Yield</h3>
            {topDividendYield && (
              <div className="space-y-3">
                {topDividendYield.map((item: any, index: number) => (
                  <div key={item.ticker} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                      <Link to={`/fund/${item.ticker}`} className="text-primary-600 hover:underline">
                        {item.ticker}
                      </Link>
                    </div>
                    <span className="font-semibold text-green-600">{item.value?.toFixed(2)}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-primary-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-primary-900 mb-2">Sobre FIILens</h3>
            <p className="text-sm text-primary-800">
              Plataforma de dados sobre FIIs construída com princípios DAMA-DMBOK, 
              focada em governança de dados, qualidade e metadata management.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
