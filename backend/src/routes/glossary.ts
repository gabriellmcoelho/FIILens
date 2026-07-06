import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function glossaryRoutes(fastify: FastifyInstance) {
  fastify.get('/', {
    schema: {
      tags: ['glossary']
    }
  }, async (request, reply) => {
    const glossary = await prisma.glossary.findMany({
      orderBy: { term: 'asc' }
    })

    return glossary
  })

  fastify.get('/:term', {
    schema: {
      tags: ['glossary'],
      params: {
        type: 'object',
        properties: {
          term: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { term } = request.params as any

    const glossaryItem = await prisma.glossary.findUnique({
      where: { term }
    })

    if (!glossaryItem) {
      return reply.code(404).send({ error: 'Term not found' })
    }

    return glossaryItem
  })
}
