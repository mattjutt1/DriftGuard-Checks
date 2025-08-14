import React, { useState } from 'react';
import { PLAN_CONFIGS, BillingPlan } from '../types';

interface PlanSelectorProps {
  currentPlan?: BillingPlan;
  onSelectPlan: (plan: BillingPlan, interval: 'monthly' | 'annual') => void;
  organizationId: number;
  organizationLogin: string;
}

export const PlanSelector: React.FC<PlanSelectorProps> = ({
  currentPlan,
  onSelectPlan,
  organizationId,
  organizationLogin
}) => {
  const [billingInterval, setBillingInterval] = useState<'monthly' | 'annual'>('monthly');

  const formatPrice = (cents: number, interval: 'monthly' | 'annual' = 'monthly') => {
    if (interval === 'annual') {
      return `$${(cents / 100 / 12).toFixed(0)}`;
    }
    return `$${(cents / 100).toFixed(0)}`;
  };

  const getAnnualSavings = (plan: typeof PLAN_CONFIGS[BillingPlan]) => {
    if (!plan.annualPrice) return 0;
    const monthlyTotal = plan.price * 12;
    return monthlyTotal - plan.annualPrice;
  };

  const getPlanRecommendation = (planId: BillingPlan) => {
    switch (planId) {
      case 'starter':
        return 'Perfect for small teams getting started';
      case 'team':
        return 'Most popular for growing teams';
      case 'enterprise':
        return 'Best for large organizations';
      default:
        return '';
    }
  };

  const isPlanPopular = (planId: BillingPlan) => {
    return planId === 'team';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Choose Your Plan
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Select the perfect plan for {organizationLogin}
        </p>
        
        {/* Billing Interval Toggle */}
        <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
          <button
            onClick={() => setBillingInterval('monthly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingInterval === 'monthly'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingInterval('annual')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingInterval === 'annual'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Annual
            <span className="ml-1 text-green-600 text-xs">Save up to 17%</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.values(PLAN_CONFIGS).map((plan) => {
          const isCurrentPlan = currentPlan === plan.id;
          const isPopular = isPlanPopular(plan.id);
          const hasAnnualPricing = plan.annualPrice && billingInterval === 'annual';
          const displayPrice = hasAnnualPricing ? plan.annualPrice : plan.price;
          const savings = getAnnualSavings(plan);

          return (
            <div
              key={plan.id}
              className={`relative rounded-lg border p-6 transition-all hover:border-blue-300 ${
                isCurrentPlan
                  ? 'border-blue-500 bg-blue-50'
                  : isPopular
                  ? 'border-blue-200 shadow-lg'
                  : 'border-gray-200'
              }`}
            >
              {/* Popular Badge */}
              {isPopular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    Most Popular
                  </span>
                </div>
              )}

              {/* Current Plan Badge */}
              {isCurrentPlan && (
                <div className="absolute -top-3 right-4">
                  <span className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    Current Plan
                  </span>
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                
                {plan.id === 'free' ? (
                  <div className="mb-2">
                    <span className="text-3xl font-bold text-gray-900">Free</span>
                  </div>
                ) : (
                  <div className="mb-2">
                    <span className="text-3xl font-bold text-gray-900">
                      {formatPrice(displayPrice, billingInterval)}
                    </span>
                    <span className="text-gray-500 ml-1">
                      /{billingInterval === 'annual' ? 'month' : 'month'}
                    </span>
                  </div>
                )}

                {billingInterval === 'annual' && savings > 0 && (
                  <p className="text-sm text-green-600 font-medium">
                    Save ${(savings / 100).toFixed(0)} per year
                  </p>
                )}

                {getPlanRecommendation(plan.id) && (
                  <p className="text-sm text-gray-600 mt-2">
                    {getPlanRecommendation(plan.id)}
                  </p>
                )}
              </div>

              {/* Plan Limits */}
              <div className="mb-6 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Repositories</span>
                  <span className="font-medium">
                    {plan.limits.repositories === Infinity ? 'Unlimited' : plan.limits.repositories}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">PR Analyses/month</span>
                  <span className="font-medium">
                    {plan.limits.monthlyPRs === Infinity ? 'Unlimited' : plan.limits.monthlyPRs.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">History</span>
                  <span className="font-medium">{plan.limits.historyDays} days</span>
                </div>
              </div>

              {/* Plan Features */}
              <div className="mb-6">
                <ul className="space-y-2">
                  {plan.features.slice(0, 5).map((feature, index) => (
                    <li key={index} className="flex items-start text-sm">
                      <svg className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                  {plan.features.length > 5 && (
                    <li className="text-sm text-gray-500 ml-6">
                      +{plan.features.length - 5} more features
                    </li>
                  )}
                </ul>
              </div>

              {/* CTA Button */}
              <div>
                {isCurrentPlan ? (
                  <button
                    disabled
                    className="w-full py-2 px-4 bg-gray-100 text-gray-500 rounded-lg font-medium cursor-not-allowed"
                  >
                    Current Plan
                  </button>
                ) : plan.id === 'free' ? (
                  <button
                    onClick={() => onSelectPlan(plan.id, billingInterval)}
                    className="w-full py-2 px-4 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  >
                    Downgrade to Free
                  </button>
                ) : (
                  <button
                    onClick={() => onSelectPlan(plan.id, billingInterval)}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                      isPopular
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-900 text-white hover:bg-gray-800'
                    }`}
                  >
                    {currentPlan && plan.price > PLAN_CONFIGS[currentPlan].price
                      ? 'Upgrade'
                      : currentPlan && plan.price < PLAN_CONFIGS[currentPlan].price
                      ? 'Downgrade'
                      : 'Select'
                    } {plan.name}
                  </button>
                )}
              </div>

              {/* Enterprise Contact */}
              {plan.id === 'enterprise' && (
                <p className="text-xs text-gray-500 text-center mt-2">
                  Contact sales for custom pricing
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Feature Comparison Link */}
      <div className="text-center mt-8">
        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
          Compare all features →
        </button>
      </div>

      {/* FAQ Section */}
      <div className="mt-12 bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Frequently Asked Questions
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">
              Can I change plans anytime?
            </h4>
            <p className="text-sm text-gray-600">
              Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">
              What happens if I exceed my limits?
            </h4>
            <p className="text-sm text-gray-600">
              Free plans have hard limits. Paid plans allow overages with additional charges at $0.10/PR and $20/repo per month.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">
              Do you offer annual billing?
            </h4>
            <p className="text-sm text-gray-600">
              Yes, annual billing saves you 2 months (17% discount) and is available for all paid plans.
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">
              Is there a free trial?
            </h4>
            <p className="text-sm text-gray-600">
              All paid plans include a 14-day free trial. No credit card required to start.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanSelector;