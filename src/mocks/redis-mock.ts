/**
 * Redis Mock for Development and Testing
 * Provides in-memory Redis-like functionality for local development
 */

import { EventEmitter } from 'events';

interface Job {
  id: string;
  data: any;
  opts?: any;
  timestamp: number;
  status: 'waiting' | 'active' | 'completed' | 'failed';
  result?: any;
  error?: any;
  progress?: number;
  attemptsMade: number;
  processedOn?: number;
  finishedOn?: number;
}

/**
 * Mock Redis Client for testing
 */
export class MockRedisClient extends EventEmitter {
  private data: Map<string, any> = new Map();
  private expiry: Map<string, number> = new Map();
  public connected: boolean = false;

  constructor() {
    super();
    this.connected = true;
    setTimeout(() => this.emit('ready'), 0);
  }

  async connect(): Promise<void> {
    this.connected = true;
    this.emit('connect');
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    this.emit('disconnect');
  }

  async get(key: string): Promise<string | null> {
    this.cleanExpired();
    return this.data.get(key) || null;
  }

  async set(key: string, value: string, options?: { EX?: number }): Promise<string> {
    this.data.set(key, value);
    if (options?.EX) {
      this.expiry.set(key, Date.now() + options.EX * 1000);
    }
    return 'OK';
  }

  async del(key: string): Promise<number> {
    const existed = this.data.has(key);
    this.data.delete(key);
    this.expiry.delete(key);
    return existed ? 1 : 0;
  }

  async exists(key: string): Promise<number> {
    this.cleanExpired();
    return this.data.has(key) ? 1 : 0;
  }

  async expire(key: string, seconds: number): Promise<number> {
    if (this.data.has(key)) {
      this.expiry.set(key, Date.now() + seconds * 1000);
      return 1;
    }
    return 0;
  }

  async keys(pattern: string): Promise<string[]> {
    this.cleanExpired();
    const regex = new RegExp(pattern.replace('*', '.*'));
    return Array.from(this.data.keys()).filter(key => regex.test(key));
  }

  async flushall(): Promise<string> {
    this.data.clear();
    this.expiry.clear();
    return 'OK';
  }

  private cleanExpired(): void {
    const now = Date.now();
    for (const [key, expireTime] of this.expiry.entries()) {
      if (expireTime <= now) {
        this.data.delete(key);
        this.expiry.delete(key);
      }
    }
  }
}

/**
 * Mock Bull Queue for testing
 */
export class MockQueue extends EventEmitter {
  private jobs: Map<string, Job> = new Map();
  private jobCounter: number = 1;
  public name: string;
  private processor?: (job: any) => Promise<any>;
  private isProcessing: boolean = false;

  constructor(name: string, _redisUrl?: string) {
    super();
    this.name = name;
  }

  async add(data: any, opts?: any): Promise<Job> {
    const job: Job = {
      id: String(this.jobCounter++),
      data,
      opts,
      timestamp: Date.now(),
      status: 'waiting',
      attemptsMade: 0
    };
    
    this.jobs.set(job.id, job);
    this.emit('waiting', job);
    
    // Auto-process if processor is set
    if (this.processor && !this.isProcessing) {
      setTimeout(() => this.processNext(), 0);
    }
    
    return job;
  }

  process(processor: (job: any) => Promise<any>): void {
    this.processor = processor;
    if (!this.isProcessing) {
      this.processNext();
    }
  }

  private async processNext(): Promise<void> {
    if (this.isProcessing || !this.processor) return;
    
    const waitingJob = Array.from(this.jobs.values()).find(j => j.status === 'waiting');
    if (!waitingJob) return;
    
    this.isProcessing = true;
    waitingJob.status = 'active';
    waitingJob.processedOn = Date.now();
    this.emit('active', waitingJob);
    
    try {
      const result = await this.processor({ 
        id: waitingJob.id,
        data: waitingJob.data,
        attemptsMade: waitingJob.attemptsMade,
        progress: (progress: number) => {
          waitingJob.progress = progress;
          this.emit('progress', waitingJob, progress);
        }
      });
      
      waitingJob.status = 'completed';
      waitingJob.result = result;
      waitingJob.finishedOn = Date.now();
      this.emit('completed', waitingJob, result);
    } catch (error) {
      waitingJob.status = 'failed';
      waitingJob.error = error;
      waitingJob.attemptsMade++;
      waitingJob.finishedOn = Date.now();
      this.emit('failed', waitingJob, error);
    } finally {
      this.isProcessing = false;
      // Process next job if available
      setTimeout(() => this.processNext(), 0);
    }
  }

  async getJob(jobId: string): Promise<Job | undefined> {
    return this.jobs.get(jobId);
  }

  async getJobs(status: string[]): Promise<Job[]> {
    return Array.from(this.jobs.values()).filter(j => status.includes(j.status));
  }

  async empty(): Promise<void> {
    this.jobs.clear();
  }

  async close(): Promise<void> {
    this.emit('closed');
  }

  async clean(grace: number, status: string): Promise<string[]> {
    const now = Date.now();
    const cleaned: string[] = [];
    
    for (const [id, job] of this.jobs.entries()) {
      if (job.status === status && job.finishedOn && (now - job.finishedOn > grace)) {
        this.jobs.delete(id);
        cleaned.push(id);
      }
    }
    
    return cleaned;
  }

  async getJobCounts(): Promise<{ [key: string]: number }> {
    const counts: { [key: string]: number } = {
      waiting: 0,
      active: 0,
      completed: 0,
      failed: 0
    };
    
    for (const job of this.jobs.values()) {
      counts[job.status]++;
    }
    
    return counts;
  }
}

/**
 * Factory to create mock Redis client or Bull queue based on environment
 */
export function createMockRedis(): MockRedisClient {
  return new MockRedisClient();
}

export function createMockQueue(name: string, redisUrl?: string): MockQueue {
  return new MockQueue(name, redisUrl);
}

/**
 * Helper to determine if we should use mock or real Redis
 */
export function shouldUseMockRedis(): boolean {
  return process.env.USE_MOCK_REDIS === 'true' || 
         process.env.NODE_ENV === 'test' ||
         (!process.env.REDIS_URL && process.env.NODE_ENV === 'development');
}