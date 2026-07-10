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

  const { data: allFundsForRanking } = useQuery({
    queryKey: ['funds-ranking'],
    queryFn: () => fundsApi.getAll({ limit: 100 })
  })

  // Ordenar por FIILens Score
  const topFIILensScore = allFundsForRanking?.data
    ?.filter((f: any) => f.qualityScore?.overallScore)
    .sort((a: any, b: any) => b.qualityScore.overallScore - a.qualityScore.overallScore)
    .slice(0, 5)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard FIILens</h1>
        <p className="mt-2 text-gray-600">
          Plataforma de dados sobre Fundos de Investimento Imobiliário brasileiros
        </p>
      </div>

      {/* FIILens Score Info Banner */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-2xl">⭐</span>
              <h3 className="text-xl font-bold">FIILens Score - Sistema Inteligente de Análise</h3>
            </div>
            <p className="text-blue-100 text-sm">
              Score de 0-100 baseado em Machine Learning, avaliando 6 componentes fundamentalistas: 
              <span className="font-semibold text-white"> Dividend Yield (25%), P/VP (20%), Liquidez (15%), Consistência de Dividendos (15%), Valorização (15%), Patrimônio (10%)</span>
            </p>
          </div>
          <div className="ml-4 bg-white/20 backdrop-blur-sm rounded-lg px-4 py-3 text-center">
            <p className="text-xs text-blue-100 mb-1">Calculado hoje</p>
            <p className="text-2xl font-bold">{topFIILensScore?.length || 0}</p>
            <p className="text-xs text-blue-100">FIIs analisados</p>
          </div>
        </div>
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
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Buscar FIIs</h2>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <span className="flex items-center">
                  <span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"></span>
                  80+ Excelente
                </span>
                <span className="flex items-center">
                  <span className="inline-block w-3 h-3 rounded-full bg-blue-500 mr-1"></span>
                  70+ Bom
                </span>
                <span className="flex items-center">
                  <span className="inline-block w-3 h-3 rounded-full bg-yellow-500 mr-1"></span>
                  60+ Regular
                </span>
              </div>
            </div>
            
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
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">FIILens Score</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">DY</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">P/VP</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Preço</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {fundsData?.data?.map((fund: any) => {
                      const score = fund.qualityScore?.overallScore || 0
                      const scoreColor = score >= 80 ? 'bg-green-100 text-green-800 border-green-300' 
                        : score >= 70 ? 'bg-blue-100 text-blue-800 border-blue-300'
                        : score >= 60 ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                        : 'bg-gray-100 text-gray-800 border-gray-300'
                      const scoreEmoji = score >= 80 ? '🏆' : score >= 70 ? '⭐' : score >= 60 ? '✓' : '⚠️'
                      
                      return (
                        <tr key={fund.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <Link to={`/fund/${fund.ticker}`} className="text-primary-600 hover:underline font-medium">
                              {fund.ticker}
                            </Link>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">{fund.name}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{fund.segment}</td>
                          <td className="px-4 py-3">
                            {fund.qualityScore ? (
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${scoreColor}`}>
                                <span className="mr-1">{scoreEmoji}</span>
                                {score.toFixed(0)}/100
                              </span>
                            ) : (
                              <span className="text-xs text-gray-400">-</span>
                            )}
                          </td>
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
                      )
                    })}
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

          {/* Top FIILens Score */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6 border-2 border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900">🏆 Top 5 - FIILens Score</h3>
              <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full">Score Inteligente</span>
            </div>
            {topFIILensScore && topFIILensScore.length > 0 ? (
              <div className="space-y-3">
                {topFIILensScore.map((fund: any, index: number) => {
                  const score = fund.qualityScore.overallScore
                  const scoreColor = score >= 80 ? 'bg-green-500' 
                    : score >= 70 ? 'bg-blue-500'
                    : score >= 60 ? 'bg-yellow-500'
                    : 'bg-gray-500'
                  const emoji = score >= 80 ? '🏆' : score >= 70 ? '⭐' : '✓'
                  
                  return (
                    <div key={fund.ticker} className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-gray-100 to-gray-200">
                            <span className="text-sm font-bold text-gray-700">#{index + 1}</span>
                          </div>
                          <div>
                            <Link to={`/fund/${fund.ticker}`} className="text-primary-600 hover:underline font-semibold">
                              {fund.ticker}
                            </Link>
                            <p className="text-xs text-gray-500">{fund.segment}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{emoji}</span>
                          <div className={`px-3 py-1 rounded-full ${scoreColor} text-white font-bold text-sm`}>
                            {score.toFixed(0)}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">Calculando scores...</p>
            )}
            <div className="mt-4 pt-3 border-t border-blue-200">
              <p className="text-xs text-gray-600 text-center">
                Score baseado em DY, P/VP, Liquidez, Consistência e mais
              </p>
            </div>
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
