import Stripe from 'stripe';
import { BillingPlan, PLAN_CONFIGS } from './types';

// Initialize Stripe client
const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
if (!stripeSecretKey) {
  throw new Error('STRIPE_SECRET_KEY environment variable is required');
}

export const stripe = new Stripe(stripeSecretKey, {
  apiVersion: '2025-07-30.basil',
  appInfo: {
    name: 'DriftGuard-Checks',
    version: '1.0.0',
  },
});

// Stripe Product and Price Management
export class StripeProductManager {
  
  /**
   * Create or update Stripe products and prices for all billing plans
   */
  async syncProducts(): Promise<void> {
    for (const [planId, config] of Object.entries(PLAN_CONFIGS)) {
      if (planId === 'free') continue; // Skip free plan
      
      await this.createOrUpdateProduct(config);
    }
  }

  /**
   * Create or update a single product with monthly/annual pricing
   */
  private async createOrUpdateProduct(config: typeof PLAN_CONFIGS[BillingPlan]): Promise<void> {
    try {
      // Create or retrieve product
      const products = await stripe.products.list({
        limit: 100,
        active: true,
      });
      
      let product = products.data.find(p => p.metadata.plan_id === config.id);
      
      if (!product) {
        product = await stripe.products.create({
          name: `DriftGuard ${config.name}`,
          description: `DriftGuard ${config.name} plan - ${config.features.slice(0, 3).join(', ')}`,
          metadata: {
            plan_id: config.id,
          },
        });
        console.log(`Created Stripe product for ${config.name}: ${product.id}`);
      }

      // Create monthly price if not exists
      const monthlyPrices = await stripe.prices.list({
        product: product.id,
        recurring: { interval: 'month' },
        active: true,
      });

      if (monthlyPrices.data.length === 0 && config.price > 0) {
        const monthlyPrice = await stripe.prices.create({
          unit_amount: config.price,
          currency: 'usd',
          recurring: { interval: 'month' },
          product: product.id,
          metadata: {
            plan_id: config.id,
            billing_interval: 'monthly',
          },
        });
        console.log(`Created monthly price for ${config.name}: ${monthlyPrice.id}`);
      }

      // Create annual price if not exists and annual pricing is available
      if (config.annualPrice) {
        const annualPrices = await stripe.prices.list({
          product: product.id,
          recurring: { interval: 'year' },
          active: true,
        });

        if (annualPrices.data.length === 0) {
          const annualPrice = await stripe.prices.create({
            unit_amount: config.annualPrice,
            currency: 'usd',
            recurring: { interval: 'year' },
            product: product.id,
            metadata: {
              plan_id: config.id,
              billing_interval: 'annual',
            },
          });
          console.log(`Created annual price for ${config.name}: ${annualPrice.id}`);
        }
      }

    } catch (error) {
      console.error(`Error syncing product for ${config.name}:`, error);
      throw error;
    }
  }

  /**
   * Get Stripe price ID for a plan and billing interval
   */
  async getPriceId(planId: BillingPlan, interval: 'month' | 'year' = 'month'): Promise<string | null> {
    if (planId === 'free') return null;

    try {
      const prices = await stripe.prices.list({
        active: true,
        limit: 100,
      });
      
      const filteredPrices = prices.data.filter(price => 
        price.metadata?.plan_id === planId &&
        price.metadata?.billing_interval === (interval === 'month' ? 'monthly' : 'annual')
      );

      return filteredPrices[0]?.id || null;
    } catch (error) {
      console.error(`Error getting price ID for ${planId}:`, error);
      return null;
    }
  }

  /**
   * Create a customer in Stripe
   */
  async createCustomer(params: {
    email: string;
    organizationId: number;
    organizationLogin: string;
    name?: string;
  }): Promise<Stripe.Customer> {
    return stripe.customers.create({
      email: params.email,
      name: params.name || params.organizationLogin,
      metadata: {
        github_organization_id: params.organizationId.toString(),
        github_organization_login: params.organizationLogin,
      },
    });
  }

  /**
   * Create a subscription for a customer
   */
  async createSubscription(params: {
    customerId: string;
    priceId: string;
    trialPeriodDays?: number;
    metadata?: Record<string, string>;
  }): Promise<Stripe.Subscription> {
    const subscriptionParams: Stripe.SubscriptionCreateParams = {
      customer: params.customerId,
      items: [{ price: params.priceId }],
      payment_behavior: 'default_incomplete',
      payment_settings: { save_default_payment_method: 'on_subscription' },
      expand: ['latest_invoice.payment_intent'],
      metadata: params.metadata || {},
    };

    if (params.trialPeriodDays && params.trialPeriodDays > 0) {
      subscriptionParams.trial_period_days = params.trialPeriodDays;
    }

    return stripe.subscriptions.create(subscriptionParams);
  }

  /**
   * Update subscription plan
   */
  async updateSubscription(params: {
    subscriptionId: string;
    newPriceId: string;
    prorate?: boolean;
  }): Promise<Stripe.Subscription> {
    const subscription = await stripe.subscriptions.retrieve(params.subscriptionId);
    
    return stripe.subscriptions.update(params.subscriptionId, {
      items: [{
        id: subscription.items.data[0].id,
        price: params.newPriceId,
      }],
      proration_behavior: params.prorate ? 'create_prorations' : 'none',
    });
  }

  /**
   * Cancel subscription at period end
   */
  async cancelSubscription(subscriptionId: string, immediately: boolean = false): Promise<Stripe.Subscription> {
    if (immediately) {
      return stripe.subscriptions.cancel(subscriptionId);
    } else {
      return stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: true,
      });
    }
  }

  /**
   * Reactivate a canceled subscription
   */
  async reactivateSubscription(subscriptionId: string): Promise<Stripe.Subscription> {
    return stripe.subscriptions.update(subscriptionId, {
      cancel_at_period_end: false,
    });
  }

  /**
   * Create a checkout session for subscription signup
   */
  async createCheckoutSession(params: {
    customerId: string;
    priceId: string;
    successUrl: string;
    cancelUrl: string;
    trialPeriodDays?: number;
    metadata?: Record<string, string>;
  }): Promise<Stripe.Checkout.Session> {
    const sessionParams: Stripe.Checkout.SessionCreateParams = {
      customer: params.customerId,
      payment_method_types: ['card'],
      line_items: [{
        price: params.priceId,
        quantity: 1,
      }],
      mode: 'subscription',
      success_url: params.successUrl,
      cancel_url: params.cancelUrl,
      metadata: params.metadata || {},
    };

    if (params.trialPeriodDays && params.trialPeriodDays > 0) {
      sessionParams.subscription_data = {
        trial_period_days: params.trialPeriodDays,
      };
    }

    return stripe.checkout.sessions.create(sessionParams);
  }

  /**
   * Create a customer portal session for subscription management
   */
  async createPortalSession(customerId: string, returnUrl: string): Promise<Stripe.BillingPortal.Session> {
    return stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl,
    });
  }
}

export const stripeProductManager = new StripeProductManager();