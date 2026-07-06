import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function indicatorsRoutes(fastify: FastifyInstance) {
  // Get rankings
  fastify.get('/rankings', {
    schema: {
      tags: ['indicators'],
      querystring: {
        type: 'object',
        properties: {
          type: { 
            type: 'string',
            enum: ['dividendYield', 'pvp', 'liquidity', 'marketCap', 'vacancy']
          },
          order: { type: 'string', enum: ['asc', 'desc'], default: 'desc' },
          limit: { type: 'number', default: 10 }
        }
      }
    }
  }, async (request, reply) => {
    const { type = 'dividendYield', order = 'desc', limit = 10 } = request.query as any

    const orderByField: any = {}
    orderByField[type] = order

    const indicators = await prisma.indicator.findMany({
      where: {
        [type]: { not: null }
      },
      include: {
        fund: true
      },
      orderBy: orderByField,
      take: limit
    })

    return indicators.map(ind => ({
      ticker: ind.fund.ticker,
      name: ind.fund.name,
      segment: ind.fund.segment,
      value: (ind as any)[type],
      indicator: ind
    }))
  })

  // Get market overview
  fastify.get('/overview', {
    schema: {
      tags: ['indicators']
    }
  }, async (request, reply) => {
    const indicators = await prisma.indicator.findMany({
      include: {
        fund: true
      }
    })

    const totalFunds = indicators.length
    const avgDividendYield = indicators.reduce((sum, ind) => sum + (ind.dividendYield || 0), 0) / totalFunds
    const avgPVP = indicators.reduce((sum, ind) => sum + (ind.pvp || 0), 0) / totalFunds
    const totalMarketCap = indicators.reduce((sum, ind) => sum + (ind.marketCap || 0), 0)

    return {
      totalFunds,
      avgDividendYield: avgDividendYield.toFixed(2),
      avgPVP: avgPVP.toFixed(2),
      totalMarketCap: totalMarketCap.toFixed(2),
      lastUpdate: new Date().toISOString()
    }
  })
}
