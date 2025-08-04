"""
Template API endpoints.
Prompt template library and management system.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from ....core.auth import get_current_active_user, get_optional_user, standard_rate_limit
from ....db.session import get_db
from ....models.user import User
from ....services.redis_service import redis_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PromptTemplate(BaseModel):
    """Prompt template model."""
    
    id: str
    title: str
    description: str
    category: str
    template_text: str
    variables: List[str]
    tags: List[str]
    difficulty: str
    use_cases: List[str]
    author: Optional[str]
    is_public: bool
    usage_count: int
    rating: float
    created_at: str
    updated_at: str


class CreateTemplateRequest(BaseModel):
    """Create template request model."""
    
    title: str = Field(..., min_length=3, max_length=200, description="Template title")
    description: str = Field(..., min_length=10, max_length=1000, description="Template description")
    category: str = Field(..., description="Template category")
    template_text: str = Field(..., min_length=20, max_length=5000, description="Template text with variables")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Template tags")
    difficulty: str = Field("intermediate", description="Template difficulty level")
    use_cases: List[str] = Field(default_factory=list, max_items=5, description="Template use cases")
    is_public: bool = Field(True, description="Whether template is public")
    
    @validator("category")
    def validate_category(cls, v):
        allowed_categories = [
            "writing", "coding", "analysis", "creative", "business", 
            "educational", "technical", "marketing", "research", "general"
        ]
        if v not in allowed_categories:
            raise ValueError(f"Invalid category. Must be one of: {allowed_categories}")
        return v
    
    @validator("difficulty")
    def validate_difficulty(cls, v):
        allowed_difficulties = ["beginner", "intermediate", "advanced", "expert"]
        if v not in allowed_difficulties:
            raise ValueError(f"Invalid difficulty. Must be one of: {allowed_difficulties}")
        return v
    
    @validator("tags")
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag) > 30:
                    raise ValueError("Each tag must be less than 30 characters")
        return v


class TemplateResponse(BaseModel):
    """Template response model."""
    
    id: str
    title: str
    description: str
    category: str
    template_text: str
    variables: List[str]
    tags: List[str]
    difficulty: str
    use_cases: List[str]
    author: Optional[str]
    is_public: bool
    usage_count: int
    rating: float
    created_at: str
    updated_at: str
    can_edit: bool = False


class TemplateLibrary(BaseModel):
    """Template library response model."""
    
    templates: List[TemplateResponse]
    total_count: int
    categories: List[Dict[str, Any]]
    popular_tags: List[str]
    featured_templates: List[TemplateResponse]


# In-memory template storage (in production, this would be in database)
TEMPLATE_STORAGE = {}
TEMPLATE_CATEGORIES = {
    "writing": {"name": "Writing & Content", "description": "Content creation and writing assistance"},
    "coding": {"name": "Code & Development", "description": "Programming and development tasks"},
    "analysis": {"name": "Analysis & Research", "description": "Data analysis and research tasks"},
    "creative": {"name": "Creative & Design", "description": "Creative and artistic prompts"},
    "business": {"name": "Business & Strategy", "description": "Business and strategic planning"},
    "educational": {"name": "Education & Learning", "description": "Educational and training content"},
    "technical": {"name": "Technical Documentation", "description": "Technical writing and documentation"},
    "marketing": {"name": "Marketing & Sales", "description": "Marketing and promotional content"},
    "research": {"name": "Research & Investigation", "description": "Research and investigation tasks"},
    "general": {"name": "General Purpose", "description": "Multi-purpose and general templates"}
}

# Sample templates for demonstration
SAMPLE_TEMPLATES = [
    {
        "id": "tpl_001",
        "title": "Blog Post Writer",
        "description": "Generate engaging blog posts on any topic with proper structure and SEO optimization",
        "category": "writing",
        "template_text": """Write a comprehensive blog post about {topic}.

Structure:
1. Engaging headline
2. Introduction that hooks the reader
3. 3-5 main points with subheadings
4. Conclusion with call-to-action

Target audience: {audience}
Tone: {tone}
Word count: {word_count}

Include relevant examples and make it SEO-friendly.""",
        "variables": ["topic", "audience", "tone", "word_count"],
        "tags": ["blog", "content", "seo", "writing"],
        "difficulty": "intermediate",
        "use_cases": ["Content marketing", "Blog writing", "SEO content"],
        "author": "System",
        "is_public": True,
        "usage_count": 245,
        "rating": 4.7,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "tpl_002", 
        "title": "Code Review Assistant",
        "description": "Perform thorough code reviews focusing on quality, security, and best practices",
        "category": "coding",
        "template_text": """Review the following {language} code and provide detailed feedback:

```{language}
{code}
```

Please analyze:
1. Code quality and readability
2. Performance considerations
3. Security vulnerabilities
4. Best practices adherence
5. Potential bugs or issues

Provide specific suggestions for improvement with examples.""",
        "variables": ["language", "code"],
        "tags": ["code-review", "programming", "quality", "security"],
        "difficulty": "advanced",
        "use_cases": ["Code review", "Quality assurance", "Mentoring"],
        "author": "System",
        "is_public": True,
        "usage_count": 178,
        "rating": 4.9,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": "tpl_003",
        "title": "Business Strategy Analyzer",
        "description": "Analyze business strategies and provide actionable insights and recommendations",
        "category": "business",
        "template_text": """Analyze the business strategy for {company_name} in the {industry} industry.

Current situation:
{current_situation}

Goals:
{goals}

Please provide:
1. SWOT analysis
2. Market opportunity assessment
3. Competitive analysis
4. Strategic recommendations
5. Implementation timeline
6. Key success metrics

Focus on actionable insights and practical next steps.""",
        "variables": ["company_name", "industry", "current_situation", "goals"],
        "tags": ["strategy", "business", "analysis", "planning"],
        "difficulty": "expert",
        "use_cases": ["Strategic planning", "Business consulting", "Market analysis"],
        "author": "System",
        "is_public": True,
        "usage_count": 89,
        "rating": 4.5,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]

# Initialize sample templates
for template in SAMPLE_TEMPLATES:
    TEMPLATE_STORAGE[template["id"]] = template


def extract_variables(template_text: str) -> List[str]:
    """Extract variables from template text (e.g., {variable_name})."""
    import re
    variables = re.findall(r'\{([^}]+)\}', template_text)
    return list(set(variables))  # Remove duplicates


@router.get("/", response_model=TemplateLibrary)
async def get_template_library(
    current_user: User = Depends(get_optional_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    sort_by: str = Query("popular", regex="^(popular|recent|rating|title)$", description="Sort order")
) -> TemplateLibrary:
    """
    Get prompt template library with filtering and search capabilities.
    
    Returns a curated collection of prompt templates with various filters.
    """
    try:
        # Get all templates (in production, this would be a database query)
        all_templates = list(TEMPLATE_STORAGE.values())
        
        # Apply filters
        filtered_templates = all_templates
        
        if category:
            filtered_templates = [t for t in filtered_templates if t["category"] == category]
        
        if tags:
            tag_list = [tag.strip().lower() for tag in tags.split(",")]
            filtered_templates = [
                t for t in filtered_templates 
                if any(tag in [t_tag.lower() for t_tag in t["tags"]] for tag in tag_list)
            ]
        
        if difficulty:
            filtered_templates = [t for t in filtered_templates if t["difficulty"] == difficulty]
        
        if search:
            search_lower = search.lower()
            filtered_templates = [
                t for t in filtered_templates 
                if search_lower in t["title"].lower() or search_lower in t["description"].lower()
            ]
        
        # Sort templates
        if sort_by == "popular":
            filtered_templates.sort(key=lambda x: x["usage_count"], reverse=True)
        elif sort_by == "recent":
            filtered_templates.sort(key=lambda x: x["updated_at"], reverse=True)
        elif sort_by == "rating":
            filtered_templates.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "title":
            filtered_templates.sort(key=lambda x: x["title"])
        
        # Apply pagination
        total_count = len(filtered_templates)
        paginated_templates = filtered_templates[skip:skip + limit]
        
        # Convert to response models
        templates_response = []
        for template in paginated_templates:
            templates_response.append(TemplateResponse(
                id=template["id"],
                title=template["title"],
                description=template["description"],
                category=template["category"],
                template_text=template["template_text"],
                variables=template["variables"],
                tags=template["tags"],
                difficulty=template["difficulty"],
                use_cases=template["use_cases"],
                author=template["author"],
                is_public=template["is_public"],
                usage_count=template["usage_count"],
                rating=template["rating"],
                created_at=template["created_at"],
                updated_at=template["updated_at"],
                can_edit=template["author"] == (current_user.username if current_user else None)
            ))
        
        # Get categories with counts
        category_counts = {}
        for template in all_templates:
            cat = template["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        categories = [
            {
                "key": key,
                "name": TEMPLATE_CATEGORIES[key]["name"],
                "description": TEMPLATE_CATEGORIES[key]["description"],
                "count": category_counts.get(key, 0)
            }
            for key in TEMPLATE_CATEGORIES.keys()
            if category_counts.get(key, 0) > 0
        ]
        
        # Get popular tags
        all_tags = []
        for template in all_templates:
            all_tags.extend(template["tags"])
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        popular_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:10]
        
        # Get featured templates (top-rated public templates)
        featured_templates = sorted(
            [t for t in all_templates if t["is_public"]], 
            key=lambda x: x["rating"], 
            reverse=True
        )[:3]
        
        featured_response = [
            TemplateResponse(
                id=template["id"],
                title=template["title"],
                description=template["description"],
                category=template["category"],
                template_text=template["template_text"],
                variables=template["variables"],
                tags=template["tags"],
                difficulty=template["difficulty"],
                use_cases=template["use_cases"],
                author=template["author"],
                is_public=template["is_public"],
                usage_count=template["usage_count"],
                rating=template["rating"],
                created_at=template["created_at"],
                updated_at=template["updated_at"],
                can_edit=template["author"] == (current_user.username if current_user else None)
            )
            for template in featured_templates
        ]
        
        return TemplateLibrary(
            templates=templates_response,
            total_count=total_count,
            categories=categories,
            popular_tags=popular_tags,
            featured_templates=featured_response
        )
    
    except Exception as e:
        logger.error(f"Failed to get template library: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template library"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_detail(
    template_id: str,
    current_user: User = Depends(get_optional_user)
) -> TemplateResponse:
    """
    Get detailed information about a specific template.
    
    Returns complete template details including usage statistics.
    """
    try:
        template = TEMPLATE_STORAGE.get(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Increment usage count (in production, this would be in database)
        template["usage_count"] += 1
        
        return TemplateResponse(
            id=template["id"],
            title=template["title"],
            description=template["description"],
            category=template["category"],
            template_text=template["template_text"],
            variables=template["variables"],
            tags=template["tags"],
            difficulty=template["difficulty"],
            use_cases=template["use_cases"],
            author=template["author"],
            is_public=template["is_public"],
            usage_count=template["usage_count"],
            rating=template["rating"],
            created_at=template["created_at"],
            updated_at=template["updated_at"],
            can_edit=template["author"] == (current_user.username if current_user else None)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template details"
        )


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: CreateTemplateRequest,
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(standard_rate_limit)
) -> TemplateResponse:
    """
    Create a new prompt template.
    
    Allows authenticated users to create and share prompt templates.
    """
    try:
        # Generate template ID
        template_id = f"tpl_{uuid.uuid4().hex[:8]}"
        
        # Extract variables from template text
        variables = extract_variables(template_data.template_text)
        
        # Create template record
        template = {
            "id": template_id,
            "title": template_data.title,
            "description": template_data.description,
            "category": template_data.category,
            "template_text": template_data.template_text,
            "variables": variables,
            "tags": template_data.tags,
            "difficulty": template_data.difficulty,
            "use_cases": template_data.use_cases,
            "author": current_user.username,
            "is_public": template_data.is_public,
            "usage_count": 0,
            "rating": 0.0,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Store template (in production, this would be in database)
        TEMPLATE_STORAGE[template_id] = template
        
        logger.info(f"Template created: {template_id} by user {current_user.username}")
        
        return TemplateResponse(
            id=template["id"],
            title=template["title"],
            description=template["description"],
            category=template["category"],
            template_text=template["template_text"],
            variables=template["variables"],
            tags=template["tags"],
            difficulty=template["difficulty"],
            use_cases=template["use_cases"],
            author=template["author"],
            is_public=template["is_public"],
            usage_count=template["usage_count"],
            rating=template["rating"],
            created_at=template["created_at"],
            updated_at=template["updated_at"],
            can_edit=True
        )
    
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> TemplateResponse:
    """
    Update an existing template.
    
    Allows template authors to update their templates.
    """
    try:
        template = TEMPLATE_STORAGE.get(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check if user can edit this template
        if template["author"] != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own templates"
            )
        
        # Update allowed fields
        allowed_fields = {
            "title", "description", "template_text", "tags", 
            "difficulty", "use_cases", "is_public"
        }
        
        for field, value in update_data.items():
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field}' cannot be updated"
                )
            
            template[field] = value
        
        # Update variables if template_text changed
        if "template_text" in update_data:
            template["variables"] = extract_variables(update_data["template_text"])
        
        # Update timestamp
        template["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        logger.info(f"Template updated: {template_id}")
        
        return TemplateResponse(
            id=template["id"],
            title=template["title"],
            description=template["description"],
            category=template["category"],
            template_text=template["template_text"],
            variables=template["variables"],
            tags=template["tags"],
            difficulty=template["difficulty"],
            use_cases=template["use_cases"],
            author=template["author"],
            is_public=template["is_public"],
            usage_count=template["usage_count"],
            rating=template["rating"],
            created_at=template["created_at"],
            updated_at=template["updated_at"],
            can_edit=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Delete a template.
    
    Allows template authors to delete their templates.
    """
    try:
        template = TEMPLATE_STORAGE.get(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check if user can delete this template
        if template["author"] != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own templates"
            )
        
        # Delete template
        del TEMPLATE_STORAGE[template_id]
        
        logger.info(f"Template deleted: {template_id}")
        
        return {"message": "Template deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )


@router.get("/categories/list")
async def get_template_categories() -> Dict[str, Any]:
    """
    Get list of template categories.
    
    Returns available categories with descriptions and counts.
    """
    try:
        # Count templates per category
        category_counts = {}
        for template in TEMPLATE_STORAGE.values():
            cat = template["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        categories = [
            {
                "key": key,
                "name": info["name"],
                "description": info["description"],
                "count": category_counts.get(key, 0)
            }
            for key, info in TEMPLATE_CATEGORIES.items()
        ]
        
        return {
            "categories": categories,
            "total_templates": len(TEMPLATE_STORAGE)
        }
    
    except Exception as e:
        logger.error(f"Failed to get template categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template categories"
        )