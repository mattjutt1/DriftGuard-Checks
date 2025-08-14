import React, { useState, useEffect } from 'react';
import { PLAN_CONFIGS, BillingPlan, OrganizationBilling } from '../types';

interface UsageDashboardData {
  current: {
    organizationId: number;
    month: string;
    repositoryCount: number;
    prAnalysisCount: number;
    lastUpdated: string;
  } | null;
  planLimits: {
    repositories: number;
    monthlyPRs: number;
    historyDays: number;
    customPolicies: boolean;
    apiAccess: boolean;
    ssoIntegration: boolean;
    auditLogs: boolean;
    prioritySupport: boolean;
  };
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
}

interface BillingDashboardProps {
  organizationId: number;
  organizationLogin: string;
  billing: OrganizationBilling;
  onUpgrade?: (newPlan: BillingPlan) => void;
  onManageSubscription?: () => void;
}

export const BillingDashboard: React.FC<BillingDashboardProps> = ({
  organizationId,
  organizationLogin,
  billing,
  onUpgrade,
  onManageSubscription
}) => {
  const [usageData, setUsageData] = useState<UsageDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentPlan = PLAN_CONFIGS[billing.plan];

  useEffect(() => {
    fetchUsageData();
  }, [organizationId]);

  const fetchUsageData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/billing/usage/${organizationId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch usage data');
      }
      
      const data = await response.json();
      setUsageData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'trialing': return 'text-blue-600';
      case 'past_due': return 'text-yellow-600';
      case 'canceled': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'Active';
      case 'trialing': return 'Trial';
      case 'past_due': return 'Past Due';
      case 'canceled': return 'Canceled';
      case 'unpaid': return 'Unpaid';
      default: return status;
    }
  };

  const formatPrice = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const renderUsageBar = (label: string, current: number, limit: number, unit: string) => {
    const percentage = limit === Infinity ? 0 : Math.min(100, (current / limit) * 100);
    const isOverLimit = current > limit && limit !== Infinity;
    
    return (
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="font-medium">{label}</span>
          <span className={isOverLimit ? 'text-red-600 font-semibold' : 'text-gray-600'}>
            {current.toLocaleString()} / {limit === Infinity ? '∞' : limit.toLocaleString()} {unit}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(percentage)}`}
            style={{ width: `${Math.min(100, percentage)}%` }}
          />
        </div>
        {isOverLimit && (
          <p className="text-red-600 text-xs mt-1">
            Overage: {(current - limit).toLocaleString()} {unit}
          </p>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading billing data: {error}</p>
        <button 
          onClick={fetchUsageData}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Billing Dashboard</h1>
            <p className="text-gray-600 mt-1">Organization: {organizationLogin}</p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Status:</span>
              <span className={`font-semibold ${getStatusColor(billing.status)}`}>
                {getStatusLabel(billing.status)}
              </span>
            </div>
            {billing.currentPeriodEnd && (
              <p className="text-sm text-gray-500 mt-1">
                Next billing: {new Date(billing.currentPeriodEnd).toLocaleDateString()}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Current Plan */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Current Plan</h2>
          {onManageSubscription && billing.stripeCustomerId && (
            <button
              onClick={onManageSubscription}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Manage Subscription
            </button>
          )}
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium text-blue-600 mb-2">
              {currentPlan.name} Plan
            </h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">
              {formatPrice(currentPlan.price)}
              <span className="text-lg font-normal text-gray-500">/month</span>
            </p>
            {currentPlan.annualPrice && (
              <p className="text-sm text-green-600">
                Save {formatPrice((currentPlan.price * 12) - currentPlan.annualPrice)} with annual billing
              </p>
            )}
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Plan Features</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              {currentPlan.features.slice(0, 4).map((feature, index) => (
                <li key={index} className="flex items-center">
                  <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Usage Statistics */}
      {usageData && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Usage This Month</h2>
          
          {usageData.current ? (
            <div className="space-y-4">
              {renderUsageBar(
                'Repositories', 
                usageData.current.repositoryCount, 
                usageData.planLimits.repositories,
                'repos'
              )}
              
              {renderUsageBar(
                'PR Analyses', 
                usageData.current.prAnalysisCount, 
                usageData.planLimits.monthlyPRs,
                'PRs'
              )}
              
              {usageData.overageCharges.totalOverage > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                  <h3 className="font-medium text-yellow-800 mb-2">Overage Charges</h3>
                  <div className="text-sm text-yellow-700 space-y-1">
                    {usageData.overageCharges.prOverage > 0 && (
                      <p>PR Analysis Overage: {formatPrice(usageData.overageCharges.prOverage)}</p>
                    )}
                    {usageData.overageCharges.repositoryOverage > 0 && (
                      <p>Repository Overage: {formatPrice(usageData.overageCharges.repositoryOverage)}</p>
                    )}
                    <p className="font-semibold">
                      Total Additional Charges: {formatPrice(usageData.overageCharges.totalOverage)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">No usage data available for this month.</p>
          )}
        </div>
      )}

      {/* Recommendations */}
      {usageData?.recommendations && usageData.recommendations.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Recommendations</h2>
          <ul className="space-y-2">
            {usageData.recommendations.map((recommendation, index) => (
              <li key={index} className="flex items-start text-blue-800">
                <svg className="w-5 h-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Upgrade Options */}
      {billing.plan !== 'enterprise' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Upgrade Options</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(PLAN_CONFIGS)
              .filter(plan => plan.id !== 'free' && plan.id !== billing.plan)
              .map(plan => (
                <div key={plan.id} className="border rounded-lg p-4 hover:border-blue-300 transition-colors">
                  <h3 className="font-medium text-lg mb-2">{plan.name}</h3>
                  <p className="text-2xl font-bold text-blue-600 mb-2">
                    {formatPrice(plan.price)}
                    <span className="text-sm font-normal text-gray-500">/month</span>
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1 mb-4">
                    <li>Up to {plan.limits.repositories === Infinity ? 'unlimited' : plan.limits.repositories} repositories</li>
                    <li>{plan.limits.monthlyPRs === Infinity ? 'Unlimited' : plan.limits.monthlyPRs.toLocaleString()} PRs/month</li>
                    <li>{plan.limits.historyDays} days history</li>
                  </ul>
                  {onUpgrade && (
                    <button
                      onClick={() => onUpgrade(plan.id)}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Upgrade to {plan.name}
                    </button>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BillingDashboard;