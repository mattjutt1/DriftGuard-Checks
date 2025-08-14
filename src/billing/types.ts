import { z } from 'zod';

// Billing Plan Types based on pricing.md
export const BillingPlan = z.enum(['free', 'starter', 'team', 'enterprise']);
export type BillingPlan = z.infer<typeof BillingPlan>;

// Plan Configuration
export interface PlanConfig {
  id: BillingPlan;
  name: string;
  price: number; // Monthly price in cents
  annualPrice?: number; // Annual price in cents (with discount)
  stripeProductId?: string;
  stripePriceId?: string;
  stripePriceIdAnnual?: string;
  limits: {
    repositories: number;
    monthlyPRs: number;
    historyDays: number;
    customPolicies: boolean;
    apiAccess: boolean;
    ssoIntegration: boolean;
    auditLogs: boolean;
    prioritySupport: boolean;
  };
  features: string[];
}

// Usage Tracking
export const UsageMetrics = z.object({
  organizationId: z.number(),
  month: z.string(), // Format: YYYY-MM
  repositoryCount: z.number(),
  prAnalysisCount: z.number(),
  lastUpdated: z.date(),
});
export type UsageMetrics = z.infer<typeof UsageMetrics>;

// Subscription Status
export const SubscriptionStatus = z.enum([
  'active',
  'trialing', 
  'past_due',
  'canceled',
  'unpaid',
  'incomplete',
  'incomplete_expired'
]);
export type SubscriptionStatus = z.infer<typeof SubscriptionStatus>;

// Organization Billing
export const OrganizationBilling = z.object({
  organizationId: z.number(),
  githubOrganizationLogin: z.string(),
  plan: BillingPlan,
  status: SubscriptionStatus,
  stripeCustomerId: z.string().optional(),
  stripeSubscriptionId: z.string().optional(),
  currentPeriodStart: z.date().optional(),
  currentPeriodEnd: z.date().optional(),
  trialEnd: z.date().optional(),
  cancelAtPeriodEnd: z.boolean().default(false),
  billingEmail: z.string().email().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
});
export type OrganizationBilling = z.infer<typeof OrganizationBilling>;

// Overage Pricing (from pricing.md)
export const OVERAGE_PRICING = {
  additionalPR: 10, // $0.10 in cents
  additionalRepository: 2000, // $20.00 in cents
} as const;

// Plan Configurations
export const PLAN_CONFIGS: Record<BillingPlan, PlanConfig> = {
  free: {
    id: 'free',
    name: 'Free',
    price: 0,
    limits: {
      repositories: 1,
      monthlyPRs: 100,
      historyDays: 7,
      customPolicies: false,
      apiAccess: false,
      ssoIntegration: false,
      auditLogs: false,
      prioritySupport: false,
    },
    features: [
      'GitHub status checks',
      'Basic violation reports',
      '7-day history',
      'Community support'
    ]
  },
  starter: {
    id: 'starter',
    name: 'Starter', 
    price: 9900, // $99.00
    annualPrice: 99000, // $990.00 (2 months free)
    limits: {
      repositories: 5,
      monthlyPRs: 500,
      historyDays: 90,
      customPolicies: true,
      apiAccess: false,
      ssoIntegration: false,
      auditLogs: false,
      prioritySupport: false,
    },
    features: [
      'All Free features',
      'Slack/Teams integration',
      '90-day history',
      'Policy configuration UI',
      'Team notifications',
      'Email support (48h response)'
    ]
  },
  team: {
    id: 'team',
    name: 'Team',
    price: 29900, // $299.00
    annualPrice: 299000, // $2,990.00 (2 months free)
    limits: {
      repositories: 25,
      monthlyPRs: 2000,
      historyDays: 365,
      customPolicies: true,
      apiAccess: true,
      ssoIntegration: true,
      auditLogs: true,
      prioritySupport: true,
    },
    features: [
      'All Starter features',
      'SSO integration',
      'Audit logs',
      'Advanced analytics',
      'Policy testing sandbox',
      'API access',
      'Priority email support (24h response)'
    ]
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 99900, // $999.00 starting price
    limits: {
      repositories: Infinity,
      monthlyPRs: Infinity,
      historyDays: 365,
      customPolicies: true,
      apiAccess: true,
      ssoIntegration: true,
      auditLogs: true,
      prioritySupport: true,
    },
    features: [
      'All Team features',
      'Unlimited repositories',
      'Unlimited PR analysis',
      'Custom policy development',
      'On-premise deployment options',
      'Custom integrations',
      'Advanced compliance reporting',
      'Priority feature requests',
      'Professional services',
      'Dedicated support + SLA'
    ]
  }
};

// Billing Events for webhooks
export const BillingEvent = z.enum([
  'subscription.created',
  'subscription.updated', 
  'subscription.deleted',
  'invoice.payment_succeeded',
  'invoice.payment_failed',
  'customer.subscription.trial_will_end',
  'customer.subscription.deleted'
]);
export type BillingEvent = z.infer<typeof BillingEvent>;

// Stripe Webhook Payload
export const StripeWebhookPayload = z.object({
  id: z.string(),
  object: z.literal('event'),
  type: BillingEvent,
  data: z.object({
    object: z.record(z.any()),
  }),
  created: z.number(),
  livemode: z.boolean(),
});
export type StripeWebhookPayload = z.infer<typeof StripeWebhookPayload>;