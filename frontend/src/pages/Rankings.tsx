import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { indicatorsApi } from '../services/api'

const rankingTypes = [
  { value: 'dividendYield', label: 'Maior Dividend Yield' },
  { value: 'pvp', label: 'Menor P/VP' },
  { value: 'liquidity', label: 'Maior Liquidez' },
  { value: 'marketCap', label: 'Maior Market Cap' },
  { value: 'vacancy', label: 'Menor Vacância' }
]

export default function Rankings() {
  const [selectedType, setSelectedType] = useState('dividendYield')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')

  const { data: ranking, isLoading } = useQuery({
    queryKey: ['rankings', selectedType, order],
    queryFn: () => indicatorsApi.getRankings(selectedType, order, 20)
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Rankings</h1>
        <p className="mt-2 text-gray-600">Classificações dos fundos por indicadores</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex flex-col sm:flex-row gap-4">
          <select
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            {rankingTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>

          <select
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            value={order}
            onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}
          >
            <option value="desc">Decrescente</option>
            <option value="asc">Crescente</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Posição
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Ticker
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Segmento
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Valor
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ranking?.map((item: any, index: number) => (
                  <tr key={item.ticker} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/fund/${item.ticker}`}
                        className="text-primary-600 hover:underline font-medium"
                      >
                        {item.ticker}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{item.segment}</td>
                    <td className="px-6 py-4">
                      <span className="text-lg font-semibold text-green-600">
                        {selectedType === 'dividendYield' && `${item.value?.toFixed(2)}%`}
                        {selectedType === 'pvp' && item.value?.toFixed(2)}
                        {selectedType === 'liquidity' && item.value?.toFixed(0)}
                        {selectedType === 'marketCap' && `R$ ${(item.value / 1000000).toFixed(1)}M`}
                        {selectedType === 'vacancy' && `${item.value?.toFixed(2)}%`}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
