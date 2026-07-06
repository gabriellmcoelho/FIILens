import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function healthRoutes(fastify: FastifyInstance) {
  fastify.get('/health', {
    schema: {
      tags: ['health'],
      description: 'Health check endpoint',
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string' },
            database: { type: 'string' },
            timestamp: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    try {
      // Test database connection
      await prisma.$queryRaw`SELECT 1`
      
      return {
        status: 'ok',
        database: 'connected',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return reply.code(503).send({
        status: 'error',
        database: 'disconnected',
        timestamp: new Date().toISOString()
      })
    }
  })
}
