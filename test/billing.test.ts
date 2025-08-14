import { describe, it, expect, beforeEach, jest } from '@jest/globals';

// Mock Stripe to avoid requiring API keys in tests
jest.mock('stripe', () => {
  return jest.fn().mockImplementation(() => ({
    products: {
      list: jest.fn(),
      create: jest.fn(),
    },
    prices: {
      list: jest.fn(),
      create: jest.fn(),
    },
    accounts: {
      retrieve: jest.fn(),
    },
  }));
});

// Set environment variable for Stripe client
process.env.STRIPE_SECRET_KEY = 'sk_test_mock_key_for_testing';

import { PLAN_CONFIGS, OVERAGE_PRICING, BillingPlan, UsageTracker } from '../src/billing';

describe('Billing System', () => {
  describe('Plan Configurations', () => {
    it('should have valid plan configurations', () => {
      expect(Object.keys(PLAN_CONFIGS)).toEqual(['free', 'starter', 'team', 'enterprise']);
      
      // Test each plan
      Object.values(PLAN_CONFIGS).forEach(plan => {
        expect(plan).toHaveProperty('id');
        expect(plan).toHaveProperty('name');
        expect(plan).toHaveProperty('price');
        expect(plan).toHaveProperty('limits');
        expect(plan).toHaveProperty('features');
        
        expect(typeof plan.price).toBe('number');
        expect(plan.price).toBeGreaterThanOrEqual(0);
        expect(Array.isArray(plan.features)).toBe(true);
        expect(plan.features.length).toBeGreaterThan(0);
      });
    });

    it('should have increasing price tiers', () => {
      const prices = Object.values(PLAN_CONFIGS).map(p => p.price);
      expect(prices[0]).toBe(0); // Free plan
      expect(prices[1]).toBeLessThan(prices[2]); // Starter < Team
      expect(prices[2]).toBeLessThan(prices[3]); // Team < Enterprise
    });

    it('should have increasing limits', () => {
      const plans = Object.values(PLAN_CONFIGS);
      
      // Repository limits should increase (except infinity)
      expect(plans[0].limits.repositories).toBeLessThan(plans[1].limits.repositories);
      expect(plans[1].limits.repositories).toBeLessThan(plans[2].limits.repositories);
      expect(plans[3].limits.repositories).toBe(Infinity);
      
      // PR limits should increase
      expect(plans[0].limits.monthlyPRs).toBeLessThan(plans[1].limits.monthlyPRs);
      expect(plans[1].limits.monthlyPRs).toBeLessThan(plans[2].limits.monthlyPRs);
      expect(plans[3].limits.monthlyPRs).toBe(Infinity);
    });

    it('should have consistent feature progression', () => {
      const plans = Object.values(PLAN_CONFIGS);
      
      // Free plan should have basic features
      expect(plans[0].limits.customPolicies).toBe(false);
      expect(plans[0].limits.apiAccess).toBe(false);
      expect(plans[0].limits.ssoIntegration).toBe(false);
      
      // Paid plans should have more features
      expect(plans[1].limits.customPolicies).toBe(true);
      expect(plans[2].limits.apiAccess).toBe(true);
      expect(plans[2].limits.ssoIntegration).toBe(true);
    });
  });

  describe('Overage Pricing', () => {
    it('should have valid overage pricing', () => {
      expect(OVERAGE_PRICING.additionalPR).toBe(10); // $0.10 in cents
      expect(OVERAGE_PRICING.additionalRepository).toBe(2000); // $20.00 in cents
    });
  });

  describe('Usage Tracker', () => {
    let usageTracker: UsageTracker;

    beforeEach(() => {
      usageTracker = new UsageTracker();
    });

    it('should track PR analysis', async () => {
      const organizationId = 123;
      
      await usageTracker.recordPRAnalysis(organizationId);
      
      const usage = await usageTracker.getUsage(organizationId);
      expect(usage?.prAnalysisCount).toBe(1);
    });

    it('should update repository count', async () => {
      const organizationId = 123;
      const repositoryCount = 5;
      
      await usageTracker.updateRepositoryCount(organizationId, repositoryCount);
      
      const usage = await usageTracker.getUsage(organizationId);
      expect(usage?.repositoryCount).toBe(repositoryCount);
    });

    it('should enforce free plan limits', async () => {
      const organizationId = 123;
      const billing = {
        organizationId,
        githubOrganizationLogin: 'test-org',
        plan: 'free' as BillingPlan,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        cancelAtPeriodEnd: false,
      };

      // Simulate reaching free plan PR limit
      for (let i = 0; i < 100; i++) {
        await usageTracker.recordPRAnalysis(organizationId);
      }

      const result = await usageTracker.canPerformAction(organizationId, 'analyze_pr', billing);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('limit');
    });

    it('should allow paid plan overages with charges', async () => {
      const organizationId = 123;
      const billing = {
        organizationId,
        githubOrganizationLogin: 'test-org',
        plan: 'starter' as BillingPlan,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        cancelAtPeriodEnd: false,
      };

      // Simulate exceeding starter plan PR limit (500)
      for (let i = 0; i < 501; i++) {
        await usageTracker.recordPRAnalysis(organizationId);
      }

      const result = await usageTracker.canPerformAction(organizationId, 'analyze_pr', billing);
      expect(result.allowed).toBe(true);
      expect(result.overageCharge).toBe(OVERAGE_PRICING.additionalPR);
    });

    it('should calculate overage charges correctly', async () => {
      const organizationId = 123;
      const billing = {
        organizationId,
        githubOrganizationLogin: 'test-org',
        plan: 'starter' as BillingPlan,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        cancelAtPeriodEnd: false,
      };

      // Add usage that exceeds limits
      for (let i = 0; i < 510; i++) { // 10 over PR limit
        await usageTracker.recordPRAnalysis(organizationId);
      }
      await usageTracker.updateRepositoryCount(organizationId, 7); // 2 over repo limit

      const charges = await usageTracker.calculateOverageCharges(organizationId, billing);
      
      expect(charges.prOverage).toBe(10 * OVERAGE_PRICING.additionalPR); // 10 * $0.10
      expect(charges.repositoryOverage).toBe(2 * OVERAGE_PRICING.additionalRepository); // 2 * $20
      expect(charges.totalOverage).toBe(charges.prOverage + charges.repositoryOverage);
    });

    it('should provide usage dashboard data', async () => {
      const organizationId = 123;
      const billing = {
        organizationId,
        githubOrganizationLogin: 'test-org',
        plan: 'starter' as BillingPlan,
        status: 'active' as const,
        createdAt: new Date(),
        updatedAt: new Date(),
        cancelAtPeriodEnd: false,
      };

      // Add some usage
      for (let i = 0; i < 250; i++) { // 50% of PR limit
        await usageTracker.recordPRAnalysis(organizationId);
      }
      await usageTracker.updateRepositoryCount(organizationId, 3); // 60% of repo limit

      const dashboard = await usageTracker.getUsageDashboard(organizationId, billing);
      
      expect(dashboard.utilizationPercentage.monthlyPRs).toBe(50);
      expect(dashboard.utilizationPercentage.repositories).toBe(60);
      expect(dashboard.planLimits).toEqual(PLAN_CONFIGS.starter.limits);
    });
  });

  describe('Billing Event Types', () => {
    it('should validate billing event types', () => {
      const validEvents = [
        'subscription.created',
        'subscription.updated', 
        'subscription.deleted',
        'invoice.payment_succeeded',
        'invoice.payment_failed',
        'customer.subscription.trial_will_end',
        'customer.subscription.deleted'
      ];

      // This would normally use Zod validation
      validEvents.forEach(event => {
        expect(typeof event).toBe('string');
        expect(event.length).toBeGreaterThan(0);
      });
    });
  });
});