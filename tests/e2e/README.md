# End-to-End (E2E) Tests

This directory contains End-to-End tests that simulate complete user workflows without manual GUI interaction.

## Purpose

E2E tests validate the entire user journey from document selection to analysis and Q&A, ensuring all components work together correctly in real-world scenarios.

## Test Categories

### 1. Complete User Workflow Tests (`test_complete_user_workflow.py`)

**What it tests:**
- ✅ Complete Sachbuch-Modus analysis pipeline
- ✅ Q&A session workflow with real documents
- ✅ Analysis report generation
- ✅ Database persistence throughout workflow
- ✅ Error handling in complete scenarios

**Simulates these user actions:**
1. Start application (`LocalInsightEngine()`)
2. Select document file (`analyze_document()`)
3. Choose Sachbuch-Modus (`factual_mode=True`)
4. Wait for analysis completion
5. Ask questions (`answer_question()`)
6. View analysis reports (`get_analysis_statistics()`)

### 2. Pipeline State Validation (`test_pipeline_states.py`) *[Planned]*

**What it will test:**
- Layer 1: Document loading and parsing
- Layer 2: Text processing with/without anonymization
- Layer 3: LLM analysis integration
- Layer 4: Database persistence
- Layer 5: Q&A functionality

## Key Differences from Unit Tests

| Aspect | Unit Tests | E2E Tests |
|--------|------------|-----------|
| **Scope** | Individual components | Complete workflows |
| **Data** | Mock/fake data | Real document content |
| **Speed** | Fast (seconds) | Slower (minutes) |
| **Purpose** | Component correctness | User journey validation |
| **Isolation** | Highly isolated | Full integration |

## Running E2E Tests

### Individual E2E Tests
```bash
# Run all E2E tests
python -m pytest tests/e2e/ -v -s

# Run specific workflow test
python -m pytest tests/e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_complete_sachbuch_analysis_workflow -v -s

# Run with detailed logging
python -m pytest tests/e2e/ -v -s --log-cli-level=DEBUG
```

### Via Test Orchestrator
E2E tests will be integrated into the main test orchestrator as a separate category:

```python
# In test_orchestrator.py - E2E Test Category
("tests/e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_complete_sachbuch_analysis_workflow", "E2E Sachbuch Workflow"),
("tests/e2e/test_complete_user_workflow.py::TestCompleteUserWorkflow::test_qa_session_workflow", "E2E Q&A Workflow"),
```

## Test Data Management

- **Temporary Files**: Tests create temporary documents with realistic content
- **Clean Environment**: Each test starts with fresh state
- **Automatic Cleanup**: Temporary files and test data are automatically removed

## Expected Behavior

### ✅ Success Scenarios
- Document analysis completes without errors
- Q&A provides meaningful answers
- Analysis reports contain expected data
- Database operations succeed

### ⚠️ Graceful Failure Scenarios
- Invalid files are handled appropriately
- Empty questions return sensible responses
- Network/API issues don't crash the application

## Integration with CI/CD

E2E tests are designed to:
- Run after successful unit tests
- Validate complete functionality before releases
- Catch integration issues early
- Ensure user workflows remain functional

## Performance Considerations

E2E tests may take longer to run due to:
- Real document processing
- LLM API calls (if enabled)
- Database operations
- File I/O operations

Use appropriate timeouts and consider running E2E tests separately from fast unit tests in CI pipelines.