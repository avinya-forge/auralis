# AI Skills

This document outlines the specialized AI skills and agents that are to be integrated into Auralis to maximize efficiency and automate repository maintenance.

## 1. Headroom Skill (Codebase Optimization)
- **Purpose:** Analyze and optimize the existing codebase.
- **Functions:**
  - Detect redundant functions and duplicate logic blocks via AST parsing.
  - Automatically generate refactoring suggestions using LLM orchestration.
  - Inject proposed optimizations into a "Tech Debt" backlog queue for human review or autonomous execution.

## 2. Task Observer Skill (Metrics & Monitoring)
- **Purpose:** Monitor agent progress and maintain system health metrics.
- **Functions:**
  - Hook into the meta-router to track state-machine execution.
  - Automatically recalculate completion metrics.
  - Act as a circuit-breaker, detecting stuck tasks (e.g., infinite retry loops) and automatically marking them as blocked to prevent system stalls.
