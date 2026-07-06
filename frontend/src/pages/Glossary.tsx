import { useQuery } from '@tanstack/react-query'
import { glossaryApi } from '../services/api'

export default function Glossary() {
  const { data: glossary, isLoading } = useQuery({
    queryKey: ['glossary'],
    queryFn: glossaryApi.getAll
  })

  const categories = Array.from(new Set(glossary?.map((item: any) => item.category) || []))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Glossário de Negócio</h1>
        <p className="mt-2 text-gray-600">
          Definições padronizadas dos termos financeiros utilizados na plataforma
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="space-y-6">
          {categories.map(category => (
            <div key={category as string} className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 bg-gray-50 border-b">
                <h2 className="text-lg font-semibold text-gray-900">{category as string}</h2>
              </div>
              <div className="p-6 space-y-4">
                {glossary
                  ?.filter((item: any) => item.category === category)
                  .map((item: any) => (
                    <div key={item.id} className="border-l-4 border-primary-500 pl-4">
                      <h3 className="text-lg font-semibold text-gray-900">{item.term}</h3>
                      <p className="mt-2 text-gray-600">{item.businessDefinition}</p>
                      {item.technicalDetails && (
                        <p className="mt-2 text-sm text-gray-500">
                          <span className="font-medium">Detalhes técnicos:</span> {item.technicalDetails}
                        </p>
                      )}
                      {item.example && (
                        <p className="mt-2 text-sm text-primary-600">
                          <span className="font-medium">Exemplo:</span> {item.example}
                        </p>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {glossary?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          Nenhum termo cadastrado ainda
        </div>
      )}
    </div>
  )
}
