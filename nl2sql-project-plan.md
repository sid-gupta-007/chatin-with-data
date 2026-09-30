# NL2SQL Project: Hackathon MVP Plan

## Core Concept
**SQL Natural** - A natural language to SQL query builder with live visualization. Users ask questions in plain English, get generated SQL, executed queries, and visualized results.

## Differentiators
1. **Edge AI** - Uses MiniLM v6 for semantic understanding locally
2. **Visual Query Builder** - Shows the SQL being generated as a flow diagram
3. **Gravity-inspired Visualization** - Results displayed in 3D/webGL format
4. **Schema Learning** - AI learns your database structure over time

## Tech Stack
### Frontend
- **React** + TypeScript for UI
- **Three.js** / **D3.js** for visualizations  
- **Monaco Editor** for SQL editing
- **Tailwind CSS** for styling

### Backend (Choose one)
**Option A (Fullstack)**:
- **FastAPI** (Python) - NL processing + SQL generation
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Demo database

**Option B (Serverless)**:
- **Next.js** API routes
- **Edge functions** for AI processing
- **Supabase** for database + auth

### AI Components
- **MiniLM v6** (sentence-transformers) - Semantic similarity
- **Template-based generation** - SQL pattern matching
- **Zero-shot classification** - Column/table prediction

## MVP Features (24h scope)

### Core (Must Have)
1. **Natural Language Input**
   - Simple text input for questions
   - Auto-complete suggestions based on schema

2. **Schema Analysis**
   - Connect to sample database (Chinook or Northwind)
   - Show table relationships visually

3. **SQL Generation**
   - Basic SELECT queries with WHERE clauses
   - Support for COUNT, SUM, AVG aggregations
   - JOIN detection from natural language

4. **Results Display**
   - Tabular results
   - Simple charts (bar, line, pie)

### Nice to Have (If Time)
5. **Query Visualization**
   - Show SQL execution plan as flow chart
   - Highlight parts of query that map to natural language

6. **Query Correction**
   - "Did you mean?" suggestions for ambiguous terms
   - Confidence scores for generated queries

7. **Export Options**
   - Export as CSV, JSON
   - Copy SQL to clipboard

## Sample Database
Use **Chinook Database** (music store) or **Northwind** (sales):
- 11 tables, clear relationships
- Rich enough for interesting queries
- Well-documented

## Implementation Steps

### Phase 1: Foundation (4h)
1. Set up project structure (frontend + backend)
2. Create sample database connection
3. Basic UI with input and results display

### Phase 2: SQL Generation (6h)
1. Implement schema parser
2. Build template-based SQL generator
3. Integrate MiniLM for semantic matching

### Phase 3: Visualization (4h)
1. Basic charting for results
2. Query visualization (optional)
3. Polish UI/UX

### Phase 4: Polish & Testing (2h)
1. Error handling
2. Performance optimization
3. Demo preparation

## Sample Queries to Support
1. "Show me all customers from London"
2. "How many tracks are in the Rock genre?"
3. "What are the top 5 selling artists?"
4. "Find invoices from January 2023"
5. "Average invoice total per country"

## Mock Data for Demo
Can pre-generate query results for reliable demo

## Success Metrics
- **Accuracy**: 80%+ correct SQL for supported query patterns
- **Latency**: < 2s for query generation + execution
- **Usability**: Non-technical users can get results in 3 clicks

## Presentation Points
- Edge AI with MiniLM v6 (privacy-focused)
- Visual query building (makes SQL accessible)
- Real-time results with gravity-inspired visualization
- Extensible architecture for future features

## Risks & Mitigation
- **Complex queries**: Start with simple patterns, expand gradually
- **Performance**: Cache common queries, use efficient embeddings
- **Ambiguity**: Provide confidence scores and alternatives
- **Database compatibility**: Focus on PostgreSQL/MySQL patterns first