# PromptEvolver 3.0 Dataset Normalization Scripts

This directory contains data processing scripts for the PromptEvolver 3.0 training system.

## normalize_datasets.py

Comprehensive dataset normalization script that converts various prompt dataset formats into the standardized PromptEvolver 3.0 engineered prompt schema format.

### Features

- **Multi-format Support**: CSV, JSON, JSONL, TXT, Parquet files
- **Domain Classification**: Automatic classification into Analytics, Coding, Content, or Cross-Domain
- **Quality Scoring**: Initial quality score generation with comprehensive metrics
- **Batch Processing**: Efficient processing with progress tracking
- **Schema Validation**: Ensures output matches engineered_prompt.schema.json
- **Statistics Reporting**: Detailed processing statistics and domain distribution
- **Error Handling**: Comprehensive error handling with detailed logging

### Requirements

```bash
pip install pandas jsonschema tqdm pyarrow numpy
```

### Usage

#### Basic Usage

```bash
python normalize_datasets.py input_file.csv
```

#### With Custom Output Prefix

```bash
python normalize_datasets.py data.jsonl --output-prefix "training_data"
```

#### With Batch Processing

```bash
python normalize_datasets.py large_dataset.parquet --batch-size 500
```

#### Full Options

```bash
python normalize_datasets.py input.csv \
  --output-prefix "custom_name" \
  --output-dir "/path/to/output" \
  --batch-size 1000 \
  --schema-path "schemas/custom_schema.json" \
  --domain-classifier-path "prompts/custom_classifier.txt" \
  --verbose
```

### Supported Input Formats

#### CSV Files

Expected columns (flexible naming):

- `original_prompt`, `originalPrompt`, `original`, `input`, `prompt`, `question`, `weak_prompt`
- `enhanced_prompt`, `enhancedPrompt`, `enhanced`, `output`, `improved`, `answer`, `strong_prompt`

#### JSON Files

```json
[
  {
    "original_prompt": "Write a summary",
    "enhanced_prompt": "As a business analyst..."
  }
]
```

#### JSONL Files

```jsonl
{"original_prompt": "Debug issue", "enhanced_prompt": "As a senior developer..."}
{"original_prompt": "Write newsletter", "enhanced_prompt": "As a content specialist..."}
```

#### TXT Files

Supports various delimiters:

- `\n---\n` (triple dash separator)
- `\n##\n` (double hash separator)
- `\n\n\n` (triple newline separator)
- `\t\t` (double tab separator)
- Alternating lines (fallback)

#### Parquet Files

Standard pandas-compatible parquet files with appropriate columns.

### Output Format

The script outputs normalized data in JSON format, organized by domain:

```
data/processed/
├── analytics/
│   └── dataset_name_analytics.json
├── coding/
│   └── dataset_name_coding.json
├── content/
│   └── dataset_name_content.json
├── cross_domain/
│   └── dataset_name_cross_domain.json
└── dataset_name_statistics_report.json
```

### Domain Classification

The script automatically classifies prompts into four domains:

- **Analytics**: Data analysis, reporting, metrics, business intelligence
- **Coding**: Software development, programming, technical implementation
- **Content**: Writing, marketing, communications, creative content
- **Cross-Domain**: Multi-disciplinary tasks or ambiguous prompts

### Quality Scoring

Each normalized record includes comprehensive quality scores:

- Overall quality score (composite)
- Clarity score
- Specificity score
- Engagement score
- Structure score
- Completeness score
- Error prevention score

### Output Schema

The normalized data follows the `engineered_prompt.schema.json` format:

```json
{
  "originalPrompt": "Original user prompt",
  "enhancedPrompt": "Optimized prompt with improvements",
  "domain": "Analytics|Coding|Content|Cross-Domain",
  "metadata": {
    "qualityScore": {...},
    "improvementAreas": [...],
    "processingTimestamp": 1754586655,
    "expertIdentity": "Domain Specialist",
    "optimizationConfig": {...},
    "reasoning": "Explanation of improvements"
  },
  "followUpQuestions": [],
  "tags": ["domain", "normalized", "training-data"],
  "version": "1.0"
}
```

### Error Handling

The script includes comprehensive error handling:

- **Schema validation**: Ensures output matches expected format
- **Data validation**: Checks prompt length and content requirements
- **Format detection**: Handles malformed or unexpected input formats
- **Logging**: Detailed logging with timestamps and error details
- **Statistics**: Tracks success/failure rates and error patterns

### Performance

- Processing speed: ~40-100 records/second (depending on complexity)
- Memory efficient: Supports large datasets through batch processing
- Progress tracking: Real-time progress bars and statistics
- Error recovery: Continues processing even if individual records fail

### Logging

Logs are saved to `logs/normalize_datasets_TIMESTAMP.log` and include:

- Processing progress and statistics
- Domain classification results
- Validation errors and warnings
- Performance metrics and timing information

### Statistics Report

Each run generates a comprehensive statistics report:

```json
{
  "processing_summary": {
    "total_processed": 1000,
    "successful_normalizations": 950,
    "failed_normalizations": 50,
    "success_rate": 95.0,
    "processing_time_seconds": 25.5,
    "records_per_second": 39.2
  },
  "domain_distribution": {
    "Analytics": 250,
    "Coding": 300,
    "Content": 200,
    "Cross-Domain": 200
  },
  "quality_metrics": {
    "average_quality_score": 0.75
  },
  "error_analysis": {
    "error_count": 50,
    "error_details": [...]
  }
}
```

### Integration with PromptEvolver 3.0

The normalized datasets are ready for use with:

- Training data preparation for PromptWizard optimization
- Domain-specific model fine-tuning
- Quality assessment and benchmarking
- A/B testing of different optimization strategies

### Best Practices

1. **Data Quality**: Ensure input data has clear original→enhanced prompt pairs
2. **Batch Size**: Use appropriate batch sizes for memory management (1000 is optimal)
3. **Validation**: Always review statistics report for data quality issues
4. **Backup**: Keep copies of original datasets before normalization
5. **Testing**: Test with small datasets first to verify format compatibility

### Troubleshooting

#### Common Issues

1. **Schema Validation Errors**: Check that tags follow pattern `^[a-z0-9-]+$`
2. **Missing Prompts**: Verify column names match expected patterns
3. **Encoding Issues**: Ensure input files use UTF-8 encoding
4. **Memory Errors**: Reduce batch size for large datasets

#### Support

For issues or questions:

1. Check the logs in `logs/` directory
2. Review the statistics report for error details
3. Verify input format matches expected patterns
4. Test with smaller datasets to isolate issues

---

*Copyright (c) 2025 Matthew J. Utt*
*Licensed under MIT License*
*Compatible with Microsoft PromptWizard Framework*
