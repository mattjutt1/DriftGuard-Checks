import { UsageMetrics, OrganizationBilling, BillingPlan, PLAN_CONFIGS, OVERAGE_PRICING } from './types';

/**
 * Usage tracking and enforcement for billing plans
 */
export class UsageTracker {
  private usageCache = new Map<string, UsageMetrics>();
  private lastFlush = Date.now();
  private readonly FLUSH_INTERVAL = 60 * 1000; // 1 minute

  /**
   * Record a PR analysis for usage tracking
   */
  async recordPRAnalysis(organizationId: number): Promise<void> {
    const month = this.getCurrentMonth();
    const key = `${organizationId}-${month}`;
    
    const current = this.usageCache.get(key) || {
      organizationId,
      month,
      repositoryCount: 0,
      prAnalysisCount: 0,
      lastUpdated: new Date(),
    };

    current.prAnalysisCount += 1;
    current.lastUpdated = new Date();
    this.usageCache.set(key, current);

    // Flush periodically
    if (Date.now() - this.lastFlush > this.FLUSH_INTERVAL) {
      await this.flushToStorage();
    }
  }

  /**
   * Update repository count for an organization
   */
  async updateRepositoryCount(organizationId: number, repositoryCount: number): Promise<void> {
    const month = this.getCurrentMonth();
    const key = `${organizationId}-${month}`;
    
    const current = this.usageCache.get(key) || {
      organizationId,
      month,
      repositoryCount: 0,
      prAnalysisCount: 0,
      lastUpdated: new Date(),
    };

    current.repositoryCount = repositoryCount;
    current.lastUpdated = new Date();
    this.usageCache.set(key, current);
  }

  /**
   * Get current usage for an organization
   */
  async getUsage(organizationId: number, month?: string): Promise<UsageMetrics | null> {
    const targetMonth = month || this.getCurrentMonth();
    const key = `${organizationId}-${targetMonth}`;
    
    // Check cache first
    const cached = this.usageCache.get(key);
    if (cached) {
      return cached;
    }

    // Load from storage (implement based on your storage solution)
    return this.loadFromStorage(organizationId, targetMonth);
  }

  /**
   * Check if organization can perform an action based on their plan limits
   */
  async canPerformAction(
    organizationId: number, 
    action: 'analyze_pr' | 'add_repository',
    billing: OrganizationBilling
  ): Promise<{ allowed: boolean; reason?: string; overageCharge?: number }> {
    const usage = await this.getUsage(organizationId);
    const planConfig = PLAN_CONFIGS[billing.plan];

    if (!usage) {
      // No usage recorded yet, allow action
      return { allowed: true };
    }

    switch (action) {
      case 'analyze_pr':
        if (usage.prAnalysisCount >= planConfig.limits.monthlyPRs) {
          const overageCharge = OVERAGE_PRICING.additionalPR;
          
          // Free plan: hard limit
          if (billing.plan === 'free') {
            return { 
              allowed: false, 
              reason: `Monthly PR analysis limit of ${planConfig.limits.monthlyPRs} reached. Upgrade to continue.`
            };
          }
          
          // Paid plans: allow with overage charge
          return { 
            allowed: true, 
            overageCharge,
            reason: `PR analysis limit exceeded. Additional charge of $${(overageCharge / 100).toFixed(2)} will apply.`
          };
        }
        return { allowed: true };

      case 'add_repository':
        if (usage.repositoryCount >= planConfig.limits.repositories) {
          const overageCharge = OVERAGE_PRICING.additionalRepository;
          
          // Free plan: hard limit
          if (billing.plan === 'free') {
            return { 
              allowed: false, 
              reason: `Repository limit of ${planConfig.limits.repositories} reached. Upgrade to continue.`
            };
          }
          
          // Paid plans: allow with overage charge  
          return { 
            allowed: true, 
            overageCharge,
            reason: `Repository limit exceeded. Additional charge of $${(overageCharge / 100).toFixed(2)}/month will apply.`
          };
        }
        return { allowed: true };

      default:
        return { allowed: true };
    }
  }

  /**
   * Calculate overage charges for current month
   */
  async calculateOverageCharges(organizationId: number, billing: OrganizationBilling): Promise<{
    prOverage: number;
    repositoryOverage: number;
    totalOverage: number;
  }> {
    const usage = await this.getUsage(organizationId);
    const planConfig = PLAN_CONFIGS[billing.plan];

    if (!usage || billing.plan === 'free') {
      return { prOverage: 0, repositoryOverage: 0, totalOverage: 0 };
    }

    const prOverage = Math.max(0, usage.prAnalysisCount - planConfig.limits.monthlyPRs);
    const repositoryOverage = Math.max(0, usage.repositoryCount - planConfig.limits.repositories);

    const prOverageCharge = prOverage * OVERAGE_PRICING.additionalPR;
    const repositoryOverageCharge = repositoryOverage * OVERAGE_PRICING.additionalRepository;
    const totalOverage = prOverageCharge + repositoryOverageCharge;

    return {
      prOverage: prOverageCharge,
      repositoryOverage: repositoryOverageCharge,
      totalOverage,
    };
  }

  /**
   * Get usage dashboard data for an organization
   */
  async getUsageDashboard(organizationId: number, billing: OrganizationBilling): Promise<{
    current: UsageMetrics | null;
    planLimits: typeof PLAN_CONFIGS[BillingPlan]['limits'];
    utilizationPercentage: {
      repositories: number;
      monthlyPRs: number;
    };
    overageCharges: {
      prOverage: number;
      repositoryOverage: number;
      totalOverage: number;
    };
    recommendations: string[];
  }> {
    const usage = await this.getUsage(organizationId);
    const planConfig = PLAN_CONFIGS[billing.plan];
    const overageCharges = await this.calculateOverageCharges(organizationId, billing);

    const utilizationPercentage = {
      repositories: usage ? Math.min(100, (usage.repositoryCount / planConfig.limits.repositories) * 100) : 0,
      monthlyPRs: usage ? Math.min(100, (usage.prAnalysisCount / planConfig.limits.monthlyPRs) * 100) : 0,
    };

    const recommendations: string[] = [];
    
    // Generate recommendations based on usage
    if (utilizationPercentage.monthlyPRs > 80) {
      recommendations.push('Consider upgrading your plan to avoid overage charges on PR analysis.');
    }
    
    if (utilizationPercentage.repositories > 80) {
      recommendations.push('You\'re approaching your repository limit. Consider upgrading for more repositories.');
    }
    
    if (overageCharges.totalOverage > 0 && billing.plan !== 'enterprise') {
      const nextPlan = this.getNextPlanRecommendation(billing.plan);
      if (nextPlan) {
        recommendations.push(`Upgrade to ${nextPlan} plan to eliminate overage charges and get more features.`);
      }
    }

    return {
      current: usage,
      planLimits: planConfig.limits,
      utilizationPercentage,
      overageCharges,
      recommendations,
    };
  }

  /**
   * Get plan upgrade recommendation based on current plan
   */
  private getNextPlanRecommendation(currentPlan: BillingPlan): string | null {
    const planHierarchy: BillingPlan[] = ['free', 'starter', 'team', 'enterprise'];
    const currentIndex = planHierarchy.indexOf(currentPlan);
    
    if (currentIndex < planHierarchy.length - 1) {
      return PLAN_CONFIGS[planHierarchy[currentIndex + 1]].name;
    }
    
    return null;
  }

  /**
   * Reset usage for new month (typically called by scheduled job)
   */
  async resetMonthlyUsage(organizationId: number): Promise<void> {
    const month = this.getCurrentMonth();
    const key = `${organizationId}-${month}`;
    
    // Clear from cache
    this.usageCache.delete(key);
    
    // Archive previous month data in storage if needed
    // Implementation depends on your storage solution
  }

  /**
   * Get current month in YYYY-MM format
   */
  private getCurrentMonth(): string {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  }

  /**
   * Flush cached usage data to persistent storage
   */
  private async flushToStorage(): Promise<void> {
    // Implementation depends on your storage solution
    // For now, we'll use in-memory storage but this should be persistent
    
    for (const [key, usage] of this.usageCache.entries()) {
      // Store to database/Redis/etc
      console.log(`Flushing usage data for ${key}:`, usage);
    }
    
    this.lastFlush = Date.now();
  }

  /**
   * Load usage data from persistent storage
   */
  private async loadFromStorage(organizationId: number, month: string): Promise<UsageMetrics | null> {
    // Implementation depends on your storage solution
    // This would typically query your database
    
    // For now, return null (no data found)
    return null;
  }
}

export const usageTracker = new UsageTracker();