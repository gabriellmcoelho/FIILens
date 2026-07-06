import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function metadataRoutes(fastify: FastifyInstance) {
  fastify.get('/', {
    schema: {
      tags: ['metadata']
    }
  }, async (request, reply) => {
    const metadata = await prisma.metadata.findMany({
      include: {
        fund: true
      },
      orderBy: { updatedAt: 'desc' }
    })

    return metadata
  })

  fastify.get('/:id', {
    schema: {
      tags: ['metadata'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { id } = request.params as any

    const metadata = await prisma.metadata.findUnique({
      where: { id },
      include: { fund: true }
    })

    if (!metadata) {
      return reply.code(404).send({ error: 'Metadata not found' })
    }

    return metadata
  })
}
