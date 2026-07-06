import { FastifyInstance } from 'fastify'
import { prisma } from '../config/database'

export async function fundsRoutes(fastify: FastifyInstance) {
  // Get all funds
  fastify.get('/', {
    schema: {
      tags: ['funds'],
      querystring: {
        type: 'object',
        properties: {
          search: { type: 'string' },
          segment: { type: 'string' },
          manager: { type: 'string' },
          page: { type: 'number', default: 1 },
          limit: { type: 'number', default: 20 }
        }
      }
    }
  }, async (request, reply) => {
    const { search, segment, manager, page = 1, limit = 20 } = request.query as any

    const where: any = {}

    if (search) {
      where.OR = [
        { ticker: { contains: search, mode: 'insensitive' } },
        { name: { contains: search, mode: 'insensitive' } }
      ]
    }

    if (segment) {
      where.segment = segment
    }

    if (manager) {
      where.manager = { contains: manager, mode: 'insensitive' }
    }

    const skip = (page - 1) * limit

    const [funds, total] = await Promise.all([
      prisma.fund.findMany({
        where,
        skip,
        take: limit,
        include: {
          indicators: {
            orderBy: { lastUpdate: 'desc' },
            take: 1
          }
        }
      }),
      prisma.fund.count({ where })
    ])

    return {
      data: funds.map(fund => ({
        ...fund,
        indicator: fund.indicators[0] || null
      })),
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    }
  })

  // Get fund by ticker
  fastify.get('/:ticker', {
    schema: {
      tags: ['funds'],
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
      where: { ticker: ticker.toUpperCase() },
      include: {
        indicators: {
          orderBy: { lastUpdate: 'desc' },
          take: 1
        },
        metadata: {
          orderBy: { updatedAt: 'desc' },
          take: 1
        },
        qualityScores: {
          orderBy: { measuredAt: 'desc' },
          take: 1
        }
      }
    })

    if (!fund) {
      return reply.code(404).send({ error: 'Fund not found' })
    }

    return {
      ...fund,
      indicator: fund.indicators[0] || null,
      metadata: fund.metadata[0] || null,
      qualityScore: fund.qualityScores[0] || null
    }
  })

  // Get fund historical prices
  fastify.get('/:ticker/history', {
    schema: {
      tags: ['funds'],
      params: {
        type: 'object',
        properties: {
          ticker: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          days: { type: 'number', default: 30 }
        }
      }
    }
  }, async (request, reply) => {
    const { ticker } = request.params as any
    const { days = 30 } = request.query as any

    const fund = await prisma.fund.findUnique({
      where: { ticker: ticker.toUpperCase() }
    })

    if (!fund) {
      return reply.code(404).send({ error: 'Fund not found' })
    }

    const startDate = new Date()
    startDate.setDate(startDate.getDate() - days)

    const prices = await prisma.historicalPrice.findMany({
      where: {
        fundId: fund.id,
        date: {
          gte: startDate
        }
      },
      orderBy: { date: 'asc' }
    })

    return prices
  })

  // Get fund dividends
  fastify.get('/:ticker/dividends', {
    schema: {
      tags: ['funds'],
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

    const dividends = await prisma.dividend.findMany({
      where: { fundId: fund.id },
      orderBy: { paymentDate: 'desc' }
    })

    return dividends
  })

  // Compare funds
  fastify.get('/compare/multiple', {
    schema: {
      tags: ['funds'],
      querystring: {
        type: 'object',
        properties: {
          tickers: { type: 'string' }
        }
      }
    }
  }, async (request, reply) => {
    const { tickers } = request.query as any

    if (!tickers) {
      return reply.code(400).send({ error: 'Tickers parameter is required' })
    }

    const tickerList = tickers.split(',').map((t: string) => t.trim().toUpperCase())

    const funds = await prisma.fund.findMany({
      where: {
        ticker: { in: tickerList }
      },
      include: {
        indicators: {
          orderBy: { lastUpdate: 'desc' },
          take: 1
        }
      }
    })

    return funds.map(fund => ({
      ...fund,
      indicator: fund.indicators[0] || null
    }))
  })
}
