import { Request, Response } from 'express';
import { stripe } from './stripe-client';
import { StripeWebhookPayload, BillingEvent, OrganizationBilling, SubscriptionStatus } from './types';
import Stripe from 'stripe';

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
if (!webhookSecret) {
  console.warn('STRIPE_WEBHOOK_SECRET not set - Stripe webhooks will not be verified');
}

/**
 * Handle Stripe webhook events for billing updates
 */
export class StripeWebhookHandler {
  
  /**
   * Process incoming Stripe webhook
   */
  async handleWebhook(req: Request, res: Response): Promise<void> {
    const sig = req.headers['stripe-signature'] as string;
    
    let event: Stripe.Event;
    
    try {
      if (webhookSecret) {
        // Verify webhook signature
        event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
      } else {
        // Development mode - parse without verification
        event = JSON.parse(req.body);
      }
    } catch (err) {
      console.error('Webhook signature verification failed:', err);
      res.status(400).send('Webhook Error: Invalid signature');
      return;
    }

    try {
      await this.processWebhookEvent(event);
      res.status(200).json({ received: true });
    } catch (error) {
      console.error('Error processing webhook event:', error);
      res.status(500).json({ error: 'Webhook processing failed' });
    }
  }

  /**
   * Process specific webhook event types
   */
  private async processWebhookEvent(event: Stripe.Event): Promise<void> {
    console.log(`Processing webhook event: ${event.type}`);

    switch (event.type) {
      case 'customer.subscription.created':
        await this.handleSubscriptionCreated(event.data.object as Stripe.Subscription);
        break;
        
      case 'customer.subscription.updated':
        await this.handleSubscriptionUpdated(event.data.object as Stripe.Subscription);
        break;
        
      case 'customer.subscription.deleted':
        await this.handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;
        
      case 'invoice.payment_succeeded':
        await this.handlePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;
        
      case 'invoice.payment_failed':
        await this.handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;
        
      case 'customer.subscription.trial_will_end':
        await this.handleTrialWillEnd(event.data.object as Stripe.Subscription);
        break;
        
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
  }

  /**
   * Handle subscription creation
   */
  private async handleSubscriptionCreated(subscription: Stripe.Subscription): Promise<void> {
    const customer = await this.getCustomerFromSubscription(subscription);
    if (!customer) return;

    const organizationId = parseInt(customer.metadata.github_organization_id);
    if (!organizationId) {
      console.error('No GitHub organization ID found in customer metadata');
      return;
    }

    // Extract plan from subscription metadata or price
    const planId = await this.extractPlanFromSubscription(subscription);
    
    const billing: Partial<OrganizationBilling> = {
      organizationId,
      githubOrganizationLogin: customer.metadata.github_organization_login,
      plan: planId,
      status: this.mapStripeStatus(subscription.status),
      stripeCustomerId: customer.id,
      stripeSubscriptionId: subscription.id,
      currentPeriodStart: new Date((subscription as any).current_period_start * 1000),
      currentPeriodEnd: new Date((subscription as any).current_period_end * 1000),
      trialEnd: subscription.trial_end ? new Date(subscription.trial_end * 1000) : undefined,
      billingEmail: customer.email || undefined,
      updatedAt: new Date(),
    };

    await this.updateOrganizationBilling(billing);
    
    console.log(`Subscription created for organization ${organizationId} (${planId} plan)`);
  }

  /**
   * Handle subscription updates
   */
  private async handleSubscriptionUpdated(subscription: Stripe.Subscription): Promise<void> {
    const customer = await this.getCustomerFromSubscription(subscription);
    if (!customer) return;

    const organizationId = parseInt(customer.metadata.github_organization_id);
    if (!organizationId) return;

    const planId = await this.extractPlanFromSubscription(subscription);
    
    const updates: Partial<OrganizationBilling> = {
      organizationId,
      plan: planId,
      status: this.mapStripeStatus(subscription.status),
      currentPeriodStart: new Date((subscription as any).current_period_start * 1000),
      currentPeriodEnd: new Date((subscription as any).current_period_end * 1000),
      trialEnd: subscription.trial_end ? new Date(subscription.trial_end * 1000) : undefined,
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
      updatedAt: new Date(),
    };

    await this.updateOrganizationBilling(updates);
    
    console.log(`Subscription updated for organization ${organizationId} (${planId} plan, status: ${subscription.status})`);
  }

  /**
   * Handle subscription deletion/cancellation
   */
  private async handleSubscriptionDeleted(subscription: Stripe.Subscription): Promise<void> {
    const customer = await this.getCustomerFromSubscription(subscription);
    if (!customer) return;

    const organizationId = parseInt(customer.metadata.github_organization_id);
    if (!organizationId) return;

    const updates: Partial<OrganizationBilling> = {
      organizationId,
      plan: 'free', // Downgrade to free plan
      status: 'canceled',
      stripeSubscriptionId: undefined,
      currentPeriodStart: undefined,
      currentPeriodEnd: undefined,
      trialEnd: undefined,
      cancelAtPeriodEnd: false,
      updatedAt: new Date(),
    };

    await this.updateOrganizationBilling(updates);
    
    console.log(`Subscription canceled for organization ${organizationId} - downgraded to free plan`);
  }

  /**
   * Handle successful payment
   */
  private async handlePaymentSucceeded(invoice: Stripe.Invoice): Promise<void> {
    if ((invoice as any).subscription) {
      const subscription = await stripe.subscriptions.retrieve((invoice as any).subscription as string);
      const customer = await this.getCustomerFromSubscription(subscription);
      
      if (!customer) return;
      
      const organizationId = parseInt(customer.metadata.github_organization_id);
      if (!organizationId) return;

      // Update subscription to active status if it was past_due
      const updates: Partial<OrganizationBilling> = {
        organizationId,
        status: 'active',
        updatedAt: new Date(),
      };

      await this.updateOrganizationBilling(updates);
      
      console.log(`Payment succeeded for organization ${organizationId} - subscription reactivated`);
    }
  }

  /**
   * Handle failed payment
   */
  private async handlePaymentFailed(invoice: Stripe.Invoice): Promise<void> {
    if ((invoice as any).subscription) {
      const subscription = await stripe.subscriptions.retrieve((invoice as any).subscription as string);
      const customer = await this.getCustomerFromSubscription(subscription);
      
      if (!customer) return;
      
      const organizationId = parseInt(customer.metadata.github_organization_id);
      if (!organizationId) return;

      const updates: Partial<OrganizationBilling> = {
        organizationId,
        status: 'past_due',
        updatedAt: new Date(),
      };

      await this.updateOrganizationBilling(updates);
      
      console.log(`Payment failed for organization ${organizationId} - subscription marked as past_due`);
      
      // TODO: Send notification to organization admins about failed payment
    }
  }

  /**
   * Handle trial ending soon
   */
  private async handleTrialWillEnd(subscription: Stripe.Subscription): Promise<void> {
    const customer = await this.getCustomerFromSubscription(subscription);
    if (!customer) return;

    const organizationId = parseInt(customer.metadata.github_organization_id);
    if (!organizationId) return;
    
    console.log(`Trial ending soon for organization ${organizationId}`);
    
    // TODO: Send notification to organization admins about trial ending
    // TODO: Trigger email campaign for trial conversion
  }

  /**
   * Get customer from subscription
   */
  private async getCustomerFromSubscription(subscription: Stripe.Subscription): Promise<Stripe.Customer | null> {
    try {
      const customer = await stripe.customers.retrieve(subscription.customer as string);
      return customer as Stripe.Customer;
    } catch (error) {
      console.error('Error retrieving customer:', error);
      return null;
    }
  }

  /**
   * Extract plan ID from subscription
   */
  private async extractPlanFromSubscription(subscription: Stripe.Subscription): Promise<'free' | 'starter' | 'team' | 'enterprise'> {
    // Get the price from the subscription
    const priceId = subscription.items.data[0]?.price?.id;
    
    if (priceId) {
      try {
        const price = await stripe.prices.retrieve(priceId);
        const planId = price.metadata?.plan_id;
        
        if (planId && ['free', 'starter', 'team', 'enterprise'].includes(planId)) {
          return planId as 'free' | 'starter' | 'team' | 'enterprise';
        }
      } catch (error) {
        console.error('Error retrieving price metadata:', error);
      }
    }
    
    // Fallback to starter if we can't determine the plan
    return 'starter';
  }

  /**
   * Map Stripe subscription status to our internal status
   */
  private mapStripeStatus(stripeStatus: Stripe.Subscription.Status): SubscriptionStatus {
    switch (stripeStatus) {
      case 'active':
        return 'active';
      case 'trialing':
        return 'trialing';
      case 'past_due':
        return 'past_due';
      case 'canceled':
        return 'canceled';
      case 'unpaid':
        return 'unpaid';
      case 'incomplete':
        return 'incomplete';
      case 'incomplete_expired':
        return 'incomplete_expired';
      default:
        return 'canceled';
    }
  }

  /**
   * Update organization billing in storage
   * Implementation depends on your storage solution
   */
  private async updateOrganizationBilling(billing: Partial<OrganizationBilling>): Promise<void> {
    // TODO: Implement database storage
    // For now, just log the update
    console.log('Updating organization billing:', billing);
    
    // This would typically update your database:
    // await db.organizationBilling.upsert({
    //   where: { organizationId: billing.organizationId },
    //   update: billing,
    //   create: { ...billing, createdAt: new Date() }
    // });
  }
}

export const stripeWebhookHandler = new StripeWebhookHandler();