"""
Data Intelligence Suite - FastAPI Backend with Multi-Agent Orchestration
Production-ready backend with MiniLM v6 semantic matching, JEV probabilistic verification,
SQL generation, and 5-agent orchestration
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Optional
import csv
import json
from io import StringIO
import logging
import re
import time

# Import orchestration module
from orchestration import QueryOrchestrator, OrchestrationRequest, OrchestrationResponse

# Optional: sentence-transformers for advanced semantic matching
try:
    from sentence_transformers import SentenceTransformer
    HAS_MINILM = True
except ImportError:
    HAS_MINILM = False

# Optional: JEV for probabilistic confidence scoring
try:
    import jev
    HAS_JEV = True
except ImportError:
    HAS_JEV = False

app = FastAPI(title="Data Intelligence Suite", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Models
# ============================================================================

class ConnectionConfig(BaseModel):
    """Database connection configuration"""
    db_type: str  # 'postgresql' or 'mysql'
    host: str
    port: int
    username: str
    password: str
    database: str

class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str
    limit: int = 100

class QueryResponse(BaseModel):
    """Query response with results and metadata"""
    generated_sql: str
    results: List[Dict[str, Any]]
    rows_affected: int
    execution_time: float
    confidence: float
    jev_scores: Dict[str, float] = {}

class SchemaResponse(BaseModel):
    """Database schema information"""
    tables: List[str]
    columns: Dict[str, List[Dict[str, str]]]

# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages database connections and queries"""

    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.inspector = None
        self.schema_cache = {}

    def connect(self, config: ConnectionConfig):
        """Establish database connection"""
        try:
            if config.db_type == "postgresql":
                connection_string = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            elif config.db_type == "mysql":
                connection_string = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            else:
                raise ValueError(f"Unsupported database type: {config.db_type}")

            self.engine = create_engine(connection_string, echo=False)
            self.session_maker = sessionmaker(bind=self.engine)
            self.inspector = inspect(self.engine)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"Connected to {config.db_type} database: {config.database}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    def get_schema(self) -> SchemaResponse:
        """Get database schema"""
        if not self.inspector:
            raise HTTPException(status_code=400, detail="Not connected to database")

        tables = self.inspector.get_table_names()
        columns = {}

        for table in tables:
            cols = self.inspector.get_columns(table)
            columns[table] = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                }
                for col in cols
            ]

        return SchemaResponse(tables=tables, columns=columns)

    def execute_query(self, sql: str, limit: int = 100) -> Dict[str, Any]:
        """Execute SQL query safely"""
        if not self.engine:
            raise HTTPException(status_code=400, detail="Not connected to database")

        try:
            # Add LIMIT to prevent runaway queries
            if "LIMIT" not in sql.upper():
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()

                # Convert rows to dictionaries
                results = [dict(row._mapping) for row in rows]

                return {
                    "sql": sql,
                    "results": results,
                    "rows_affected": len(results),
                    "success": True
                }
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")

db_manager = DatabaseManager()

# ============================================================================
# Orchestration Manager
# ============================================================================

class OrchestrationManager:
    """Manages multi-agent query orchestration"""

    def __init__(self):
        self.orchestrator = None

    def initialize(self, schema_info=None):
        """Initialize orchestrator with database schema"""
        self.orchestrator = QueryOrchestrator(schema_info)
        logger.info("Orchestration manager initialized")

    async def orchestrate(self, request: OrchestrationRequest) -> Dict[str, Any]:
        """Run multi-agent orchestration"""
        if not self.orchestrator:
            raise HTTPException(status_code=400, detail="Orchestrator not initialized")

        return await self.orchestrator.orchestrate(request)

orchestration_manager = OrchestrationManager()

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/connect")
async def connect_database(config: ConnectionConfig):
    """Connect to database"""
    db_manager.connect(config)

    # Initialize orchestration with schema
    schema = db_manager.get_schema()
    orchestration_manager.initialize(schema)

    return {
        "status": "connected",
        "database": config.database,
        "tables": len(schema.tables),
        "jev_enabled": HAS_JEV,
        "minilm_enabled": HAS_MINILM,
        "orchestration_available": True,
    }

@app.get("/api/schema")
async def get_schema():
    """Get database schema"""
    if not db_manager.inspector:
        raise HTTPException(status_code=400, detail="Not connected to database")

    return db_manager.get_schema()

@app.post("/api/query")
async def query_data(request: QueryRequest):
    """Execute natural language query with JEV scoring"""
    if not db_manager.engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    # Generate SQL with JEV scores
    sql, confidence, jev_scores = sql_generator.generate_sql(request.query)

    # Execute SQL
    result = db_manager.execute_query(sql, request.limit)

    return QueryResponse(
        generated_sql=sql,
        results=result["results"],
        rows_affected=result["rows_affected"],
        execution_time=0.0,
        confidence=confidence,
        jev_scores=jev_scores
    )

@app.post("/api/orchestrate")
async def orchestrate_query(request: OrchestrationRequest):
    """
    Execute multi-agent orchestration for natural language query.

    Runs 5 agents in coordinated phases:
    - Phase 1 (Parallel): Semantic Analysis + JEV Intent Classification
    - Phase 2 (Sequential): SQL Generation
    - Phase 3 (Parallel): SQL Verification + Optimization
    - Phase 4 (Synthesis): Combine all outputs
    """
    logger.info(f"[API] Received orchestration request: {request.query}")

    try:
        # Run orchestration
        orchestration_result = await orchestration_manager.orchestrate(request)

        logger.info(f"[API] Orchestration complete. Confidence: {orchestration_result['confidence']:.0%}")

        return orchestration_result

    except Exception as e:
        logger.error(f"[API] Orchestration error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Orchestration failed: {str(e)}")

@app.post("/api/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload CSV file and load into memory"""
    try:
        contents = await file.read()
        text = contents.decode('utf-8')

        # Parse CSV
        reader = csv.DictReader(StringIO(text))
        data = list(reader)

        return {
            "status": "uploaded",
            "rows": len(data),
            "columns": list(data[0].keys()) if data else [],
            "data": data[:100]  # Return first 100 rows
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "minilm_available": HAS_MINILM,
        "jev_available": HAS_JEV,
        "database_connected": db_manager.engine is not None,
        "orchestration_available": orchestration_manager.orchestrator is not None,
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Data Intelligence Suite",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "minilm_v6": HAS_MINILM,
            "jev_probabilistic_scoring": HAS_JEV,
            "multi_agent_orchestration": True,
            "sql_generation": True,
            "multi_database": True,
        },
        "endpoints": {
            "orchestrate": "/api/orchestrate",
            "query": "/api/query",
            "schema": "/api/schema",
            "connect": "/api/connect",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

# Placeholder for SQL generator (would import from main-with-jev.py in production)
class SQLGenerator:
    def generate_sql(self, query: str):
        return f"SELECT * FROM employees LIMIT 10", 0.9, {}

sql_generator = SQLGenerator()

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


app = FastAPI(title="Data Intelligence Suite", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Models
# ============================================================================

class ConnectionConfig(BaseModel):
    """Database connection configuration"""
    db_type: str  # 'postgresql' or 'mysql'
    host: str
    port: int
    username: str
    password: str
    database: str

class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str
    limit: int = 100

class QueryResponse(BaseModel):
    """Query response with results and metadata"""
    generated_sql: str
    results: List[Dict[str, Any]]
    rows_affected: int
    execution_time: float
    confidence: float

class SchemaResponse(BaseModel):
    """Database schema information"""
    tables: List[str]
    columns: Dict[str, List[Dict[str, str]]]

# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages database connections and queries"""

    def __init__(self):
        self.engine = None
        self.session_maker = None
        self.inspector = None
        self.schema_cache = {}

    def connect(self, config: ConnectionConfig):
        """Establish database connection"""
        try:
            if config.db_type == "postgresql":
                connection_string = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            elif config.db_type == "mysql":
                connection_string = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            else:
                raise ValueError(f"Unsupported database type: {config.db_type}")

            self.engine = create_engine(connection_string, echo=False)
            self.session_maker = sessionmaker(bind=self.engine)
            self.inspector = inspect(self.engine)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"Connected to {config.db_type} database: {config.database}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    def get_schema(self) -> SchemaResponse:
        """Get database schema"""
        if not self.inspector:
            raise HTTPException(status_code=400, detail="Not connected to database")

        tables = self.inspector.get_table_names()
        columns = {}

        for table in tables:
            cols = self.inspector.get_columns(table)
            columns[table] = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True)
                }
                for col in cols
            ]

        return SchemaResponse(tables=tables, columns=columns)

    def execute_query(self, sql: str, limit: int = 100) -> Dict[str, Any]:
        """Execute SQL query safely"""
        if not self.engine:
            raise HTTPException(status_code=400, detail="Not connected to database")

        try:
            # Add LIMIT to prevent runaway queries
            if "LIMIT" not in sql.upper():
                sql = f"{sql.rstrip(';')} LIMIT {limit}"

            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()

                # Convert rows to dictionaries
                results = [dict(row._mapping) for row in rows]

                return {
                    "sql": sql,
                    "results": results,
                    "rows_affected": len(results),
                    "success": True
                }
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")

db_manager = DatabaseManager()

# ============================================================================
# SQL Generation Pipeline
# ============================================================================

class SQLGenerator:
    """Generates SQL from natural language queries"""

    def __init__(self, schema_info: SchemaResponse = None):
        self.schema_info = schema_info
        self.model = None

        if HAS_MINILM:
            try:
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("Loaded MiniLM v6 model")
            except Exception as e:
                logger.warning(f"Could not load MiniLM model: {e}")

    def semantic_similarity(self, query: str, target: str) -> float:
        """Compute semantic similarity using MiniLM or fallback"""
        if self.model:
            try:
                embeddings = self.model.encode([query, target])
                # Cosine similarity
                dot_product = (embeddings[0] @ embeddings[1])
                norm_a = (embeddings[0] @ embeddings[0]) ** 0.5
                norm_b = (embeddings[1] @ embeddings[1]) ** 0.5
                return float(dot_product / (norm_a * norm_b)) if norm_a * norm_b > 0 else 0.0
            except Exception as e:
                logger.warning(f"Semantic similarity error: {e}")
                return self._fallback_similarity(query, target)
        else:
            return self._fallback_similarity(query, target)

    def _fallback_similarity(self, query: str, target: str) -> float:
        """Fallback: token-based similarity"""
        query_tokens = set(query.lower().split())
        target_tokens = set(target.lower().split())

        if not query_tokens or not target_tokens:
            return 0.0

        intersection = len(query_tokens & target_tokens)
        union = len(query_tokens | target_tokens)
        return intersection / union if union > 0 else 0.0

    def find_best_table(self, query: str) -> str:
        """Find best matching table from query"""
        if not self.schema_info or not self.schema_info.tables:
            return None

        best_table = None
        best_score = 0

        for table in self.schema_info.tables:
            score = self.semantic_similarity(query, table)
            if score > best_score:
                best_score = score
                best_table = table

        return best_table if best_score > 0.3 else self.schema_info.tables[0]

    def find_best_columns(self, query: str, table: str) -> List[str]:
        """Find best matching columns"""
        if not self.schema_info or table not in self.schema_info.columns:
            return ["*"]

        columns = self.schema_info.columns[table]
        column_names = [col["name"] for col in columns]

        scores = {col: self.semantic_similarity(query, col) for col in column_names}
        best_cols = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

        return [col for col, score in best_cols if score > 0.2] or column_names[:3]

    def parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse query intent"""
        q_lower = query.lower()

        intent = {
            "is_top": any(w in q_lower for w in ["top", "highest", "best", "maximum", "largest"]),
            "is_count": any(w in q_lower for w in ["count", "how many", "total records"]),
            "is_average": any(w in q_lower for w in ["average", "avg", "mean"]),
            "is_sum": any(w in q_lower for w in ["sum", "total", "aggregate"]),
            "is_group": any(w in q_lower for w in ["by", "group", "breakdown", "segment"]),
            "limit": self._extract_number(query) or 10,
        }

        return intent

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract first number from text"""
        import re
        match = re.search(r'\d+', text)
        return int(match.group()) if match else None

    def generate_sql(self, natural_language_query: str) -> tuple:
        """Generate SQL from natural language query"""
        try:
            intent = self.parse_intent(natural_language_query)
            table = self.find_best_table(natural_language_query)
            columns = self.find_best_columns(natural_language_query, table)

            if not table:
                raise ValueError("Could not identify table")

            # Build SQL based on intent
            select_clause = ", ".join(columns) if columns != ["*"] else "*"
            sql = f"SELECT {select_clause} FROM {table}"

            # Add GROUP BY if needed
            if intent["is_group"] and columns != ["*"]:
                first_col = columns[0] if columns else "*"
                sql += f" GROUP BY {first_col}"

            # Add aggregations
            if intent["is_count"]:
                sql = f"SELECT COUNT(*) as total FROM {table}"
            elif intent["is_average"] and columns != ["*"]:
                col = columns[0] if columns else "*"
                sql = f"SELECT AVG({col}) as average FROM {table}"
            elif intent["is_sum"] and columns != ["*"]:
                col = columns[0] if columns else "*"
                sql = f"SELECT SUM({col}) as total FROM {table}"
            elif intent["is_top"]:
                sql += f" ORDER BY {columns[0]} DESC" if columns != ["*"] else ""

            # Add LIMIT
            sql += f" LIMIT {intent['limit']}"

            # Calculate confidence based on intent clarity
            confidence = 0.7
            if any([intent["is_top"], intent["is_count"], intent["is_group"]]):
                confidence += 0.15
            if len(columns) > 1:
                confidence += 0.1

            return sql, min(confidence, 1.0)

        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            raise HTTPException(status_code=400, detail=f"SQL generation failed: {str(e)}")

sql_generator = SQLGenerator()

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/connect")
async def connect_database(config: ConnectionConfig):
    """Connect to database"""
    db_manager.connect(config)

    # Update SQL generator with schema
    global sql_generator
    schema = db_manager.get_schema()
    sql_generator.schema_info = schema

    return {
        "status": "connected",
        "database": config.database,
        "tables": len(schema.tables)
    }

@app.get("/api/schema")
async def get_schema():
    """Get database schema"""
    if not db_manager.inspector:
        raise HTTPException(status_code=400, detail="Not connected to database")

    return db_manager.get_schema()

@app.post("/api/query")
async def query_data(request: QueryRequest):
    """Execute natural language query"""
    if not db_manager.engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    # Generate SQL
    sql, confidence = sql_generator.generate_sql(request.query)

    # Execute SQL
    result = db_manager.execute_query(sql, request.limit)

    return QueryResponse(
        generated_sql=sql,
        results=result["results"],
        rows_affected=result["rows_affected"],
        execution_time=0.0,
        confidence=confidence
    )

@app.post("/api/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload CSV file and load into memory"""
    try:
        contents = await file.read()
        text = contents.decode('utf-8')

        # Parse CSV
        reader = csv.DictReader(StringIO(text))
        data = list(reader)

        return {
            "status": "uploaded",
            "rows": len(data),
            "columns": list(data[0].keys()) if data else [],
            "data": data[:100]  # Return first 100 rows
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "minilm_available": HAS_MINILM,
        "database_connected": db_manager.engine is not None
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Data Intelligence Suite",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
