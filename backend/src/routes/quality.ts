import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function qualityRoutes(fastify: FastifyInstance) {
  fastify.get('/', {
    schema: {
      tags: ['quality']
    }
  }, async (request, reply) => {
    const qualityScores = await prisma.qualityScore.findMany({
      include: {
        fund: true
      },
      orderBy: { measuredAt: 'desc' }
    })

    const avgScores = {
      completeness: 0,
      consistency: 0,
      accuracy: 0,
      uniqueness: 0,
      validity: 0,
      timeliness: 0,
      overall: 0
    }

    qualityScores.forEach(score => {
      avgScores.completeness += score.completeness
      avgScores.consistency += score.consistency
      avgScores.accuracy += score.accuracy
      avgScores.uniqueness += score.uniqueness
      avgScores.validity += score.validity
      avgScores.timeliness += score.timeliness
      avgScores.overall += score.overallScore
    })

    const count = qualityScores.length || 1

    Object.keys(avgScores).forEach(key => {
      avgScores[key as keyof typeof avgScores] = Number((avgScores[key as keyof typeof avgScores] / count).toFixed(2))
    })

    return {
      averages: avgScores,
      scores: qualityScores,
      totalDatasets: count,
      measuredAt: new Date().toISOString()
    }
  })

  fastify.get('/fund/:ticker', {
    schema: {
      tags: ['quality'],
      params: {
        type: 'object',
        properties: {
          ticker: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { ticker } = request.params as any

    const fund = await prisma.fund.findUnique({
      where: { ticker: ticker.toUpperCase() }
    })

    if (!fund) {
      return reply.code(404).send({ error: 'Fund not found' })
    }

    const qualityScores = await prisma.qualityScore.findMany({
      where: { fundId: fund.id },
      orderBy: { measuredAt: 'desc' }
    })

    return qualityScores
  })
}
