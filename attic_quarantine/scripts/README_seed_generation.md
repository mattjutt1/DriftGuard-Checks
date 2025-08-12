# PromptWizard Seed Pair Generation

This script integrates Microsoft's PromptWizard framework to generate high-quality prompt optimization training pairs for PromptEvolver 3.0.

## Features

- **Microsoft PromptWizard Integration**: Uses the official PromptWizard framework for systematic prompt optimization
- **Domain-Specific Generation**: Supports Analytics, Coding, Content, and Cross-Domain categories
- **Quality Validation**: Comprehensive quality scoring and validation against our schema
- **Batch Processing**: Efficient batch processing with progress tracking
- **Checkpoint System**: Resumable generation with automatic checkpointing
- **Multiple Backends**: Supports both Ollama (local) and API-based generation
- **Error Handling**: Robust error handling with detailed logging
- **Statistics Reporting**: Comprehensive generation statistics and quality metrics

## Requirements

### Dependencies
```bash
pip install jsonschema tqdm pyyaml aiohttp
```

### Optional: PromptWizard Framework
The script automatically detects if Microsoft PromptWizard is available. If not found, it uses a standalone generation mode with Ollama.

### Optional: Ollama Setup
For local generation, ensure Ollama is running with Qwen2.5:7B model:
```bash
ollama pull qwen2.5:7b
ollama serve
```

## Usage

### Generate pairs for a specific domain
```bash
python scripts/generate_seed_pairs.py --domain Analytics --count 100
```

### Generate pairs for all domains
```bash
python scripts/generate_seed_pairs.py --all-domains --pairs-per-domain 50
```

### Resume from checkpoint
```bash
python scripts/generate_seed_pairs.py --resume --domain Coding --count 200
```

### Custom configuration
```bash
python scripts/generate_seed_pairs.py --config-path configs/my_config.yaml --domain Content
```

### Disable checkpointing
```bash
python scripts/generate_seed_pairs.py --domain Analytics --no-checkpoint
```

## Command Line Options

- `--domain {Analytics,Coding,Content,Cross-Domain}`: Specific domain to generate pairs for
- `--count INTEGER`: Number of pairs to generate (default: 100)
- `--all-domains`: Generate pairs for all domains
- `--pairs-per-domain INTEGER`: Pairs per domain when using --all-domains (default: 100)
- `--batch-size INTEGER`: Batch size for processing (default: 20)
- `--output-dir PATH`: Output directory for generated pairs
- `--config-path PATH`: Path to PromptWizard configuration file
- `--no-checkpoint`: Disable checkpoint system
- `--resume`: Resume from existing checkpoint
- `--verbose`: Enable verbose logging

## Output Structure

### Generated Files
```
data/generated/
├── analytics/
│   ├── seed_pairs_analytics_20250107_143022.json
│   └── seed_pairs_analytics_batch_1_20250107_143015.json
├── coding/
│   └── seed_pairs_coding_20250107_143045.json
├── content/
│   └── seed_pairs_content_20250107_143112.json
├── cross_domain/
│   └── seed_pairs_cross_domain_20250107_143140.json
├── checkpoints/
│   ├── checkpoint_analytics_1736267402.json
│   └── checkpoint_coding_1736267445.json
└── generation_statistics_20250107_143155.json
```

### Output Format
Each generated file follows this structure:
```json
{
  "metadata": {
    "domain": "Analytics",
    "generation_method": "ollama",
    "pairs_count": 100,
    "generation_timestamp": 1736267402,
    "generator_version": "1.0",
    "schema_version": "1.0",
    "promptwizard_config": {...}
  },
  "pairs": [
    {
      "originalPrompt": "Analyze the data",
      "enhancedPrompt": "As a senior business analyst...",
      "domain": "Analytics",
      "metadata": {
        "qualityScore": {...},
        "improvementAreas": [...],
        "processingTimestamp": 1736267402,
        "expertIdentity": "Analytics Specialist",
        "optimizationConfig": {...},
        "reasoning": "..."
      },
      "followUpQuestions": [...],
      "tags": [...],
      "version": "1.0"
    }
  ]
}
```

## Quality Assurance

### Quality Metrics
- **Overall Quality Score**: Composite score (0.0-1.0)
- **Clarity**: How clear and unambiguous the prompt is
- **Specificity**: Level of detail and precision
- **Engagement**: How motivating and engaging the prompt is
- **Structure**: Organization and logical flow
- **Completeness**: Comprehensive requirements coverage
- **Error Prevention**: How well it prevents mistakes

### Validation Criteria
- Enhanced prompt must be at least 1.2x longer than original
- Overall quality score must be ≥0.65
- Must pass JSON schema validation
- Must include meaningful improvement areas
- Must have appropriate domain classification

## Configuration

### PromptWizard Configuration
The script uses a YAML configuration file compatible with Microsoft PromptWizard:

```yaml
prompt_technique_name: "critique_n_refine"
mutate_refine_iterations: 3
mutation_rounds: 3  
temperature: 0.7
generate_reasoning: true
generate_expert_identity: true
```

See `configs/promptwizard_example.yaml` for a complete example.

### Default Configuration
If no configuration file is specified, the script creates a default configuration optimized for prompt pair generation.

## Testing

Run the test script to verify functionality:
```bash
python test_seed_generation.py
```

This tests:
- Basic generator initialization
- Domain classification
- Weak prompt generation
- Quality score calculation
- Seed pair creation and validation
- Mini generation (if Ollama available)

## Integration with PromptEvolver

The generated pairs are compatible with:
- **Training Pipeline**: Direct input to model training
- **Data Processing**: Seamless integration with normalize_datasets.py
- **Schema Validation**: Full compliance with engineered_prompt.schema.json
- **Domain Routing**: Automatic classification for optimization strategies

## Performance

Typical performance metrics:
- **Generation Rate**: 10-30 pairs per minute (with Ollama)
- **Success Rate**: 85-95% valid pairs
- **Quality Scores**: Average 0.75-0.85 overall quality
- **Processing Time**: ~2-5 seconds per pair

## Error Handling

The script includes comprehensive error handling:
- **Network Errors**: Automatic retry with exponential backoff
- **Generation Failures**: Graceful fallback and error logging
- **Validation Errors**: Detailed validation failure reports
- **Interrupt Handling**: Graceful shutdown with checkpoint saving
- **Resume Capability**: Automatic recovery from interruptions

## Logging

Detailed logging includes:
- Generation progress and statistics
- Quality metrics and validation results
- Error details and troubleshooting information
- Performance metrics and timing data
- Checkpoint creation and loading events

Log files are saved to `logs/generate_seed_pairs_YYYYMMDD_HHMMSS.log`

## Best Practices

1. **Start Small**: Begin with 10-20 pairs to test configuration
2. **Use Checkpoints**: Enable checkpointing for large generations
3. **Monitor Quality**: Review generated pairs for quality
4. **Domain Balance**: Generate similar quantities for each domain
5. **Resource Management**: Monitor system resources during generation
6. **Configuration Tuning**: Adjust temperature and iteration settings based on results

## Troubleshooting

### Common Issues

**PromptWizard not found**
- This is expected - the script will use standalone mode
- Install PromptWizard if you want the full framework integration

**Ollama connection errors**
- Ensure Ollama is running: `ollama serve`
- Verify model is available: `ollama list`
- Check port accessibility: `curl http://localhost:11434/api/tags`

**Generation failures**
- Check model compatibility and resource availability
- Review error logs for specific failure reasons
- Try reducing batch size or generation count

**Quality validation failures**
- Review quality thresholds in configuration
- Check that enhanced prompts are significantly improved
- Verify schema compliance

### Performance Optimization

- Adjust `batch_size` based on system resources
- Use `--no-checkpoint` for faster processing (at risk of data loss)
- Increase `temperature` for more creative variations
- Reduce `mutate_refine_iterations` for faster generation

## License

Copyright (c) 2025 Matthew J. Utt  
Licensed under MIT License  
Compatible with Microsoft PromptWizard Framework