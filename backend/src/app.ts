import 'dotenv/config'
import Fastify from 'fastify'
import cors from '@fastify/cors'
import jwt from '@fastify/jwt'
import swagger from '@fastify/swagger'
import swaggerUI from '@fastify/swagger-ui'
import { fundsRoutes } from './routes/funds'
import { indicatorsRoutes } from './routes/indicators'
import { metadataRoutes } from './routes/metadata'
import { glossaryRoutes } from './routes/glossary'
import { qualityRoutes } from './routes/quality'
import { authRoutes } from './routes/auth'
import { healthRoutes } from './routes/health'

const fastify = Fastify({
  logger: true
})

const start = async () => {
  try {
    // CORS
    await fastify.register(cors, {
      origin: true
    })

    // JWT
    await fastify.register(jwt, {
      secret: process.env.JWT_SECRET || 'fallback-secret-key'
    })

    // Swagger
    await fastify.register(swagger, {
      openapi: {
        info: {
          title: 'FIILens API',
          description: 'Brazilian FII Data Platform API',
          version: '1.0.0'
        },
        servers: [
          {
            url: 'http://localhost:3333',
            description: 'Development server'
          }
        ],
        tags: [
          { name: 'funds', description: 'Fund related endpoints' },
          { name: 'indicators', description: 'Indicator endpoints' },
          { name: 'metadata', description: 'Metadata endpoints' },
          { name: 'quality', description: 'Data quality endpoints' },
          { name: 'glossary', description: 'Business glossary' },
          { name: 'auth', description: 'Authentication' },
          { name: 'health', description: 'Health check' }
        ]
      }
    })

    await fastify.register(swaggerUI, {
      routePrefix: '/docs',
      uiConfig: {
        docExpansion: 'list',
        deepLinking: false
      }
    })

    // Routes
    await fastify.register(healthRoutes, { prefix: '/api/v1' })
    await fastify.register(authRoutes, { prefix: '/api/v1/auth' })
    await fastify.register(fundsRoutes, { prefix: '/api/v1/funds' })
    await fastify.register(indicatorsRoutes, { prefix: '/api/v1/indicators' })
    await fastify.register(metadataRoutes, { prefix: '/api/v1/metadata' })
    await fastify.register(glossaryRoutes, { prefix: '/api/v1/glossary' })
    await fastify.register(qualityRoutes, { prefix: '/api/v1/quality' })

    const port = Number(process.env.PORT) || 3333
    await fastify.listen({ port, host: '0.0.0.0' })
    
    console.log(`🚀 FIILens API running on port ${port}`)
    console.log(`📚 Swagger docs available at http://localhost:${port}/docs`)
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}

start()
