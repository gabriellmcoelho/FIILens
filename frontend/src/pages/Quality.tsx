import { useQuery } from '@tanstack/react-query'
import { qualityApi } from '../services/api'

export default function Quality() {
  const { data: qualityData, isLoading } = useQuery({
    queryKey: ['quality'],
    queryFn: qualityApi.getAll
  })

  const dimensions = [
    { key: 'completeness', label: 'Completude' },
    { key: 'consistency', label: 'Consistência' },
    { key: 'accuracy', label: 'Precisão' },
    { key: 'uniqueness', label: 'Unicidade' },
    { key: 'validity', label: 'Validade' },
    { key: 'timeliness', label: 'Tempestividade' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Qualidade de Dados</h1>
        <p className="mt-2 text-gray-600">
          Métricas de qualidade dos datasets da plataforma
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <>
          {qualityData?.averages && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-6">Médias Gerais de Qualidade</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                {dimensions.map(dim => (
                  <div key={dim.key} className="text-center">
                    <p className="text-sm text-gray-600 mb-2">{dim.label}</p>
                    <div className="relative pt-1">
                      <div className="flex mb-2 items-center justify-between">
                        <div className="text-3xl font-bold text-primary-600">
                          {qualityData.averages[dim.key]?.toFixed(1) || 0}%
                        </div>
                      </div>
                      <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                        <div
                          style={{ width: `${qualityData.averages[dim.key] || 0}%` }}
                          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-8 text-center">
                <p className="text-sm text-gray-600">Score Geral</p>
                <p className="text-5xl font-bold text-green-600 mt-2">
                  {qualityData.averages.overall?.toFixed(1)}%
                </p>
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b">
              <h2 className="text-xl font-semibold">Scores por Dataset</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      FII
                    </th>
                    {dimensions.map(dim => (
                      <th key={dim.key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {dim.label}
                      </th>
                    ))}
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Score Geral
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {qualityData?.scores?.map((score: any) => (
                    <tr key={score.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {score.fund?.ticker || 'N/A'}
                      </td>
                      {dimensions.map(dim => (
                        <td key={dim.key} className="px-6 py-4 text-sm text-gray-900">
                          {score[dim.key]?.toFixed(1)}%
                        </td>
                      ))}
                      <td className="px-6 py-4 text-sm font-semibold text-primary-600">
                        {score.overallScore?.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {qualityData?.scores?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Nenhum score de qualidade disponível
        </div>
      )}
    </div>
  )
}
