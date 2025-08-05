"""
Sample prompts and test data for PromptEvolver CLI tests
"""

SAMPLE_PROMPTS = {
    "simple": [
        "Write a haiku about coding",
        "Explain photosynthesis",
        "Create a todo list",
    ],
    
    "complex": [
        "Develop a comprehensive marketing strategy for a B2B SaaS product targeting enterprise customers in the healthcare industry, including market analysis, positioning, pricing, and go-to-market tactics",
        "Design and implement a distributed microservices architecture for an e-commerce platform that handles 1M+ daily transactions, ensuring high availability, scalability, and data consistency",
        "Create a detailed project management plan for migrating a legacy monolithic application to cloud-native architecture, including risk assessment, timeline, resource allocation, and rollback strategies",
    ],
    
    "domain_specific": {
        "technical": [
            "Debug this Python memory leak",
            "Optimize database query performance",
            "Design REST API endpoints",
        ],
        "creative": [
            "Write a compelling brand story",
            "Create engaging social media content",
            "Develop a creative advertising campaign",
        ],
        "business": [
            "Analyze quarterly financial reports",
            "Develop stakeholder communication plan",
            "Create performance improvement strategy",
        ],
        "academic": [
            "Conduct literature review on AI ethics",
            "Design research methodology",
            "Write academic paper abstract",
        ]
    },
    
    "edge_cases": [
        "",  # Empty prompt
        "a",  # Single character
        "A" * 1000,  # Very long prompt
        "Test with special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./",
        "Test with Unicode: 你好 🌍 Здравствуй",
        "Line 1\nLine 2\nLine 3",  # Multi-line
    ]
}

EXPECTED_OPTIMIZATIONS = {
    "simple_haiku": {
        "original": "Write a haiku about coding",
        "optimized": "Please compose a traditional haiku (5-7-5 syllable structure) that captures the essence of programming and software development. Focus on the creative, meditative, or challenging aspects of coding.",
        "improvements": [
            "Added specific format requirements (5-7-5 syllables)",
            "Clarified the topic focus areas",
            "Enhanced with structural guidance"
        ]
    },
    
    "technical_optimization": {
        "original": "Debug this Python memory leak",
        "optimized": "You are a senior Python developer with expertise in memory profiling and optimization. Please help debug a memory leak issue by: 1) Analyzing the provided code for common memory leak patterns, 2) Identifying potential causes (circular references, unclosed resources, large object retention), 3) Recommending specific debugging tools and techniques, 4) Providing code examples for fixes.",
        "improvements": [
            "Added expert identity and context",
            "Structured the debugging approach",
            "Specified common memory leak patterns to check",
            "Requested actionable solutions with examples"
        ]
    }
}

BATCH_TEST_DATA = {
    "small_batch": [
        "Summarize this article",
        "Translate to French",
        "Write unit tests"
    ],
    
    "medium_batch": [
        f"Generate example {i} for testing batch processing"
        for i in range(1, 11)
    ],
    
    "large_batch": [
        f"Large batch test prompt number {i} with varying complexity and length"
        for i in range(1, 26)
    ]
}

CONFIG_TEST_DATA = {
    "quick_mode": {
        "mutate_refine_iterations": 1,
        "mutation_rounds": 1,
        "expected_time": 15  # seconds
    },
    
    "advanced_mode": {
        "mutate_refine_iterations": 3,
        "mutation_rounds": 3,
        "expected_time": 45  # seconds
    },
    
    "domain_configs": {
        "technical": {
            "style_variation": 2,
            "focus": "precision and accuracy"
        },
        "creative": {
            "style_variation": 5,
            "temperature": 0.8,
            "focus": "creativity and engagement"
        }
    }
}

ERROR_TEST_SCENARIOS = {
    "network_errors": [
        {
            "error_type": "ConnectionError",
            "message": "Failed to connect to Convex backend",
            "expected_suggestion": "Check your internet connection"
        },
        {
            "error_type": "TimeoutError", 
            "message": "Request timed out after 30 seconds",
            "expected_suggestion": "Try running 'promptevolver health'"
        }
    ],
    
    "api_errors": [
        {
            "error_type": "InvalidRequest",
            "message": "Invalid prompt format",
            "expected_suggestion": "Check that your prompt is properly formatted"
        },
        {
            "error_type": "RateLimitError",
            "message": "API rate limit exceeded",
            "expected_suggestion": "Please wait before making more requests"
        }
    ]
}

PERFORMANCE_BENCHMARKS = {
    "response_times": {
        "health_check": 2.0,  # seconds
        "single_optimization": 30.0,  # seconds  
        "batch_processing": 60.0,  # seconds per 10 prompts
    },
    
    "throughput": {
        "batch_rate": 10,  # prompts per minute
        "concurrent_limit": 5  # maximum concurrent requests
    },
    
    "resource_usage": {
        "memory_limit": 100,  # MB
        "cpu_threshold": 80  # percentage
    }
}