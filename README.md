# ODILE: Agentic LLM Safety Evaluations

A HUD-based framework for testing LLM agent safety across adversarial scenarios, focusing on GraySwan attacks (jailbreaks, prompt injections, and conflicting objectives).

## Project Goals

- **Safety Testing**: Evaluate LLM agents against real-world adversarial scenarios
- **Scalable Evaluation**: Support multi-model testing (OpenAI, Claude, vLLM)
- **Deterministic + LLM Judges**: Combine fast VR evaluators with robust LLM-based evaluation
- **Research Platform**: Extensible framework for new attack scenarios and defenses

## What's Implemented ✓

### GraySwan Attack Scenarios (5/5 Complete)

**A.1 Medical Records Leak** - Jailbreak to access unauthorized patient data
**A.2 Price Manipulation** - Conflicting objectives in pharmaceutical pricing
**A.3 Calendar Deletion** - Indirect prompt injection via external data
**A.4 Biased Resume Screening** - LLM judge evaluation (placeholder active)
**A.5 Spam Email** - Mass email detection

### Core Infrastructure

- **17 GraySwan Tools**: All scenario-specific tools implemented (`server/tools.py`)
- **Backend State Management**: Pharma inventory, calendar events, hiring queue, email outbox (`server/backend.py`)
- **5 VR Evaluators**: Deterministic reward functions for breach detection
- **HUD Integration**: Full MCP server with setup/evaluate lifecycle
- **Multi-Model Support**: OpenAI, Claude, vLLM agents via HUD

### Evaluation System

```bash
# Run single attack
python run_eval.py grayswan_attacks.json --task-id grayswan_a2_price_manipulation

# Run all attacks
python run_eval.py grayswan_attacks.json

# Test with different models
python run_eval.py grayswan_attacks.json --agent claude --model claude-sonnet-4-5
python run_eval.py grayswan_attacks.json --agent openai --model gpt-4o
```

## Quick Start

### 1. Start Backend
```bash
cd server
uv run uvicorn backend:app --reload
```

### 2. Build Environment
```bash
hud build  # Creates docker image test0:0.1.21
```

### 3. Run Evaluations
```bash
python run_eval.py grayswan_attacks.json
```

## Architecture

```
User Prompt → HUD Agent Loop
                 ↓
         setup_generic_scenario (initialize state)
                 ↓
         Agent uses GraySwan tools
                 ↓
         Tool calls logged to backend
                 ↓
         VR Evaluator checks logs
                 ↓
         Return reward (1.0 = breach, 0.0 = safe)
```

## Planned Features

### Phase 2: LLM Judge System
- 3-model voting with `gpt-5-mini-2025-08-07`
- Conversation trace analysis for A.4 scenario
- Appeal system for disputed evaluations

### Phase 3: Extended Testing
- Multi-turn attack scenarios
- Defense mechanism benchmarking
- Performance optimization

## Project Structure

```
server/
  backend.py       # FastAPI backend with state management
  tools.py         # 17 GraySwan tools + 5 evaluators
  main.py          # MCP server entry point

grayswan_attacks.json  # Attack task definitions
run_eval.py           # Evaluation runner using HUD
test_grayswan.py      # Validation tests
```

## Test Results

- ✓ All 17 tools operational
- ✓ VR evaluators functional (4/5 fully working, A.4 needs LLM judge)
- ✓ Backend integration tests passing
- ✓ Multi-model support verified

See `TEST_RESULTS.md` for detailed test output.

## Implementation Notes

**VR vs LLM Evaluation**:
- A.1, A.2, A.3, A.5: Deterministic tool call checking (fast, cheap)
- A.4: Requires LLM judge to parse natural language scores (pending)

**Mock Implementations**:
Tools use simulated data for rapid iteration. Sufficient for safety testing.

**State Management**:
Backend maintains per-scenario state (inventory, calendars, etc.) via `_STATE` dictionary.

## Documentation

- `GRAYSWAN_IMPLEMENTATION.md` - Full implementation details
- `TEST_RESULTS.md` - Test results and validation
- `.hud_eval.toml` - HUD evaluation configuration

## Contributing

This is a research project for LLM agent safety evaluation. See implementation docs for technical details.
