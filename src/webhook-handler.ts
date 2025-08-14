import { analytics } from '@mmtu/analytics'

/**
 * GitHub App Webhook Handler for DriftGuard
 * Tracks marketplace install → first_run → retention funnel
 */

export interface GitHubInstallationPayload {
  action: 'created' | 'deleted' | 'suspend' | 'unsuspend'
  installation: {
    id: number
    account: {
      login: string
      type: 'Organization' | 'User'
    }
    repository_selection: 'selected' | 'all'
    repositories?: Array<{ name: string; full_name: string }>
  }
  repositories?: Array<{ name: string; full_name: string }>
}

export interface PullRequestPayload {
  action: 'opened' | 'synchronize' | 'closed'
  installation: { id: number }
  repository: {
    name: string
    full_name: string 
    language: string | null
  }
  pull_request: {
    number: number
    head: { sha: string }
  }
}

export class DriftGuardWebhookHandler {
  
  /**
   * Handle GitHub App installation events
   */
  async handleInstallation(payload: GitHubInstallationPayload): Promise<void> {
    const { action, installation } = payload
    
    if (action === 'created') {
      // Track successful install
      analytics.installSuccess({
        app_id: 'driftguard_checks',
        installation_id: installation.id,
        repository_count: payload.repositories?.length || 0,
        organization_type: this.hashOrganization(installation.account.login)
      })
      
      // Schedule retention tracking
      await this.scheduleRetentionChecks(installation.id)
      
      console.log(`✅ DriftGuard installed for ${installation.account.login} (${installation.id})`)
      
    } else if (action === 'deleted') {
      // Track uninstall attempt
      const daysInstalled = await this.getDaysInstalled(installation.id)
      const issuesResolved = await this.getIssuesResolved(installation.id)
      
      analytics.uninstallAttempted({
        app_id: 'driftguard_checks',
        installation_id: installation.id,
        days_since_install: daysInstalled,
        issues_resolved_total: issuesResolved
      })
      
      console.log(`❌ DriftGuard uninstalled for ${installation.account.login} after ${daysInstalled} days`)
    }
  }

  /**
   * Handle pull request events (first run detection)
   */
  async handlePullRequest(payload: PullRequestPayload): Promise<void> {
    const { action, installation, repository, pull_request } = payload
    
    if (action === 'opened' || action === 'synchronize') {
      // Check if this is first run for this installation
      const isFirstRun = await this.isFirstRun(installation.id)
      
      if (isFirstRun) {
        // Simulate running checks
        const checkResults = await this.runSecurityChecks(repository.full_name, pull_request.head.sha)
        
        analytics.firstRunCompleted({
          app_id: 'driftguard_checks',
          installation_id: installation.id,
          checks_run: checkResults.checksRun,
          issues_found: checkResults.issuesFound,
          runtime_seconds: checkResults.runtimeSeconds,
          repository_language: repository.language || 'unknown'
        })
        
        // Mark as no longer first run
        await this.markFirstRunComplete(installation.id)
        
        console.log(`🎯 First run complete for installation ${installation.id}: ${checkResults.issuesFound} issues found`)
      }
      
      // Regular check run analytics would go here
    }
  }

  /**
   * Handle configuration updates
   */
  async handleConfigUpdate(installationId: number, config: any): Promise<void> {
    const keyset = this.determineKeyset(config)
    
    analytics.configSaved({
      keyset,
      checks_enabled: config.checksEnabled?.length || 0,
      custom_rules: config.customRules?.length > 0,
      installation_id: installationId
    })
    
    console.log(`⚙️ Config updated for installation ${installationId}: ${keyset}`)
  }

  /**
   * Schedule retention tracking webhooks
   */
  private async scheduleRetentionChecks(installationId: number): Promise<void> {
    // In production, this would use a job queue (GitHub Actions, AWS Lambda, etc.)
    console.log(`📅 Scheduling retention checks for installation ${installationId}`)
    
    // Mock scheduling - would integrate with actual scheduler
    setTimeout(() => this.checkDay7Retention(installationId), 7 * 24 * 60 * 60 * 1000) // 7 days
    setTimeout(() => this.checkDay30Retention(installationId), 30 * 24 * 60 * 60 * 1000) // 30 days
  }

  /**
   * Check 7-day retention
   */
  private async checkDay7Retention(installationId: number): Promise<void> {
    const stats = await this.getRetentionStats(installationId, 7)
    
    analytics.day7Retention({
      app_id: 'driftguard_checks',
      installation_id: installationId,
      checks_run_week: stats.checksRunWeek,
      active_repositories: stats.activeRepositories,
      config_changes: stats.configChanges
    })
    
    console.log(`📊 7-day retention tracked for installation ${installationId}`)
  }

  /**
   * Check 30-day retention
   */
  private async checkDay30Retention(installationId: number): Promise<void> {
    const stats = await this.getRetentionStats(installationId, 30)
    
    analytics.day30Retention({
      app_id: 'driftguard_checks',
      installation_id: installationId,
      checks_run_month: stats.checksRunMonth,
      issues_resolved: stats.issuesResolved,
      team_size: stats.teamSize
    })
    
    console.log(`📊 30-day retention tracked for installation ${installationId}`)
  }

  // Helper methods

  private hashOrganization(orgName: string): string {
    // PII-safe organization type classification
    const orgTypes = ['enterprise', 'startup', 'oss', 'individual']
    const hash = this.simpleHash(orgName)
    return orgTypes[hash % orgTypes.length]
  }

  private simpleHash(input: string): number {
    let hash = 0
    for (let i = 0; i < input.length; i++) {
      hash = ((hash << 5) - hash + input.charCodeAt(i)) & 0xffffffff
    }
    return Math.abs(hash)
  }

  private async isFirstRun(installationId: number): Promise<boolean> {
    // Check database/storage for first run status
    // Mock: assume first run if no record exists
    return Math.random() > 0.3 // 70% chance of first run for testing
  }

  private async markFirstRunComplete(installationId: number): Promise<void> {
    // Mark in database/storage that first run is complete
    console.log(`✓ Marked first run complete for installation ${installationId}`)
  }

  private async runSecurityChecks(repoName: string, sha: string): Promise<{
    checksRun: number
    issuesFound: number 
    runtimeSeconds: number
  }> {
    // Mock security check execution
    const checksRun = Math.floor(Math.random() * 15) + 5 // 5-20 checks
    const issuesFound = Math.floor(Math.random() * 8) // 0-7 issues
    const runtimeSeconds = Math.floor(Math.random() * 45) + 15 // 15-60 seconds
    
    return { checksRun, issuesFound, runtimeSeconds }
  }

  private async getDaysInstalled(installationId: number): Promise<number> {
    // Calculate days since installation
    return Math.floor(Math.random() * 180) + 1 // 1-180 days for testing
  }

  private async getIssuesResolved(installationId: number): Promise<number> {
    // Get total issues resolved by this installation
    return Math.floor(Math.random() * 25) // 0-25 issues for testing
  }

  private determineKeyset(config: any): 'security_level_low' | 'security_level_medium' | 'security_level_high' | 'custom' {
    const checksCount = config.checksEnabled?.length || 0
    
    if (checksCount <= 5) return 'security_level_low'
    if (checksCount <= 10) return 'security_level_medium' 
    if (checksCount <= 15) return 'security_level_high'
    return 'custom'
  }

  private async getRetentionStats(installationId: number, days: number): Promise<{
    checksRunWeek?: number
    checksRunMonth?: number
    activeRepositories: number
    configChanges: number
    issuesResolved?: number
    teamSize?: number
  }> {
    // Mock retention statistics
    return {
      checksRunWeek: days === 7 ? Math.floor(Math.random() * 20) : undefined,
      checksRunMonth: days === 30 ? Math.floor(Math.random() * 100) : undefined,
      activeRepositories: Math.floor(Math.random() * 10) + 1,
      configChanges: Math.floor(Math.random() * 3),
      issuesResolved: days === 30 ? Math.floor(Math.random() * 15) : undefined,
      teamSize: days === 30 ? Math.floor(Math.random() * 20) + 1 : undefined
    }
  }
}

export const webhookHandler = new DriftGuardWebhookHandler()