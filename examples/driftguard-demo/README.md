# DriftGuard Demo Repository

## Overview

This demo showcases **Prompt Gate for GitHub** in action with a realistic golden test set. It demonstrates how prompt quality evaluation works in a real repository environment.

## What's Included

### Golden Test Set

- **High-quality prompts** that should pass evaluation (>80% threshold)
- **Low-quality prompts** that should fail evaluation (<80% threshold)
- **Edge cases** that test the evaluation system boundaries
- **Real-world examples** from different domains (coding, content, analytics)

### Demo Artifacts

- **Sample PR screenshots** showing Prompt Gate in action
- **Branch protection setup** demonstration
- **Workflow results** examples with different outcomes
- **Configuration variations** for different use cases

## Files Structure

```
examples/driftguard-demo/
├── README.md                    # This file
├── .promptops.yml               # Demo configuration
├── golden-prompts/              # Test prompt collection
│   ├── high-quality.yml         # Prompts that should pass
│   ├── low-quality.yml          # Prompts that should fail
│   ├── edge-cases.yml           # Boundary test cases
│   └── domain-specific.yml      # Domain-focused examples
├── screenshots/                 # PR and workflow screenshots
│   ├── pr-passed.png           # Successful evaluation
│   ├── pr-failed.png           # Failed evaluation
│   ├── pr-skipped.png          # Skipped evaluation
│   └── workflow-logs.png       # Detailed workflow results
└── configurations/              # Different config examples
    ├── strict.yml               # High threshold (90%)
    ├── permissive.yml           # Low threshold (70%)
    └── domain-focused.yml       # Domain-specific tests
```

## How to Use This Demo

### Method 1: Copy to Your Repository

1. **Copy the demo configuration**:

   ```bash
   cp examples/driftguard-demo/.promptops.yml .promptops.yml
   ```

2. **Install Prompt Gate workflow**:

   ```bash
   cp examples/prompt-gate.min.yml .github/workflows/prompt-gate.yml
   ```

3. **Test with demo prompts**:
   - Create a PR with changes
   - Add the `prompt-check` label
   - Watch Prompt Gate evaluate using the golden test set

### Method 2: Fork and Experiment

1. **Fork this repository**
2. **Enable branch protection** with Prompt Gate as required check
3. **Create test PRs** with different prompt modifications
4. **Observe different outcomes** based on prompt quality

## Golden Test Set Details

### High-Quality Prompts (Should Pass)

These prompts demonstrate best practices and should consistently score >80%:

- **Clear context**: Well-defined problem statements
- **Specific requirements**: Detailed output format specifications
- **Examples included**: Concrete examples of expected behavior
- **Edge case handling**: Consideration of error conditions

### Low-Quality Prompts (Should Fail)

These prompts have common issues and should score <80%:

- **Vague instructions**: Unclear or ambiguous requirements
- **Missing context**: Insufficient background information
- **No examples**: Abstract requests without concrete examples
- **Poor formatting**: Difficult to parse or understand

### Edge Cases

Boundary conditions that test evaluation system limits:

- **Minimal prompts**: Very short but potentially effective
- **Verbose prompts**: Long but potentially unfocused
- **Technical jargon**: Domain-specific language
- **Multi-step requests**: Complex workflows

## Expected Results

When running Prompt Gate with this demo configuration:

### ✅ Passing Scenarios

- **High-quality prompts**: Win rate >80%, clear pass status
- **Well-structured requests**: Professional PR comments with metrics
- **Domain-specific excellence**: Specialized prompts scoring well

### ❌ Failing Scenarios

- **Low-quality prompts**: Win rate <80%, fail status with suggestions
- **Vague requests**: Poor scores with specific improvement recommendations
- **Incomplete prompts**: Clear feedback on missing elements

### 🔇 Skipped Scenarios

- **No label**: PR without `prompt-check` label shows skip message
- **Disabled workflow**: Manual trigger only mode demonstration

## Configuration Variations

### Strict Configuration (90% threshold)

```yaml
version: '1.0'
threshold: 0.90
model: 'mock'
test_prompts: [high-quality examples only]
```

### Permissive Configuration (70% threshold)

```yaml
version: '1.0'
threshold: 0.70
model: 'mock'
test_prompts: [mixed quality examples]
```

### Domain-Focused Configuration

```yaml
version: '1.0'
threshold: 0.80
model: 'mock'
test_prompts: [domain-specific examples]
```

## Demo Screenshots

The `screenshots/` directory contains examples of:

1. **Successful Evaluation**: Green check, passing metrics, artifact links
2. **Failed Evaluation**: Red X, failing metrics, improvement suggestions
3. **Skipped Evaluation**: Neutral status, label requirement message
4. **Workflow Logs**: Detailed execution results and timing

## Using This for Training

This demo is perfect for:

- **Team onboarding**: Show new team members how Prompt Gate works
- **Quality standards**: Demonstrate what constitutes good vs. poor prompts
- **Process documentation**: Evidence of automated quality gates in action
- **Stakeholder demos**: Visual proof of concept for management

## Customization

To adapt this demo for your organization:

1. **Replace test prompts** with examples from your domain
2. **Adjust threshold** based on your quality standards
3. **Add domain-specific** evaluation criteria
4. **Include organization-specific** prompt templates

## Support

If you have questions about this demo:

1. Review the [installation guide](../../docs/install.md)
2. Check the [troubleshooting section](../../docs/install.md#troubleshooting)
3. Open an issue in the [main repository](https://github.com/mattjutt1/prompt-wizard/issues)

---

**Ready to see Prompt Gate in action? This demo provides everything you need to evaluate automated prompt quality gates in your environment.** 🎯
