# DriftGuard Billing Integration

## Overview

Complete monetization infrastructure for DriftGuard GitHub App with Stripe integration, usage tracking, and subscription management.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub App    │────│ Billing Engine   │────│   Stripe API    │
│   (Probot)      │    │ (Usage Tracking) │    │ (Subscriptions) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────────────┐               │
         └──────────────│ Enforcement     │───────────────┘
                        │ Middleware      │
                        └─────────────────┘
```

## Components

### 1. Core Types (`src/billing/types.ts`)
- **Plan Configurations**: Free, Starter ($99), Team ($299), Enterprise ($999+)
- **Usage Metrics**: Repository count, PR analysis tracking
- **Billing Data**: Subscription status, customer information
- **Overage Pricing**: $0.10/PR, $20/repository per month

### 2. Stripe Integration (`src/billing/stripe-client.ts`)
- **Product Management**: Automatic product/price sync
- **Customer Management**: Create customers, subscriptions
- **Checkout Sessions**: Subscription signup flow
- **Portal Sessions**: Customer self-service

### 3. Usage Tracking (`src/billing/usage-tracker.ts`)
- **Real-time Tracking**: PR analysis, repository counts
- **Limit Enforcement**: Plan-based usage limits
- **Overage Calculation**: Automatic billing for overages
- **Dashboard Data**: Usage insights and recommendations

### 4. Webhook Handler (`src/billing/webhook-handler.ts`)
- **Subscription Events**: Created, updated, deleted
- **Payment Events**: Success, failed, trial ending
- **Data Sync**: Keep billing status current
- **Notifications**: Alert on payment issues

### 5. GitHub Integration (`src/billing/github-integration.ts`)
- **Enforcement Middleware**: Block analysis when limits reached
- **Check Run Creation**: Billing messages in PR checks
- **Usage Recording**: Track every PR analysis
- **Upgrade Prompts**: Clear upgrade paths

### 6. UI Components (`src/billing/ui/`)
- **Billing Dashboard**: Usage overview, plan details
- **Plan Selector**: Upgrade/downgrade interface
- **React Components**: TypeScript, responsive design

## Plan Structure

| Plan | Price | Repositories | PRs/Month | Features |
|------|-------|-------------|-----------|----------|
| **Free** | $0 | 1 | 100 | Basic checks, 7-day history |
| **Starter** | $99 | 5 | 500 | Slack integration, 90-day history |
| **Team** | $299 | 25 | 2,000 | SSO, audit logs, API access |
| **Enterprise** | $999+ | Unlimited | Unlimited | Custom policies, on-premise |

## Usage-Based Billing

### Overage Charges
- **Additional PRs**: $0.10 per PR over plan limit
- **Additional Repositories**: $20/month per repository over limit

### Enforcement Strategy
- **Free Plan**: Hard limits (analysis blocked when exceeded)
- **Paid Plans**: Soft limits with overage billing
- **Grace Period**: 24-hour grace before enforcement

## Integration Points

### Environment Variables
```bash
# Required
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
APP_URL=https://your-domain.com

# Optional
STRIPE_WEBHOOK_SECRET=whsec_...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ENFORCE_BILLING=true
```

### API Endpoints
- `POST /webhooks/stripe` - Stripe webhook handler
- `GET /api/billing/plans` - Available plans
- `GET /api/billing/usage/:orgId` - Usage dashboard
- `GET /health` - Health check with billing metrics

### Scripts
- `npm run billing:sync` - Sync Stripe products
- `npm run billing:verify` - Validate configuration
- `npm run test:billing` - Run billing tests
- `npm run start:billing` - Start with billing enabled

## Development Setup

### 1. Install Dependencies
```bash
npm install stripe @types/stripe
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your Stripe credentials
```

### 3. Sync Stripe Products
```bash
npm run billing:sync
```

### 4. Start Development Server
```bash
npm run start:billing
```

### 5. Run Tests
```bash
npm run test:billing
```

## Production Deployment

### 1. Stripe Configuration
- Create products in Stripe Dashboard (or use sync script)
- Set up webhook endpoint: `https://your-domain.com/webhooks/stripe`
- Configure webhook events:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
  - `customer.subscription.trial_will_end`

### 2. Database Setup (Optional)
For persistent billing data, set up PostgreSQL:
```sql
CREATE TABLE organization_billing (
  organization_id INTEGER PRIMARY KEY,
  github_organization_login VARCHAR NOT NULL,
  plan VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  stripe_customer_id VARCHAR,
  stripe_subscription_id VARCHAR,
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  trial_end TIMESTAMP,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  billing_email VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_metrics (
  organization_id INTEGER,
  month VARCHAR,
  repository_count INTEGER DEFAULT 0,
  pr_analysis_count INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (organization_id, month)
);
```

### 3. GitHub App Configuration
Update GitHub App manifest to include billing permissions:
```yaml
default_permissions:
  contents: read
  metadata: read
  pull_requests: write
  checks: write
  organization_administration: read  # For billing
```

### 4. Monitoring Setup
- Track billing webhook success/failure rates
- Monitor usage tracking accuracy
- Set up alerts for payment failures
- Track subscription churn and upgrades

## Testing

### Unit Tests
```bash
npm run test:billing
```

Tests cover:
- Plan configuration validation
- Usage tracking accuracy
- Overage calculation logic
- Billing enforcement rules

### Integration Tests
```bash
npm run billing:verify
```

Validates:
- Stripe API connectivity
- Webhook endpoint configuration
- Product/price synchronization
- Environment variable setup

### Manual Testing

#### Test Cards (Stripe Test Mode)
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0000 0000 3220`

#### Test Scenarios
1. **Free Plan Limits**: Create 101 PRs, verify blocking
2. **Paid Plan Overages**: Exceed limits, verify overage billing
3. **Subscription Changes**: Upgrade/downgrade plans
4. **Payment Failures**: Test dunning management
5. **Trial Expiration**: Test trial-to-paid conversion

## Security Considerations

### Webhook Verification
- Always verify Stripe webhook signatures
- Use `STRIPE_WEBHOOK_SECRET` in production
- Implement idempotency for webhook processing

### Data Protection
- Never log payment method details
- Encrypt sensitive billing data at rest
- Use HTTPS for all billing-related communications
- Implement proper access controls for billing data

### Error Handling
- Graceful degradation when Stripe is unavailable
- Retry logic for failed API calls
- Proper error messages for users
- Detailed logging for debugging

## Marketplace Integration

### GitHub Marketplace Billing
When ready for marketplace:
1. Configure marketplace billing in GitHub App settings
2. Implement marketplace webhook handlers
3. Sync pricing with GitHub's requirements
4. Test marketplace billing flow

### Revenue Sharing
- GitHub takes 5% of marketplace revenue
- Direct billing (via Stripe) retains 100% revenue
- Consider hybrid approach for different customer segments

## Monitoring & Analytics

### Key Metrics
- **Conversion Rate**: Free to paid
- **Churn Rate**: Monthly subscription cancellations
- **Usage Growth**: PR analysis volume trends
- **Revenue Growth**: Monthly recurring revenue
- **Support Load**: Billing-related tickets

### Dashboards
- Stripe Dashboard: Revenue, customers, failed payments
- Application Metrics: Usage patterns, enforcement actions
- GitHub Insights: App installation and usage data

## Support & Troubleshooting

### Common Issues

**"Billing limit reached"**
- Check current usage vs plan limits
- Verify subscription status in Stripe
- Review recent webhook deliveries

**"Payment failed"**
- Check payment method in Stripe
- Review dunning management settings
- Verify customer communication preferences

**"Usage not tracking"**
- Verify webhook delivery success
- Check application logs for errors
- Validate GitHub App permissions

### Customer Support Workflows
1. **Usage Questions**: Direct to billing dashboard
2. **Payment Issues**: Stripe customer portal
3. **Plan Changes**: Self-service via UI
4. **Technical Issues**: Application logs + Stripe events

## Future Enhancements

### Planned Features
- **Team Management**: Per-seat billing for large teams
- **Custom Policies**: Enterprise policy development
- **Analytics Dashboard**: Advanced usage analytics
- **API Rate Limiting**: Usage-based API throttling
- **Multi-Currency**: International pricing support

### Integration Opportunities
- **Slack App**: Usage notifications and billing alerts
- **Microsoft Teams**: Enterprise integration
- **Jira/Linear**: Ticket-based usage tracking
- **Datadog/New Relic**: Advanced monitoring integration

---

## Quick Start Commands

```bash
# Development
npm run start:billing

# Production Setup
npm run billing:sync
npm run billing:verify

# Testing
npm run test:billing

# Monitoring
curl https://your-domain.com/health
curl https://your-domain.com/metrics
```

## Support

For billing system issues:
1. Check application logs
2. Review Stripe webhook delivery logs
3. Run `npm run billing:verify`
4. Contact support with organization ID and timestamp