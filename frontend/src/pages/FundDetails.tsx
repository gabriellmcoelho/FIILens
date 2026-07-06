import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fundsApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function FundDetails() {
  const { ticker } = useParams<{ ticker: string }>()

  const { data: fund, isLoading } = useQuery({
    queryKey: ['fund', ticker],
    queryFn: () => fundsApi.getByTicker(ticker!),
    enabled: !!ticker
  })

  const { data: history } = useQuery({
    queryKey: ['history', ticker],
    queryFn: () => fundsApi.getHistory(ticker!, 90),
    enabled: !!ticker
  })

  const { data: dividends } = useQuery({
    queryKey: ['dividends', ticker],
    queryFn: () => fundsApi.getDividends(ticker!),
    enabled: !!ticker
  })

  if (isLoading) {
    return <div className="text-center py-12">Carregando...</div>
  }

  if (!fund) {
    return <div className="text-center py-12">FII não encontrado</div>
  }

  const chartData = history?.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString('pt-BR'),
    price: item.price
  })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-4">
            <h1 className="text-3xl font-bold text-gray-900">{fund.ticker}</h1>
            <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
              {fund.segment}
            </span>
          </div>
          <p className="mt-2 text-gray-600">{fund.name}</p>
        </div>
        <Link
          to="/"
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          ← Voltar
        </Link>
      </div>

      {/* Key Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Preço</p>
          <p className="text-2xl font-bold text-gray-900">
            R$ {fund.indicator?.price?.toFixed(2) || '-'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Dividend Yield</p>
          <p className="text-2xl font-bold text-green-600">
            {fund.indicator?.dividendYield?.toFixed(2) || '-'}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">P/VP</p>
          <p className="text-2xl font-bold text-gray-900">
            {fund.indicator?.pvp?.toFixed(2) || '-'}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Liquidez</p>
          <p className="text-2xl font-bold text-gray-900">
            {fund.indicator?.liquidity?.toFixed(0) || '-'}
          </p>
        </div>
      </div>

      {/* Historical Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Histórico de Preços (90 dias)</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center text-gray-500 py-8">Nenhum dado histórico disponível</p>
        )}
      </div>

      {/* Fund Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Informações</h2>
          <dl className="space-y-2">
            <div className="flex justify-between">
              <dt className="text-gray-600">Gestor:</dt>
              <dd className="font-medium">{fund.manager}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Administrador:</dt>
              <dd className="font-medium">{fund.administrator}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">CNPJ:</dt>
              <dd className="font-medium">{fund.cnpj}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Segmento:</dt>
              <dd className="font-medium">{fund.segment}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Últimos Dividendos</h2>
          {dividends && dividends.length > 0 ? (
            <div className="space-y-2">
              {dividends.slice(0, 5).map((div: any) => (
                <div key={div.id} className="flex justify-between border-b pb-2">
                  <span className="text-gray-600">
                    {new Date(div.paymentDate).toLocaleDateString('pt-BR')}
                  </span>
                  <span className="font-semibold text-green-600">
                    R$ {div.value.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Nenhum dividendo registrado</p>
          )}
        </div>
      </div>

      {/* Quality Score */}
      {fund.qualityScore && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Score de Qualidade de Dados</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Completude</p>
              <p className="text-xl font-bold">{fund.qualityScore.completeness.toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Consistência</p>
              <p className="text-xl font-bold">{fund.qualityScore.consistency.toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Precisão</p>
              <p className="text-xl font-bold">{fund.qualityScore.accuracy.toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Score Geral</p>
              <p className="text-xl font-bold text-primary-600">
                {fund.qualityScore.overallScore.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
