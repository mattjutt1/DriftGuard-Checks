/**
 * Security Module for DriftGuard
 * Implements comprehensive security measures including:
 * - Webhook signature validation
 * - Rate limiting
 * - Error sanitization
 * - Security headers
 * - Input validation
 */

import crypto from 'crypto';
import rateLimit from 'express-rate-limit';
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';

/**
 * Verify GitHub webhook signature using HMAC-SHA256
 * Implements timing-safe comparison to prevent timing attacks
 */
export function verifyWebhookSignature(
  payload: string,
  signature: string | undefined,
  secret: string
): boolean {
  if (!signature || !secret) {
    console.error('Missing signature or secret for webhook validation');
    return false;
  }
  
  // GitHub sends the signature in the format: sha256=<signature>
  const expectedSignature = `sha256=${crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex')}`;
  
  try {
    // Use timing-safe comparison to prevent timing attacks
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch (error) {
    console.error('Error validating webhook signature:', error);
    return false;
  }
}

/**
 * Express middleware for webhook signature validation
 */
export function webhookSignatureMiddleware(secret: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    const signature = req.headers['x-hub-signature-256'] as string;
    const payload = JSON.stringify(req.body);
    
    if (!verifyWebhookSignature(payload, signature, secret)) {
      console.error('Invalid webhook signature attempted', {
        ip: req.ip,
        timestamp: new Date().toISOString(),
        userAgent: req.headers['user-agent']
      });
      return res.status(401).json({ 
        error: 'Unauthorized',
        message: 'Invalid webhook signature' 
      });
    }
    
    next();
  };
}

/**
 * Rate limiting configurations for different endpoints
 */
export const rateLimiters = {
  // Webhook endpoint rate limiter
  webhook: rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000'), // 1 minute
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'), // 100 requests per minute
    message: 'Too many webhook requests, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
      console.warn('Webhook rate limit exceeded', {
        ip: req.ip,
        timestamp: new Date().toISOString(),
        endpoint: req.path
      });
      res.status(429).json({ 
        error: 'Rate limit exceeded',
        retryAfter: res.getHeader('Retry-After')
      });
    }
  }),
  
  // Health check endpoint rate limiter (more permissive)
  health: rateLimit({
    windowMs: 60000, // 1 minute
    max: 300, // 300 requests per minute
    message: 'Too many health check requests'
  }),
  
  // General API rate limiter
  api: rateLimit({
    windowMs: 60000, // 1 minute
    max: 200, // 200 requests per minute
    message: 'Too many API requests'
  })
};

/**
 * Sanitize error messages for external responses
 * Prevents information disclosure through error messages
 */
export function sanitizeError(error: any): { message: string; code?: string } {
  // Log full error internally for debugging
  console.error('Internal error:', {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
  
  // In production, return generic messages
  if (process.env.NODE_ENV === 'production') {
    // Map known error types to safe messages
    const errorMap: Record<string, string> = {
      'ValidationError': 'Invalid request data',
      'UnauthorizedError': 'Authentication required',
      'ForbiddenError': 'Access denied',
      'NotFoundError': 'Resource not found',
      'RateLimitError': 'Too many requests'
    };
    
    const errorType = error.constructor?.name || 'Error';
    return {
      message: errorMap[errorType] || 'An error occurred processing your request',
      code: error.code
    };
  }
  
  // In development, return more details (but still sanitized)
  return {
    message: error.message || 'An error occurred',
    code: error.code
  };
}

/**
 * Security headers middleware
 * Implements OWASP recommended security headers
 */
export function securityHeaders() {
  return (req: Request, res: Response, next: NextFunction) => {
    // Prevent MIME type sniffing
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // Prevent clickjacking
    res.setHeader('X-Frame-Options', 'DENY');
    
    // Enable XSS protection
    res.setHeader('X-XSS-Protection', '1; mode=block');
    
    // Force HTTPS
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
    
    // Prevent information leakage through referrer
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    
    // Content Security Policy
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");
    
    // Remove powered by header
    res.removeHeader('X-Powered-By');
    
    next();
  };
}

/**
 * Input validation schemas using Zod
 */
export const validationSchemas = {
  // GitHub webhook payload validation
  webhookPayload: z.object({
    action: z.string(),
    workflow_run: z.object({
      id: z.number(),
      name: z.string().optional(),
      head_sha: z.string().regex(/^[a-f0-9]{40}$/),
      head_branch: z.string().optional(),
      status: z.string().optional(),
      conclusion: z.string().nullable().optional(),
      workflow_id: z.number(),
      repository: z.object({
        id: z.number(),
        name: z.string(),
        full_name: z.string(),
        owner: z.object({
          login: z.string(),
          id: z.number()
        })
      })
    }).optional(),
    repository: z.object({
      id: z.number(),
      name: z.string(),
      full_name: z.string()
    }),
    sender: z.object({
      login: z.string(),
      id: z.number()
    })
  }).passthrough(), // Allow additional fields
  
  // Environment variable validation
  envConfig: z.object({
    GITHUB_APP_ID: z.string().regex(/^\d+$/),
    GITHUB_CLIENT_ID: z.string().min(1),
    GITHUB_CLIENT_SECRET: z.string().min(20),
    WEBHOOK_SECRET: z.string().min(32),
    PRIVATE_KEY_PATH: z.string().optional(),
    NODE_ENV: z.enum(['development', 'production', 'test']).default('production'),
    PORT: z.string().regex(/^\d+$/).default('3000'),
    RATE_LIMIT_WINDOW_MS: z.string().regex(/^\d+$/).default('60000'),
    RATE_LIMIT_MAX_REQUESTS: z.string().regex(/^\d+$/).default('100'),
    LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('error')
  })
};

/**
 * Validate webhook payload
 */
export function validateWebhookPayload(payload: unknown) {
  try {
    return validationSchemas.webhookPayload.parse(payload);
  } catch (error) {
    console.error('Webhook payload validation failed:', error);
    throw new Error('Invalid webhook payload');
  }
}

/**
 * Validate environment configuration
 */
export function validateEnvConfig(config: unknown) {
  try {
    return validationSchemas.envConfig.parse(config);
  } catch (error) {
    console.error('Environment configuration validation failed:', error);
    throw new Error('Invalid environment configuration');
  }
}

/**
 * Security audit logging
 */
export class SecurityAuditLogger {
  private events: Array<{
    timestamp: string;
    event: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    details: any;
  }> = [];
  
  log(event: string, severity: 'info' | 'warning' | 'error' | 'critical', details: any) {
    const entry = {
      timestamp: new Date().toISOString(),
      event,
      severity,
      details
    };
    
    this.events.push(entry);
    
    // Log to console based on severity
    switch (severity) {
      case 'critical':
      case 'error':
        console.error(`[SECURITY ${severity.toUpperCase()}]`, event, details);
        break;
      case 'warning':
        console.warn(`[SECURITY WARNING]`, event, details);
        break;
      default:
        console.log(`[SECURITY INFO]`, event, details);
    }
    
    // TODO: Send to external logging service (e.g., Sentry, DataDog)
  }
  
  getEvents() {
    return this.events;
  }
}

export const securityAuditLogger = new SecurityAuditLogger();

/**
 * Express error handler for security errors
 */
export function securityErrorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  // Log security error
  securityAuditLogger.log('Security error occurred', 'error', {
    error: err.message,
    path: req.path,
    method: req.method,
    ip: req.ip
  });
  
  // Send sanitized error response
  const sanitized = sanitizeError(err);
  res.status(500).json(sanitized);
}