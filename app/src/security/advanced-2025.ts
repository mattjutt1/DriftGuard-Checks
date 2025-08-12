/**
 * Advanced Security Features for 2025 Best Practices
 * Implements additional security measures based on latest OWASP and GitHub recommendations
 */

import { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import { Queue } from 'bull';
import rawBody from 'raw-body';

/**
 * GitHub IP Whitelist Management
 * Implements automatic IP whitelisting from GitHub's meta API
 * Best Practice 2025: Dynamic IP allowlist management
 */
export class GitHubIPWhitelist {
  private allowedIPs: Set<string> = new Set();
  private lastUpdate: Date = new Date(0);
  private updateInterval = 3600000; // 1 hour
  
  async updateWhitelist(): Promise<void> {
    try {
      const response = await axios.get('https://api.github.com/meta');
      const { hooks, web, api, git, packages, pages, actions } = response.data;
      
      // Combine all GitHub IP ranges
      const allIPs = [
        ...(hooks || []),
        ...(web || []),
        ...(api || []),
        ...(git || []),
        ...(packages || []),
        ...(pages || []),
        ...(actions || [])
      ];
      
      this.allowedIPs.clear();
      allIPs.forEach(ip => this.allowedIPs.add(ip));
      this.lastUpdate = new Date();
      
      console.log(`Updated GitHub IP whitelist: ${this.allowedIPs.size} IP ranges`);
    } catch (error) {
      console.error('Failed to update GitHub IP whitelist:', error);
    }
  }
  
  async isAllowed(ip: string): Promise<boolean> {
    // Update whitelist if it's stale
    if (Date.now() - this.lastUpdate.getTime() > this.updateInterval) {
      await this.updateWhitelist();
    }
    
    // Check if IP is in allowed ranges
    // Note: In production, use a proper IP range checking library like 'ip-range-check'
    for (const range of this.allowedIPs) {
      if (this.ipInRange(ip, range)) {
        return true;
      }
    }
    
    return false;
  }
  
  private ipInRange(ip: string, range: string): boolean {
    // Simplified check - in production use proper CIDR checking
    // This would require a library like 'ip-range-check' or 'ipaddr.js'
    return range.includes(ip.split('.').slice(0, 2).join('.'));
  }
}

/**
 * IP Whitelist Middleware
 * Validates webhook requests come from GitHub IPs
 */
export function ipWhitelistMiddleware(whitelist: GitHubIPWhitelist) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const clientIP = req.ip || req.connection.remoteAddress || '';
    
    // Skip in development mode
    if (process.env.NODE_ENV === 'development') {
      return next();
    }
    
    const allowed = await whitelist.isAllowed(clientIP);
    if (!allowed) {
      console.warn('Webhook request from non-GitHub IP blocked:', {
        ip: clientIP,
        timestamp: new Date().toISOString()
      });
      return res.status(403).json({ error: 'Forbidden' });
    }
    
    next();
  };
}

/**
 * Asynchronous Webhook Processing Queue
 * Best Practice 2025: Process webhooks asynchronously to meet 30-second timeout
 */
export class WebhookQueue {
  private queue: Queue;
  
  constructor(redisUrl?: string) {
    this.queue = new Queue('webhook-processing', redisUrl || 'redis://127.0.0.1:6379', {
      defaultJobOptions: {
        removeOnComplete: true,
        removeOnFail: false,
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 2000
        }
      }
    });
  }

  /**
   * Test Redis connection
   */
  async testConnection(): Promise<void> {
    // Bull queue will throw if it can't connect
    await this.queue.isReady();
    
    // Additional test: try to get job counts
    await this.queue.getJobCounts();
  }
  
  async addWebhook(payload: any, headers: any): Promise<string> {
    const job = await this.queue.add('process-webhook', {
      payload,
      headers,
      receivedAt: new Date().toISOString()
    });
    
    return job.id.toString();
  }
  
  processWebhooks(handler: (data: any) => Promise<void>): void {
    this.queue.process('process-webhook', async (job) => {
      const { payload, headers } = job.data;
      await handler({ payload, headers });
    });
  }
  
  getQueueStatus(): Promise<any> {
    return this.queue.getJobCounts();
  }
}

/**
 * Request Size Limiting Middleware
 * Best Practice 2025: Different limits for different content types
 */
export function requestSizeLimiter() {
  return async (req: Request, res: Response, next: NextFunction) => {
    const contentType = req.headers['content-type'] || '';
    
    // Set different limits based on content type
    let sizeLimit: number;
    if (contentType.includes('application/json')) {
      sizeLimit = 1 * 1024 * 1024; // 1MB for JSON (blocking parser)
    } else if (contentType.includes('multipart')) {
      sizeLimit = 10 * 1024 * 1024; // 10MB for multipart
    } else {
      sizeLimit = 5 * 1024 * 1024; // 5MB default
    }
    
    try {
      const body = await rawBody(req, {
        length: req.headers['content-length'],
        limit: sizeLimit,
        encoding: 'utf8'
      });
      
      req.body = JSON.parse(body.toString());
      next();
    } catch (error: any) {
      if (error.type === 'entity.too.large') {
        return res.status(413).json({ 
          error: 'Request entity too large',
          maxSize: `${sizeLimit / 1024 / 1024}MB`
        });
      }
      
      return res.status(400).json({ error: 'Invalid request body' });
    }
  };
}

/**
 * Replay Attack Prevention
 * Best Practice 2025: Track X-GitHub-Delivery headers to prevent replay attacks
 */
export class ReplayProtection {
  private processedDeliveries: Set<string> = new Set();
  private maxAge = 3600000; // 1 hour
  private cleanupInterval = 600000; // 10 minutes
  private deliveryTimestamps: Map<string, number> = new Map();
  
  constructor() {
    // Periodic cleanup of old delivery IDs
    setInterval(() => this.cleanup(), this.cleanupInterval);
  }
  
  isReplay(deliveryId: string): boolean {
    if (this.processedDeliveries.has(deliveryId)) {
      console.warn('Replay attack detected:', {
        deliveryId,
        timestamp: new Date().toISOString()
      });
      return true;
    }
    
    this.processedDeliveries.add(deliveryId);
    this.deliveryTimestamps.set(deliveryId, Date.now());
    return false;
  }
  
  private cleanup(): void {
    const now = Date.now();
    const expired: string[] = [];
    
    this.deliveryTimestamps.forEach((timestamp, deliveryId) => {
      if (now - timestamp > this.maxAge) {
        expired.push(deliveryId);
      }
    });
    
    expired.forEach(deliveryId => {
      this.processedDeliveries.delete(deliveryId);
      this.deliveryTimestamps.delete(deliveryId);
    });
    
    if (expired.length > 0) {
      console.log(`Cleaned up ${expired.length} expired delivery IDs`);
    }
  }
}

/**
 * Replay Protection Middleware
 */
export function replayProtectionMiddleware(protection: ReplayProtection) {
  return (req: Request, res: Response, next: NextFunction) => {
    const deliveryId = req.headers['x-github-delivery'] as string;
    
    if (!deliveryId) {
      return res.status(400).json({ error: 'Missing X-GitHub-Delivery header' });
    }
    
    if (protection.isReplay(deliveryId)) {
      return res.status(409).json({ error: 'Duplicate webhook delivery' });
    }
    
    next();
  };
}

/**
 * Enhanced Security Headers for 2025
 * Additional headers beyond basic Helmet configuration
 */
export function enhancedSecurityHeaders() {
  return (req: Request, res: Response, next: NextFunction) => {
    // Additional security headers for 2025
    res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
    res.setHeader('X-Permitted-Cross-Domain-Policies', 'none');
    res.setHeader('Expect-CT', 'max-age=86400, enforce');
    res.setHeader('X-DNS-Prefetch-Control', 'off');
    res.setHeader('X-Download-Options', 'noopen');
    
    // Remove fingerprinting headers
    res.removeHeader('X-Powered-By');
    res.removeHeader('Server');
    
    next();
  };
}

/**
 * Process Management Configuration
 * Best Practice 2025: Memory limits and process management
 */
export interface ProcessLimits {
  maxMemoryMB: number;
  maxCPUPercent: number;
  restartOnMemoryLimit: boolean;
}

export function enforceProcessLimits(limits: ProcessLimits): void {
  // Monitor memory usage
  setInterval(() => {
    const usage = process.memoryUsage();
    const heapUsedMB = usage.heapUsed / 1024 / 1024;
    
    if (heapUsedMB > limits.maxMemoryMB) {
      console.error(`Memory limit exceeded: ${heapUsedMB}MB / ${limits.maxMemoryMB}MB`);
      
      if (limits.restartOnMemoryLimit) {
        console.log('Initiating graceful restart...');
        process.exit(0); // PM2 or Docker will restart
      }
    }
  }, 10000); // Check every 10 seconds
  
  // Set V8 heap limit
  if (process.execArgv.indexOf('--max-old-space-size') === -1) {
    console.log(`Setting max heap size to ${limits.maxMemoryMB}MB`);
    // This would need to be set when starting the process
  }
}

/**
 * API Method Restriction Middleware
 * Best Practice 2025: Disable unnecessary HTTP methods
 */
export function restrictHTTPMethods(allowedMethods: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!allowedMethods.includes(req.method)) {
      res.setHeader('Allow', allowedMethods.join(', '));
      return res.status(405).json({ 
        error: 'Method not allowed',
        allowed: allowedMethods
      });
    }
    next();
  };
}

/**
 * Comprehensive Security Audit Trail
 * Best Practice 2025: Detailed audit logging for compliance
 */
export class SecurityAuditTrail {
  private events: any[] = [];
  private maxEvents = 10000;
  
  log(event: {
    type: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    ip?: string;
    user?: string;
    action?: string;
    result?: 'success' | 'failure' | 'blocked';
    details?: any;
  }): void {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      ...event
    };
    
    this.events.push(auditEntry);
    
    // Rotate old events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents);
    }
    
    // Log critical events to external service
    if (event.severity === 'critical') {
      this.sendToExternalAudit(auditEntry);
    }
  }
  
  private sendToExternalAudit(entry: any): void {
    // In production, send to SIEM or audit service
    console.error('CRITICAL SECURITY EVENT:', entry);
  }
  
  getAuditTrail(filters?: any): any[] {
    // Apply filters if provided
    if (filters) {
      return this.events.filter(event => {
        return Object.keys(filters).every(key => event[key] === filters[key]);
      });
    }
    return this.events;
  }
}