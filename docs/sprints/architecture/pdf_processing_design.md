# PDF Processing Architecture Design

## Overview

This document specifies the complete PDF processing architecture for PeerRead dataset integration, designed to handle large scientific papers with large context window models (>50k tokens, preferably 200k+) while providing intelligent fallback strategies for smaller context models.

## Architecture Components

### 1. PDF Ingestion System

#### 1.1 PDF Content Extraction

**Primary Strategy**: Leverage existing parsed PDF capability in PeerRead dataset
- **Data Source**: Utilize `parsed_pdfs` directory in PeerRead dataset
- **Format**: JSON files with structured content (`sections` → `text` extraction)
- **Integration Point**: Extend existing `PeerReadLoader.load_parsed_pdf_content(paper_id)` method
- **Performance**: Direct text extraction without PDF parsing overhead

**Fallback Strategy**: Raw PDF processing capability
- **Library**: `markitdown[pdf]` (already in dependencies)
- **Integration Point**: New `PDFProcessor` class in `src/app/data_utils/pdf_processor.py`
- **Fallback Trigger**: When parsed JSON unavailable or corrupted

#### 1.2 Content Validation and Sanitization

**Text Preprocessing Pipeline**:
```python
class PDFContentProcessor(BaseModel):
    """PDF content processing with validation."""
    
    max_section_length: int = Field(default=50000)
    encoding_validation: bool = Field(default=True)
    content_sanitization: bool = Field(default=True)
    
    def process_content(self, raw_content: str) -> ProcessedContent:
        """Process and validate PDF content."""
        pass
```

**Validation Requirements**:
- UTF-8 encoding validation
- Malformed text detection and cleaning
- Section-based content organization
- Metadata extraction (title, abstract, sections)

### 2. Large Context Model Integration Architecture

#### 2.1 Model Selection Logic

**Automatic Model Selection**:
```python
class ModelSelector(BaseModel):
    """Intelligent model selection based on content size."""
    
    token_counting_method: str = Field(default="tiktoken")
    model_context_limits: dict[str, int] = Field(default={
        "claude-3-opus": 200000,
        "claude-3-sonnet": 200000,
        "gpt-4-turbo": 128000,
        "gemini-1.5-pro": 1000000
    })
    
    def select_model(self, content: str) -> ModelConfig:
        """Select optimal model based on content token count."""
        pass
```

**Selection Criteria**:
1. **Token Count Estimation**: Use tiktoken for OpenAI models, anthropic tokenizer for Claude
2. **Context Buffer**: Reserve 20% of context limit for response generation
3. **Model Priority**: Prefer models with larger context windows for full papers
4. **Fallback Chain**: Large context → Medium context → Chunked processing

#### 2.2 Content Segmentation Strategy

**Intelligent Chunking Algorithm**:
```python
class ContentSegmenter(BaseModel):
    """Intelligent document chunking for smaller context models."""
    
    chunk_overlap: int = Field(default=200)
    preserve_sections: bool = Field(default=True)
    semantic_boundaries: bool = Field(default=True)
    
    def segment_content(self, content: str, max_tokens: int) -> list[ContentChunk]:
        """Create semantically coherent chunks."""
        pass
```

**Chunking Strategy**:
- **Section-Aware**: Preserve academic paper structure (abstract, intro, methods, results, conclusion)
- **Semantic Boundaries**: Break at paragraph boundaries, not mid-sentence
- **Overlap Strategy**: 200-token overlap between chunks for context continuity
- **Metadata Preservation**: Include paper metadata in each chunk

### 3. Performance Optimization Architecture

#### 3.1 Caching Strategy

**Multi-Level Caching**:
```python
class PDFProcessingCache(BaseModel):
    """Multi-level caching for PDF processing efficiency."""
    
    parsed_content_cache: str = Field(default="./cache/parsed_pdfs/")
    token_count_cache: str = Field(default="./cache/token_counts/")
    model_selection_cache: str = Field(default="./cache/model_selections/")
    
    cache_ttl_hours: int = Field(default=24)
    cache_compression: bool = Field(default=True)
```

**Cache Levels**:
1. **L1 - Parsed Content**: Cache extracted and processed PDF content
2. **L2 - Token Counts**: Cache token count calculations per model type
3. **L3 - Model Selection**: Cache optimal model selections per paper
4. **L4 - Chunk Mappings**: Cache segmentation results for fallback scenarios

#### 3.2 Asynchronous Processing

**Async Processing Pipeline**:
```python
class AsyncPDFProcessor:
    """Asynchronous PDF processing with concurrent handling."""
    
    async def process_batch(self, paper_ids: list[str]) -> list[ProcessingResult]:
        """Process multiple PDFs concurrently."""
        pass
    
    async def preprocess_content(self, paper_id: str) -> ProcessedContent:
        """Async content preprocessing with caching."""
        pass
```

**Performance Targets**:
- **Single Paper Processing**: <1s for cached content, <5s for fresh processing
- **Batch Processing**: 10 papers processed concurrently
- **Memory Efficiency**: Streaming processing for large papers
- **Resource Limits**: <50MB additional memory per paper

### 4. Error Handling Architecture

#### 4.1 Robust Error Recovery

**Error Categories and Handling**:
```python
class PDFProcessingError(BaseModel):
    """Comprehensive PDF processing error handling."""
    
    error_type: str = Field(description="Error category classification")
    recovery_strategy: str = Field(description="Automatic recovery approach")
    fallback_available: bool = Field(description="Fallback processing capability")
    
    @classmethod
    def handle_pdf_error(cls, error: Exception, paper_id: str) -> ErrorResult:
        """Intelligent error handling with recovery."""
        pass
```

**Error Recovery Strategies**:
1. **Encoding Issues**: Automatic re-encoding with fallback charsets
2. **Malformed PDFs**: Graceful degradation to text-only extraction
3. **Size Limits**: Automatic chunking activation
4. **Missing Files**: Fallback to alternative data sources
5. **API Failures**: Retry with exponential backoff

#### 4.2 Validation Framework

**Content Validation Pipeline**:
```python
class ContentValidator(BaseModel):
    """Multi-stage content validation."""
    
    min_content_length: int = Field(default=1000)
    max_content_length: int = Field(default=200000)
    required_sections: list[str] = Field(default=["abstract", "introduction"])
    
    def validate_processed_content(self, content: ProcessedContent) -> ValidationResult:
        """Comprehensive content validation."""
        pass
```

**Validation Stages**:
1. **Structure Validation**: Verify academic paper structure
2. **Content Quality**: Ensure meaningful text extraction
3. **Completeness Check**: Validate all sections present
4. **Token Limit Verification**: Confirm model compatibility

### 5. Integration Points

#### 5.1 PeerRead Dataset Integration

**Enhanced PeerReadLoader Integration**:
```python
class EnhancedPeerReadLoader(PeerReadLoader):
    """Extended PeerRead loader with PDF processing capabilities."""
    
    def __init__(self, config: PeerReadConfig, pdf_processor: PDFProcessor):
        super().__init__(config)
        self.pdf_processor = pdf_processor
    
    async def load_paper_with_content(self, paper_id: str) -> PeerReadPaperWithContent:
        """Load paper with full PDF content processed."""
        pass
    
    async def get_optimized_content(self, paper_id: str, target_model: str) -> OptimizedContent:
        """Get content optimized for specific model context limits."""
        pass
```

**New Data Models**:
```python
class ProcessedPDFContent(BaseModel):
    """Processed PDF content with metadata."""
    paper_id: str
    raw_content: str
    processed_content: str
    token_count: dict[str, int]  # Per model type
    sections: dict[str, str]
    metadata: dict[str, Any]
    processing_timestamp: str

class PeerReadPaperWithContent(PeerReadPaper):
    """Extended PeerRead paper with PDF content."""
    pdf_content: ProcessedPDFContent | None = None
    content_chunks: list[ContentChunk] | None = None
    recommended_model: str | None = None
```

#### 5.2 Agent System Integration

**Manager Agent Enhancement**:
```python
class EnhancedManagerAgent:
    """Manager agent with PDF processing capabilities."""
    
    def __init__(self, pdf_processor: PDFProcessor, model_selector: ModelSelector):
        self.pdf_processor = pdf_processor
        self.model_selector = model_selector
    
    async def process_peerread_paper(self, paper_id: str) -> ReviewGenerationResult:
        """Process PeerRead paper with optimal model selection."""
        # 1. Load and process PDF content
        # 2. Select optimal model based on content size
        # 3. Delegate to appropriate agents based on model capabilities
        # 4. Handle chunked processing if needed
        pass
```

**Tool Integration**:
- **PeerRead Tool Enhancement**: Extend existing `PeerReadTool` with PDF content access
- **Model Selection Tool**: New tool for runtime model switching
- **Content Chunking Tool**: Tool for handling large documents

### 6. Configuration Architecture

#### 6.1 PDF Processing Configuration

**Configuration Schema**:
```python
class PDFProcessingConfig(BaseModel):
    """Comprehensive PDF processing configuration."""
    
    # Processing Settings
    max_paper_size_mb: int = Field(default=50)
    processing_timeout_seconds: int = Field(default=30)
    concurrent_processing_limit: int = Field(default=5)
    
    # Model Selection
    preferred_models: list[str] = Field(default=["claude-3-opus", "gpt-4-turbo"])
    fallback_chunk_size: int = Field(default=8000)
    context_buffer_ratio: float = Field(default=0.2)
    
    # Caching
    enable_caching: bool = Field(default=True)
    cache_directory: str = Field(default="./cache/pdf_processing/")
    cache_cleanup_interval_hours: int = Field(default=24)
    
    # Error Handling
    max_retry_attempts: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)
    enable_fallback_processing: bool = Field(default=True)
```

#### 6.2 Model Configuration Integration

**Extended Model Configuration**:
```python
class LargeContextModelConfig(BaseModel):
    """Configuration for large context model integration."""
    
    model_name: str
    context_limit: int
    token_cost_per_1k: float
    processing_speed_tokens_per_second: int
    preferred_content_types: list[str]
    supports_streaming: bool = Field(default=False)
    
    @field_validator("context_limit")
    def validate_context_limit(cls, v: int) -> int:
        if v < 50000:
            raise ValueError("Large context models must support >50k tokens")
        return v
```

## Implementation Guide for Developers

### Phase 1: Core PDF Processing (Day 1-2)

**Required Implementation**:
1. **Create `src/app/data_utils/pdf_processor.py`**:
   - Implement `PDFProcessor` class with `markitdown` integration
   - Add content validation and sanitization
   - Implement caching layer

2. **Extend `src/app/data_utils/datasets_peerread.py`**:
   - Enhance `PeerReadLoader` with PDF content methods
   - Add async processing capabilities
   - Implement error handling

3. **Create `src/app/data_models/pdf_models.py`**:
   - Define `ProcessedPDFContent`, `PeerReadPaperWithContent`
   - Add validation schemas
   - Implement configuration models

### Phase 2: Model Integration (Day 2-3)

**Required Implementation**:
1. **Create `src/app/utils/model_selector.py`**:
   - Implement `ModelSelector` with token counting
   - Add model context limit management
   - Create fallback strategy logic

2. **Extend `src/app/agents/llm_model_funs.py`**:
   - Add large context model configurations
   - Implement model switching logic
   - Add token cost calculation

3. **Update `src/app/agents/agent_system.py`**:
   - Enhance Manager agent with PDF processing
   - Add content chunking support
   - Implement model-aware delegation

### Phase 3: Performance Optimization (Day 3-4)

**Required Implementation**:
1. **Create `src/app/utils/content_segmenter.py`**:
   - Implement semantic chunking algorithm
   - Add section-aware processing
   - Create overlap management

2. **Add `src/app/utils/pdf_cache.py`**:
   - Implement multi-level caching
   - Add cache invalidation logic
   - Create compression support

3. **Create configuration files**:
   - Update `config/config_pdf.json`
   - Add model configuration entries
   - Update evaluation configuration

### Testing Requirements

**Unit Tests**:
- PDF content extraction accuracy
- Token counting precision
- Model selection logic
- Error handling scenarios
- Cache functionality

**Integration Tests**:
- End-to-end paper processing
- Model switching scenarios
- Large paper handling
- Error recovery testing
- Performance benchmarks

**Performance Tests**:
- Processing time benchmarks
- Memory usage profiling
- Concurrent processing limits
- Cache efficiency metrics

### Dependencies

**Required Packages** (already in pyproject.toml):
- `markitdown[pdf]>=0.1.2` - PDF content extraction
- `pydantic>=2.10.6` - Data validation
- `httpx>=0.28.1` - Async HTTP operations

**Additional Utilities**:
- `tiktoken` - Token counting for OpenAI models
- `anthropic` - Token counting for Claude models
- File system caching utilities

### Success Criteria

**Functional Requirements**:
- [ ] Process 95% of PeerRead papers successfully
- [ ] Automatic model selection based on content size
- [ ] Intelligent chunking for smaller context models
- [ ] Robust error handling with recovery

**Performance Requirements**:
- [ ] <1s processing time for cached content
- [ ] <5s processing time for fresh content
- [ ] <50MB memory usage per paper
- [ ] Support for concurrent processing

**Quality Requirements**:
- [ ] >90% test coverage
- [ ] Zero data loss during processing
- [ ] Consistent content quality across models
- [ ] Comprehensive error logging

This architecture provides a complete foundation for PDF processing with large context models while maintaining the existing codebase patterns and ensuring robust, efficient operation.