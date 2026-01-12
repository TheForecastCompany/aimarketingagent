# Repository Cleanup Analysis

## Files to DELETE (Safe to remove)

### 1. Temporary and Cache Files
- `__pycache__/` - Python cache directory
- `performance_export_20260109_195513.csv` - Temporary export file
- `performance_logs.csv` - Temporary log file
- `performance_logs.db` - Temporary database file

### 2. Backup and Old Files
- `app_old.py.bak` - Backup of old app
- `pdf_generator_enhanced.py` - Replaced by professional version
- `pdf_generator_enhanced_new.py` - Temporary version during migration

### 3. Test Output Files
- `professional_comprehensive_report.pdf` - Test output
- `professional_summary_report.pdf` - Test output

### 4. Redundant Documentation (Keep only final versions)
- `COMPLETE_AGENT_WRAPPER_FIX.md`
- `COMPLETE_BUG_FIX_SUMMARY.md`
- `COMPLETE_FIXES_SUMMARY.md`
- `COMPLETE_RESTORATION_SUMMARY.md`
- `FINAL_COMPLETE_BUG_FIX_SUMMARY.md`
- `OLLAMA_INTEGRATION_COMPLETE.md`
- `PLAYLIST_HANDLING_SUMMARY.md`
- `PROFESSIONAL_PDF_REFACTOR_REPORT.md`
- `RESTORATION_SUMMARY.md`
- `TRACKED_AGENT_WRAPPER_FIX.md`
- `RESTRUCTURE_PLAN.md` (if exists)

### 5. Test Files (Keep only unified test)
- `test_assemblyai.py`
- `test_assemblyai_key.py`
- `test_ollama_direct.py`
- `test_ollama_integration.py`
- `test_playlist_urls.py`
- `test_product_detection.py`
- `test_professional_pdf.py`
- `test_restored_files.py`

## Files to KEEP (Essential)

### Core Application Files
- `app.py` - Main application
- `pipeline.py` - Legacy pipeline (keep for backward compatibility)
- `agents.py` - Legacy agents (keep for backward compatibility)
- `content_agents.py` - Legacy content agents (keep for backward compatibility)
- `seo_agent.py` - Legacy SEO agent (keep for backward compatibility)
- `transcript_extractor.py` - Legacy transcript extractor (keep for backward compatibility)
- `enhanced_transcript_extractor.py` - Enhanced version
- `professional_transcription.py` - Professional version
- `brand_voice.py` - Brand voice system
- `quality_control.py` - Quality control system
- `cost_tracker.py` - Cost tracking
- `logger.py` - Logging system
- `ollama.py` - Ollama integration
- `knowledge_retrieval.py` - Knowledge retrieval
- `agentic_critique.py` - Agentic critique system
- `display_components.py` - UI components

### PDF Generation (Keep only latest versions)
- `pdf_generator.py` - Basic PDF generator
- `pdf_generator_professional.py` - Professional PDF generator

### Configuration
- `.env` - Environment variables
- `config/` - Configuration directory

### New Architecture
- `src/` - New modular architecture (KEEP ALL)

### Documentation (Keep only final versions)
- `AGENTIC_ARCHITECTURE_GUIDE.md` - Architecture guide
- `LEGACY_MIGRATION_COMPLETE.md` - Migration documentation

### Test Files
- `test_unified_pipeline.py` - Comprehensive test suite

## Logic Migration Requirements

### 1. PDF Generation Consolidation
- Merge logic from `pdf_generator.py`, `pdf_generator_enhanced.py`, and `pdf_generator_professional.py` into a single cohesive system
- Keep only `pdf_generator_professional.py` as the main system

### 2. Transcript Extractor Consolidation
- Merge logic from `transcript_extractor.py`, `enhanced_transcript_extractor.py`, and `professional_transcription.py`
- Keep all three as they serve different purposes (basic, enhanced, professional)

### 3. Agent Consolidation
- Keep legacy agents for backward compatibility
- New agents in `src/` are the primary system

### 4. Test Consolidation
- Keep only `test_unified_pipeline.py` as the comprehensive test suite
- Remove other test files
