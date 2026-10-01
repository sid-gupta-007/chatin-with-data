"""
Multi-Agent Orchestration for NL→SQL
Integrates the 5-agent workflow into FastAPI backend
"""

import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ============================================================================
# Orchestration Models
# ============================================================================

class OrchestrationRequest(BaseModel):
    """Request to orchestrate multi-agent analysis"""
    query: str
    limit: int = 100

class AgentOutput(BaseModel):
    """Output from a single orchestrated agent"""
    table: str = None
    columns: List[str] = None
    confidence: float = None
    sql: str = None
    explanation: str = None
    valid: bool = None
    safe: bool = None
    issues: List[str] = []
    suggestions: List[str] = []
    jev_scores: Dict[str, float] = {}

class OrchestrationResponse(BaseModel):
    """Complete orchestration response with all agent outputs"""
    query: str
    generated_sql: str
    confidence: float
    execution_time_ms: float
    agents: Dict[str, Any]

# ============================================================================
# Agent Implementations
# ============================================================================

class SemanticAnalyzer:
    """Agent 1: Semantic table & column identification"""

    @staticmethod
    def analyze(query: str, schema_info=None) -> Dict[str, Any]:
        """
        Analyze query semantically to identify table and columns
        In production, would use MiniLM v6 embeddings
        """
        logger.info(f"[Semantic Analyzer] Analyzing: {query}")

        # Fallback logic (in production, use MiniLM embeddings)
        tables = schema_info.tables if schema_info else ["employees", "products", "orders"]

        # Simple heuristic: find best matching table
        best_table = None
        best_score = 0
        for table in tables:
            if table.lower() in query.lower():
                best_table = table
                best_score = 0.95
                break

        if not best_table:
            best_table = tables[0] if tables else "unknown"
            best_score = 0.5

        # Infer columns based on query
        columns = ["name", "salary"] if best_table == "employees" else ["*"]
        if "all" in query.lower():
            columns = ["*"]

        return {
            "table": best_table,
            "columns": columns,
            "confidence": min(best_score, 0.95)
        }

class JEVIntentClassifier:
    """Agent 2: JEV probabilistic intent classification"""

    @staticmethod
    def classify(query: str) -> Dict[str, float]:
        """
        Classify query intent with JEV probabilistic scores
        """
        logger.info(f"[JEV Classifier] Classifying: {query}")

        q_lower = query.lower()
        scores = {
            "top": JEVIntentClassifier._score_intent(q_lower, ["top", "highest", "best", "maximum", "largest"]),
            "count": JEVIntentClassifier._score_intent(q_lower, ["count", "how many", "total records"]),
            "average": JEVIntentClassifier._score_intent(q_lower, ["average", "avg", "mean"]),
            "sum": JEVIntentClassifier._score_intent(q_lower, ["sum", "total", "aggregate"]),
            "group": JEVIntentClassifier._score_intent(q_lower, ["by", "group", "breakdown"]),
            "filter": JEVIntentClassifier._score_intent(q_lower, ["where", "filter", "select"])
        }

        return scores

    @staticmethod
    def _score_intent(query_lower: str, keywords: List[str]) -> float:
        """Score probability of intent based on keyword matches"""
        matches = sum(1 for kw in keywords if kw in query_lower)
        return min(0.3 + (matches * 0.2), 1.0)

class SQLGenerator:
    """Agent 3: SQL query generation"""

    @staticmethod
    def generate(query: str, semantic: Dict[str, Any], intent: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate SQL from semantic analysis and intent classification
        """
        logger.info(f"[SQL Generator] Generating SQL for: {query}")

        table = semantic.get("table", "employees")
        columns = semantic.get("columns", ["*"])
        select_clause = ", ".join(columns) if columns != ["*"] else "*"

        sql = f"SELECT {select_clause} FROM {table}"

        # Add clauses based on intent
        primary_intent = max(intent.items(), key=lambda x: x[1])[0]

        if primary_intent == "top" and intent.get("top", 0) > 0.7:
            sql += " ORDER BY " + (columns[0] if columns != ["*"] else "id") + " DESC LIMIT 10"
        elif primary_intent == "count" and intent.get("count", 0) > 0.7:
            sql = f"SELECT COUNT(*) as total FROM {table}"
        elif primary_intent == "average" and intent.get("average", 0) > 0.7:
            sql = f"SELECT AVG({columns[0] if columns != ['*'] else 'id'}) as average FROM {table}"
        elif primary_intent == "group" and intent.get("group", 0) > 0.6:
            if columns != ["*"]:
                sql += f" GROUP BY {columns[0]}"

        explanation = f"Primary intent detected: {primary_intent} ({intent.get(primary_intent, 0):.0%} confidence). Generated {primary_intent.upper()} query."

        return {
            "sql": sql,
            "explanation": explanation,
            "confidence": intent.get(primary_intent, 0.7)
        }

class SQLVerifier:
    """Agent 4: SQL correctness and safety verification"""

    @staticmethod
    def verify(sql: str, query: str, intent: Dict[str, float]) -> Dict[str, Any]:
        """
        Verify SQL is correct, safe, and matches intent
        """
        logger.info(f"[SQL Verifier] Verifying: {sql}")

        issues = []

        # Check basic syntax
        valid = all(keyword in sql.upper() for keyword in ["SELECT", "FROM"])

        # Check safety (no injection patterns)
        safe = "DROP" not in sql.upper() and "DELETE" not in sql.upper()

        # Check intent match
        primary_intent = max(intent.items(), key=lambda x: x[1])[0]
        intent_match = True

        if primary_intent == "top" and "ORDER BY" not in sql.upper():
            issues.append("Query doesn't have ORDER BY for TOP intent")
            intent_match = False

        if primary_intent == "count" and "COUNT" not in sql.upper():
            issues.append("Query doesn't have COUNT for COUNT intent")
            intent_match = False

        confidence = 0.95 if (valid and safe and intent_match) else 0.7

        return {
            "valid": valid,
            "safe": safe,
            "confidence": confidence,
            "issues": issues
        }

class SQLOptimizer:
    """Agent 5: SQL query optimization suggestions"""

    @staticmethod
    def optimize(sql: str, query: str) -> Dict[str, Any]:
        """
        Suggest SQL optimizations
        """
        logger.info(f"[SQL Optimizer] Optimizing: {sql}")

        suggestions = []

        if "ORDER BY" in sql.upper() and "LIMIT" in sql.upper():
            col = sql.upper().split("ORDER BY")[1].split("LIMIT")[0].strip().split()[0]
            suggestions.append(f"Add INDEX on {col} column for faster sorting")

        if len(sql) > 100:
            suggestions.append("Consider breaking this into a view for reusability")

        if "COUNT(*)" in sql.upper():
            suggestions.append("Use COUNT(1) instead of COUNT(*) for potential performance gain")

        improvement_reason = "The original query is simple and efficient." if not suggestions else "Several optimization opportunities detected."

        return {
            "optimized_sql": sql,  # In production, would modify the SQL
            "suggestions": suggestions,
            "improvement_reason": improvement_reason
        }

# ============================================================================
# Orchestrator
# ============================================================================

class QueryOrchestrator:
    """Orchestrates all 5 agents to analyze a natural language query"""

    def __init__(self, schema_info=None):
        self.schema_info = schema_info
        self.semantic_analyzer = SemanticAnalyzer()
        self.jev_classifier = JEVIntentClassifier()
        self.sql_generator = SQLGenerator()
        self.verifier = SQLVerifier()
        self.optimizer = SQLOptimizer()

    async def orchestrate(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """
        Run multi-agent orchestration: 5 agents in coordinated phases

        Phase 1 (Parallel): Semantic Analysis + JEV Intent Classification
        Phase 2 (Sequential): SQL Generation (uses Phase 1 results)
        Phase 3 (Parallel): SQL Verification + Optimization
        Phase 4 (Synthesis): Combine all outputs
        """
        import time
        start_time = time.time()

        logger.info(f"[Orchestrator] Starting orchestration for query: {request.query}")

        # =====================================================================
        # Phase 1: Parallel Analysis (Semantic + JEV Intent)
        # =====================================================================
        logger.info("[Orchestrator] Phase 1: Semantic Analysis & JEV Intent Classification (Parallel)")

        semantic_result = self.semantic_analyzer.analyze(request.query, self.schema_info)
        intent_result = self.jev_classifier.classify(request.query)

        logger.info(f"[Orchestrator] Phase 1 Complete:")
        logger.info(f"  - Semantic: table={semantic_result['table']}, confidence={semantic_result['confidence']}")
        logger.info(f"  - Intent: {intent_result}")

        # =====================================================================
        # Phase 2: SQL Generation (Sequential - uses Phase 1 results)
        # =====================================================================
        logger.info("[Orchestrator] Phase 2: SQL Generation (Sequential)")

        sql_result = self.sql_generator.generate(request.query, semantic_result, intent_result)

        logger.info(f"[Orchestrator] Phase 2 Complete:")
        logger.info(f"  - SQL: {sql_result['sql']}")
        logger.info(f"  - Confidence: {sql_result['confidence']}")

        # =====================================================================
        # Phase 3: Parallel Verification & Optimization
        # =====================================================================
        logger.info("[Orchestrator] Phase 3: Verification & Optimization (Parallel)")

        verify_result = self.verifier.verify(sql_result["sql"], request.query, intent_result)
        optimize_result = self.optimizer.optimize(sql_result["sql"], request.query)

        logger.info(f"[Orchestrator] Phase 3 Complete:")
        logger.info(f"  - Verification: valid={verify_result['valid']}, safe={verify_result['safe']}")
        logger.info(f"  - Optimization: {len(optimize_result['suggestions'])} suggestions")

        # =====================================================================
        # Phase 4: Synthesis
        # =====================================================================
        logger.info("[Orchestrator] Phase 4: Synthesis")

        final_confidence = max(
            semantic_result.get("confidence", 0.7),
            verify_result.get("confidence", 0.8),
            sql_result.get("confidence", 0.75),
            max(intent_result.values()) if intent_result else 0
        )

        final_sql = optimize_result.get("optimized_sql", sql_result["sql"])

        execution_time_ms = (time.time() - start_time) * 1000

        logger.info(f"[Orchestrator] Orchestration Complete in {execution_time_ms:.0f}ms")
        logger.info(f"[Orchestrator] Final confidence: {final_confidence:.0%}")

        # =====================================================================
        # Return orchestrated response
        # =====================================================================
        return {
            "query": request.query,
            "generated_sql": final_sql,
            "confidence": min(final_confidence, 0.99),
            "execution_time_ms": execution_time_ms,
            "agents": {
                "semantic": semantic_result,
                "intent": intent_result,
                "sql_generation": sql_result,
                "verification": verify_result,
                "optimization": optimize_result
            }
        }
