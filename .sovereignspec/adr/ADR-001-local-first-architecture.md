# ADR-001: Local-First Architecture with Ollama for LLM Inference

## Status
Accepted

## Context
BookForge needs to process knowledge graphs and generate technical book content. The system requires LLM capabilities for:
- Understanding and analyzing knowledge graphs
- Generating technical content from specifications
- Reviewing content for quality and accuracy

The key constraint is that BookForge must be local-first, meaning no data should leave the user's machine. This is critical for:
1. Privacy - knowledge graphs may contain proprietary information
2. Sovereignty - users maintain full control over their data
3. Determinism - consistent results without external API variability
4. Cost - no per-token charges for large document generation

## Decision
We will use Ollama as the local LLM inference engine with the following approach:
- Primary model: qwen2.5-coder:32b for code and technical content
- Fallback models: smaller models for simple tasks
- All inference happens locally via Ollama's HTTP API
- No external API calls required for core functionality

## Rationale
1. **Privacy**: All data stays on the user's machine
2. **Performance**: Local inference avoids network latency
3. **Cost**: No per-token charges for large document generation
4. **Determinism**: Consistent results without API version changes
5. **Offline capability**: Works without internet connection

## Alternatives Considered
1. **OpenAI API**: Rejected due to data privacy concerns and cost
2. **Azure OpenAI**: Rejected due to data sovereignty requirements
3. **Local models via transformers**: Considered but Ollama provides better UX
4. ** llama.cpp**: Considered but Ollama provides easier model management

## Consequences
### Positive
- Complete data sovereignty
- No ongoing API costs
- Works offline
- Consistent results

### Negative
- Requires local compute resources
- Model quality depends on local hardware
- Initial model download can be large
- May need to optimize for different hardware configurations

## Implementation
- Use httpx to communicate with Ollama's HTTP API
- Implement model selection based on task requirements
- Add fallback mechanisms for different hardware capabilities
- Cache model responses where appropriate