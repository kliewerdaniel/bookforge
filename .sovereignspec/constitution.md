# BookForge Constitution

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI for runtime API
- **Knowledge Graph**: NetworkX + custom graph format
- **Vector Store**: ChromaDB (local-first)
- **LLM Integration**: Ollama (local inference)
- **Document Processing**: Markdown, YAML, JSON
- **Testing**: pytest
- **Package Management**: Poetry or pip with pyproject.toml

## Architectural Principles
1. **Knowledge First**: No writing without prior knowledge synthesis
2. **Deterministic Pipeline**: Every stage produces inspectable artifacts
3. **Evidence-Backed**: All content traces to source evidence
4. **Modular Agents**: Specialized agents for each pipeline stage
5. **Local-First**: No external API calls required for core functionality
6. **Living Publications**: Books evolve with their knowledge base

## Non-Negotiables
- No direct LLM-to-book generation
- All intermediate artifacts must be persisted
- Every paragraph must be traceable to evidence
- Pipeline stages must be independently reproducible
- Knowledge graph is the single source of truth

## Domain Scope
- Initially focused on technical books from SovereignSpec knowledge graphs
- Architecture must be domain-independent for future generalization
- Support multiple output formats: PDF, EPUB, HTML