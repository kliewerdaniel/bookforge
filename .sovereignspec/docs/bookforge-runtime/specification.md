# BookForge Runtime - Agentic Technical Book Synthesis

**ID:** bookforge-runtime
**Version:** 1.0.0
**Status:** draft

## Purpose
Transform structured knowledge graphs into professionally written technical books through a deterministic pipeline of research, planning, synthesis, and publishing. BookForge treats writing as the final stage of a much larger research, planning, and synthesis pipeline, ensuring technical accuracy, internal consistency, and evidence-backed publications.


## Requirements
- System must import and analyze knowledge graphs from SovereignSpec projects
- System must perform semantic survey to discover concepts and relationships
- System must organize concepts into coherent themes and structures
- System must identify knowledge gaps and perform additional research
- System must construct evidence-backed outlines and chapter specifications
- System must generate technical illustration specifications
- System must produce internally consistent manuscripts
- System must review content using multiple specialized agents
- System must compile publications into PDF, EPUB, and HTML formats
- System must track provenance for all generated content
- System must support continuous publishing when knowledge base changes
- System must preserve all intermediate artifacts for reproducibility

## Constraints
- No direct LLM-to-book generation without pipeline stages
- All intermediate artifacts must be persisted to disk
- Every paragraph must be traceable to source evidence
- Pipeline stages must be independently reproducible
- Knowledge graph serves as single source of truth
- No external API calls required for core functionality
- Local-first architecture using Ollama for inference
- Must support incremental updates when knowledge graph changes

## Acceptance Criteria
- Given a valid knowledge graph, system produces complete book blueprint
- Given chapter specifications, system generates evidence-backed chapters
- Given generated chapters, system produces technical review reports
- Given reviewed content, system compiles to PDF/EPUB/HTML formats
- Given knowledge graph updates, system identifies affected chapters
- Given affected chapters, system regenerates only impacted sections
- Given any pipeline stage, system produces inspectable artifacts
- Given concept discovery, system identifies relationships and dependencies
- Given theme construction, system groups concepts into coherent structures
- Given evidence collection, system links every paragraph to sources

## Dependencies
- None
