import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fundsApi } from '../services/api'

export default function Compare() {
  const [selectedTickers, setSelectedTickers] = useState<string[]>([])
  const [searchTicker, setSearchTicker] = useState('')

  const { data: searchResults } = useQuery({
    queryKey: ['funds-search', searchTicker],
    queryFn: () => fundsApi.getAll({ search: searchTicker, limit: 5 }),
    enabled: searchTicker.length > 0
  })

  const { data: compareData } = useQuery({
    queryKey: ['compare', selectedTickers],
    queryFn: () => fundsApi.compare(selectedTickers),
    enabled: selectedTickers.length > 0
  })

  const addTicker = (ticker: string) => {
    if (!selectedTickers.includes(ticker) && selectedTickers.length < 5) {
      setSelectedTickers([...selectedTickers, ticker])
      setSearchTicker('')
    }
  }

  const removeTicker = (ticker: string) => {
    setSelectedTickers(selectedTickers.filter(t => t !== ticker))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Comparar FIIs</h1>
        <p className="mt-2 text-gray-600">Compare até 5 fundos lado a lado</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Selecionar FIIs</h2>
        
        <div className="relative">
          <input
            type="text"
            placeholder="Digite o ticker do FII..."
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
          />
          
          {searchResults?.data && searchTicker && (
            <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg">
              {searchResults.data.map((fund: any) => (
                <button
                  key={fund.ticker}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 border-b last:border-b-0"
                  onClick={() => addTicker(fund.ticker)}
                >
                  <span className="font-medium">{fund.ticker}</span>
                  <span className="text-gray-600 ml-2">- {fund.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {selectedTickers.map(ticker => (
            <span
              key={ticker}
              className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-800 rounded-full"
            >
              {ticker}
              <button
                onClick={() => removeTicker(ticker)}
                className="ml-2 text-primary-600 hover:text-primary-900"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {compareData && compareData.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Indicador
                </th>
                {compareData.map((fund: any) => (
                  <th key={fund.ticker} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    {fund.ticker}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Nome</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    {fund.name}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Segmento</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    {fund.segment}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Preço</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    R$ {fund.indicator?.price?.toFixed(2) || '-'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Dividend Yield</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-green-600 font-semibold">
                    {fund.indicator?.dividendYield?.toFixed(2) || '-'}%
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">P/VP</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    {fund.indicator?.pvp?.toFixed(2) || '-'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Liquidez</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    {fund.indicator?.liquidity?.toFixed(0) || '-'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium text-gray-900">Gestor</td>
                {compareData.map((fund: any) => (
                  <td key={fund.ticker} className="px-6 py-4 text-sm text-gray-900">
                    {fund.manager}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {selectedTickers.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Selecione FIIs para comparar
        </div>
      )}
    </div>
  )
}
