import { Probot } from 'probot';
import { usageTracker } from './usage-tracker';
import { OrganizationBilling, BillingPlan } from './types';

/**
 * GitHub App billing integration
 * Enforces plan limits and tracks usage for billing
 */
export class GitHubBillingIntegration {
  
  /**
   * Check if organization can analyze a PR based on their billing plan
   */
  async canAnalyzePR(organizationId: number): Promise<{
    allowed: boolean;
    reason?: string;
    overageCharge?: number;
    upgradeUrl?: string;
  }> {
    const billing = await this.getOrganizationBilling(organizationId);
    
    if (!billing) {
      // No billing record - default to free plan with limits
      return {
        allowed: false,
        reason: 'No billing information found. Please set up billing to continue.',
        upgradeUrl: this.getBillingSetupUrl(organizationId),
      };
    }

    // Check if subscription is active
    if (!this.isSubscriptionActive(billing)) {
      return {
        allowed: false,
        reason: this.getSubscriptionInactiveReason(billing),
        upgradeUrl: this.getBillingPortalUrl(billing.stripeCustomerId),
      };
    }

    // Check usage limits
    const result = await usageTracker.canPerformAction(organizationId, 'analyze_pr', billing);
    
    if (!result.allowed && billing.plan === 'free') {
      return {
        ...result,
        upgradeUrl: this.getUpgradeUrl(organizationId, billing.plan),
      };
    }

    return result;
  }

  /**
   * Record PR analysis for billing and usage tracking
   */
  async recordPRAnalysis(organizationId: number, repositoryFullName: string): Promise<void> {
    // Track usage for billing
    await usageTracker.recordPRAnalysis(organizationId);
    
    // Update repository count if needed
    const repoCount = await this.getActiveRepositoryCount(organizationId);
    await usageTracker.updateRepositoryCount(organizationId, repoCount);
    
    console.log(`Recorded PR analysis for org ${organizationId}, repo ${repositoryFullName}`);
  }

  /**
   * Check if organization can add a new repository
   */
  async canAddRepository(organizationId: number): Promise<{
    allowed: boolean;
    reason?: string;
    overageCharge?: number;
    upgradeUrl?: string;
  }> {
    const billing = await this.getOrganizationBilling(organizationId);
    
    if (!billing) {
      return {
        allowed: false,
        reason: 'No billing information found. Please set up billing to continue.',
        upgradeUrl: this.getBillingSetupUrl(organizationId),
      };
    }

    if (!this.isSubscriptionActive(billing)) {
      return {
        allowed: false,
        reason: this.getSubscriptionInactiveReason(billing),
        upgradeUrl: this.getBillingPortalUrl(billing.stripeCustomerId),
      };
    }

    const result = await usageTracker.canPerformAction(organizationId, 'add_repository', billing);
    
    if (!result.allowed && billing.plan === 'free') {
      return {
        ...result,
        upgradeUrl: this.getUpgradeUrl(organizationId, billing.plan),
      };
    }

    return result;
  }

  /**
   * Get billing enforcement middleware for PR checks
   */
  getBillingEnforcementMiddleware() {
    return async (context: any, next: () => Promise<void>) => {
      const { payload } = context;
      
      // Skip billing for private repos during development
      if (process.env.NODE_ENV === 'development' && !process.env.ENFORCE_BILLING) {
        return next();
      }

      const organizationId = payload.organization?.id || payload.repository?.owner?.id;
      
      if (!organizationId) {
        console.warn('No organization ID found in payload');
        return next();
      }

      // Check if PR analysis is allowed
      const result = await this.canAnalyzePR(organizationId);
      
      if (!result.allowed) {
        // Create a failing check run with billing message
        await this.createBillingCheckRun(context, result);
        return; // Don't continue with analysis
      }

      // Record the analysis for billing
      const repositoryFullName = payload.repository?.full_name;
      if (repositoryFullName) {
        await this.recordPRAnalysis(organizationId, repositoryFullName);
      }

      // Continue with normal processing
      return next();
    };
  }

  /**
   * Create a check run that indicates billing issue
   */
  private async createBillingCheckRun(context: any, result: {
    reason?: string;
    upgradeUrl?: string;
    overageCharge?: number;
  }): Promise<void> {
    const { payload } = context;
    
    let summary = result.reason || 'Billing limit reached';
    let text = 'Your current plan limits have been reached.';
    
    if (result.upgradeUrl) {
      text += `\n\n[Upgrade your plan](${result.upgradeUrl}) to continue using DriftGuard.`;
    }
    
    if (result.overageCharge) {
      text += `\n\nContinuing will incur an additional charge of $${(result.overageCharge / 100).toFixed(2)}.`;
    }

    await context.octokit.checks.create({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      name: 'DriftGuard Billing',
      head_sha: payload.pull_request?.head?.sha || payload.after,
      status: 'completed',
      conclusion: 'action_required',
      output: {
        title: 'Billing Action Required',
        summary,
        text,
      },
      actions: result.upgradeUrl ? [{
        label: 'Upgrade Plan',
        description: 'Upgrade to continue using DriftGuard',
        identifier: 'upgrade_plan',
      }] : undefined,
    });
  }

  /**
   * Check if subscription is active
   */
  private isSubscriptionActive(billing: OrganizationBilling): boolean {
    return ['active', 'trialing'].includes(billing.status);
  }

  /**
   * Get reason for inactive subscription
   */
  private getSubscriptionInactiveReason(billing: OrganizationBilling): string {
    switch (billing.status) {
      case 'past_due':
        return 'Your subscription payment is past due. Please update your payment method.';
      case 'canceled':
        return 'Your subscription has been canceled. Please reactivate to continue.';
      case 'unpaid':
        return 'Your subscription is unpaid. Please complete payment to continue.';
      case 'incomplete':
        return 'Your subscription setup is incomplete. Please complete the setup process.';
      case 'incomplete_expired':
        return 'Your subscription setup has expired. Please start the setup process again.';
      default:
        return 'Your subscription is not active. Please check your billing status.';
    }
  }

  /**
   * Get current repository count for organization
   */
  private async getActiveRepositoryCount(organizationId: number): Promise<number> {
    // TODO: Implement based on your installation tracking
    // This would typically query installations and count active repositories
    
    // For now, return a placeholder
    return 1;
  }

  /**
   * Get organization billing information
   */
  private async getOrganizationBilling(organizationId: number): Promise<OrganizationBilling | null> {
    // TODO: Implement database query
    // This would typically query your database for billing information
    
    // For now, return a default free plan
    return {
      organizationId,
      githubOrganizationLogin: 'example-org',
      plan: 'free',
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date(),
      cancelAtPeriodEnd: false,
    };
  }

  /**
   * Get billing setup URL for new organizations
   */
  private getBillingSetupUrl(organizationId: number): string {
    const baseUrl = process.env.APP_URL || 'https://www.mmtuentertainment.com';
    return `${baseUrl}/billing/setup?org=${organizationId}`;
  }

  /**
   * Get upgrade URL for existing customers
   */
  private getUpgradeUrl(organizationId: number, currentPlan: BillingPlan): string {
    const baseUrl = process.env.APP_URL || 'https://www.mmtuentertainment.com';
    return `${baseUrl}/billing/upgrade?org=${organizationId}&from=${currentPlan}`;
  }

  /**
   * Get Stripe customer portal URL
   */
  private getBillingPortalUrl(stripeCustomerId?: string): string {
    const baseUrl = process.env.APP_URL || 'https://www.mmtuentertainment.com';
    if (stripeCustomerId) {
      return `${baseUrl}/billing/portal?customer=${stripeCustomerId}`;
    }
    return `${baseUrl}/billing`;
  }
}

export const githubBillingIntegration = new GitHubBillingIntegration();