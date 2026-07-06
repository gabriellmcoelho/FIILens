import { useQuery } from '@tanstack/react-query'
import { metadataApi } from '../services/api'

export default function Metadata() {
  const { data: metadata, isLoading } = useQuery({
    queryKey: ['metadata'],
    queryFn: metadataApi.getAll
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Catálogo de Metadados</h1>
        <p className="mt-2 text-gray-600">
          Documentação empresarial dos ativos de dados da plataforma
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {metadata?.map((item: any) => (
            <div key={item.id} className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900">{item.entityName}</h3>
                  <p className="mt-2 text-gray-600">{item.businessDescription}</p>
                  
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Data Owner</p>
                      <p className="font-medium">{item.dataOwner}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Data Steward</p>
                      <p className="font-medium">{item.dataSteward}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Fonte</p>
                      <p className="font-medium">{item.source}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Frequência de Atualização</p>
                      <p className="font-medium">{item.refreshFrequency}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Classificação</p>
                      <p className="font-medium">{item.classification}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Sensibilidade</p>
                      <p className="font-medium">{item.sensitivity}</p>
                    </div>
                  </div>
                </div>
                <span className="ml-4 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                  v{item.version}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {metadata?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Nenhum metadado cadastrado ainda
        </div>
      )}
    </div>
  )
}
