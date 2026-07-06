import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify'
import { exec } from 'child_process'
import { promisify } from 'util'
import { prisma } from '../config/database'

const execAsync = promisify(exec)

export async function dataRoutes(fastify: FastifyInstance) {
  // Update data from real-time sources
  fastify.post('/update', {
    schema: {
      tags: ['data'],
      summary: 'Update FII data from real-time sources',
      description: 'Triggers the analytics engine to fetch fresh data from APIs',
      response: {
        200: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            message: { type: 'string' },
            timestamp: { type: 'string' }
          }
        },
        500: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            error: { type: 'string' }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      fastify.log.info('Triggering data update...')
      
      // Run Python analytics engine in update mode
      const { stdout, stderr } = await execAsync(
        'cd analytics && /usr/bin/python3 main.py --mode update',
        { timeout: 60000 } // 60 second timeout
      )
      
      if (stderr && !stderr.includes('INFO')) {
        fastify.log.error(`Update stderr: ${stderr}`)
      }
      
      fastify.log.info(`Update completed: ${stdout}`)
      
      return reply.send({
        success: true,
        message: 'Data updated successfully',
        timestamp: new Date().toISOString()
      })
    } catch (error: any) {
      fastify.log.error(`Data update failed: ${error.message}`)
      
      return reply.status(500).send({
        success: false,
        error: error.message
      })
    }
  })
  
  // Get last update timestamp
  fastify.get('/last-update', {
    schema: {
      tags: ['data'],
      summary: 'Get last data update timestamp',
      description: 'Returns when the data was last updated',
      response: {
        200: {
          type: 'object',
          properties: {
            lastUpdate: { type: 'string' },
            nextUpdate: { type: 'string' }
          }
        }
      }
    }
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      // Query the most recent update from indicators table
      const result = await prisma.indicator.findFirst({
        orderBy: { lastUpdate: 'desc' },
        select: { lastUpdate: true }
      })
      
      const lastUpdate = result?.lastUpdate || null
      const nextUpdate = lastUpdate 
        ? new Date(lastUpdate.getTime() + 15 * 60 * 1000) // 15 minutes from last update
        : new Date()
      
      return reply.send({
        lastUpdate: lastUpdate?.toISOString() || null,
        nextUpdate: nextUpdate.toISOString()
      })
    } catch (error: any) {
      fastify.log.error(`Failed to get last update: ${error.message}`)
      
      return reply.status(500).send({
        error: 'Failed to retrieve update information'
      })
    }
  })
}
