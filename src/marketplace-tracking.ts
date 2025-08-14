import { analytics } from '@mmtu/analytics'

/**
 * GitHub Marketplace Tracking Integration
 * Tracks the complete funnel: marketplace_view → install_clicked → install_success → first_run → retention
 */

export class MarketplaceTracker {

  /**
   * Track marketplace listing view
   * Called when users visit the DriftGuard GitHub Marketplace page
   */
  trackMarketplaceView(source: string): void {
    const trackingSource = this.normalizeSource(source)
    
    analytics.marketplaceView({
      source: trackingSource,
      app_id: 'driftguard_checks'
    })
    
    console.log(`👁️ Marketplace view tracked: ${trackingSource}`)
  }

  /**
   * Track install button click
   * Called when users click "Install" on the marketplace listing
   */
  trackInstallClicked(source: string): void {
    const trackingSource = this.normalizeSource(source)
    
    analytics.installClicked({
      source: trackingSource, 
      app_id: 'driftguard_checks'
    })
    
    console.log(`🖱️ Install clicked: ${trackingSource}`)
  }

  /**
   * Initialize marketplace tracking
   * Sets up tracking for marketplace page interactions
   */
  initializeMarketplaceTracking(): void {
    if (typeof window === 'undefined') return
    
    // Track marketplace view on page load
    const referrer = document.referrer
    const urlParams = new URLSearchParams(window.location.search)
    const utmSource = urlParams.get('utm_source') || 'direct_link'
    
    this.trackMarketplaceView(utmSource)
    
    // Track install button clicks
    const installButtons = document.querySelectorAll('[data-track="install-click"]')
    installButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.trackInstallClicked(utmSource)
      })
    })
    
    // Track repository selection changes
    const repoSelectors = document.querySelectorAll('[data-track="repo-select"]')
    repoSelectors.forEach(selector => {
      selector.addEventListener('change', (event) => {
        const target = event.target as HTMLSelectElement
        this.trackRepositorySelection(parseInt(target.value) || 0)
      })
    })
    
    console.log('🎯 Marketplace tracking initialized')
  }

  /**
   * Track repository selection during install
   */
  private trackRepositorySelection(repoCount: number): void {
    console.log(`📂 Repository selection: ${repoCount} repos selected`)
    
    // Could enhance with additional analytics events for funnel analysis
    if (repoCount > 10) {
      console.log('📊 Large installation detected (>10 repos)')
    }
  }

  /**
   * Normalize traffic sources for consistent tracking
   */
  private normalizeSource(source: string): 'marketplace_search' | 'marketplace_browse' | 'direct_link' | 'github_notification' | 'referral' {
    const lowerSource = source.toLowerCase()
    
    if (lowerSource.includes('search')) return 'marketplace_search'
    if (lowerSource.includes('browse') || lowerSource.includes('category')) return 'marketplace_browse'
    if (lowerSource.includes('github') || lowerSource.includes('notification')) return 'github_notification'
    if (lowerSource.includes('referral') || lowerSource.includes('ref')) return 'referral'
    
    return 'direct_link'
  }

  /**
   * Get funnel conversion metrics
   * Useful for analyzing marketplace performance
   */
  async getFunnelMetrics(installationId?: number): Promise<{
    marketplace_views: number
    install_clicks: number
    install_success: number
    first_run_completion: number
    day_7_retention: number
    day_30_retention: number
  }> {
    // In production, this would query PostHog or analytics database
    // Mock data for testing
    return {
      marketplace_views: 1000,
      install_clicks: 150,
      install_success: 120,
      first_run_completion: 95,
      day_7_retention: 70,
      day_30_retention: 45
    }
  }

  /**
   * Generate marketplace performance report
   */
  async generateMarketplaceReport(): Promise<{
    funnel_conversion_rate: number
    install_to_first_run_rate: number
    retention_7d_rate: number
    retention_30d_rate: number
    top_traffic_sources: string[]
  }> {
    const metrics = await this.getFunnelMetrics()
    
    return {
      funnel_conversion_rate: (metrics.install_success / metrics.marketplace_views) * 100,
      install_to_first_run_rate: (metrics.first_run_completion / metrics.install_success) * 100,
      retention_7d_rate: (metrics.day_7_retention / metrics.install_success) * 100,
      retention_30d_rate: (metrics.day_30_retention / metrics.install_success) * 100,
      top_traffic_sources: ['marketplace_search', 'github_notification', 'referral']
    }
  }

  /**
   * A/B test marketplace messaging
   * Track different messaging variants for optimization
   */
  trackMarketplaceVariant(variant: 'control' | 'security_focused' | 'developer_friendly'): void {
    console.log(`🧪 Marketplace variant exposed: ${variant}`)
    
    // Would track variant exposure for A/B testing
    // analytics.marketplaceVariantExposed({ variant, app_id: 'driftguard_checks' })
  }
}

// Marketplace tracking utilities
export class FunnelAnalyzer {
  
  /**
   * Calculate funnel drop-off points
   */
  static calculateDropoffs(funnelData: {
    step: string
    users: number
  }[]): { step: string; dropoff_rate: number }[] {
    const dropoffs = []
    
    for (let i = 1; i < funnelData.length; i++) {
      const current = funnelData[i]
      const previous = funnelData[i - 1]
      
      const dropoffRate = ((previous.users - current.users) / previous.users) * 100
      
      dropoffs.push({
        step: `${previous.step} → ${current.step}`,
        dropoff_rate: Math.round(dropoffRate * 100) / 100
      })
    }
    
    return dropoffs
  }

  /**
   * Identify high-value user segments
   */
  static segmentUsers(installationData: Array<{
    installation_id: number
    repository_count: number
    organization_type: string
    retention_7d: boolean
    retention_30d: boolean
  }>): {
    high_value: number
    medium_value: number
    low_value: number
  } {
    let highValue = 0, mediumValue = 0, lowValue = 0
    
    installationData.forEach(install => {
      const score = 
        (install.repository_count > 5 ? 2 : 0) +
        (install.retention_7d ? 2 : 0) +
        (install.retention_30d ? 3 : 0) +
        (install.organization_type === 'enterprise' ? 2 : 0)
      
      if (score >= 7) highValue++
      else if (score >= 4) mediumValue++
      else lowValue++
    })
    
    return { high_value: highValue, medium_value: mediumValue, low_value: lowValue }
  }
}

export const marketplaceTracker = new MarketplaceTracker()