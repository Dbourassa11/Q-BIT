"""
SGPA FastAPI Application

RESTful API for Sacred Geometric Principles of Alignment services.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from ..agents.data_integrity_scanner import DataIntegrityScannerAgent
from ..agents.sgpa_analyzer import SGPAAnalyzerAgent
from ..core.agent import Task
from ..sgpa.calculators import AlignmentScore, SGPACalculator, ValueCalculator, ValueMetrics
from ..sgpa.optimizer import OptimizationPlan, SGPAOptimizer
from ..sgpa.pattern_engine import PatternRecognitionEngine
from ..sgpa.report_generator import SGPAReportGenerator
from ..sgpa.templates import SGPATemplateLibrary
from ..sgpa.visualizer import SGPAVisualizer

# Create FastAPI app
app = FastAPI(
    title="SGPA API",
    description="Sacred Geometric Principles of Alignment API for data optimization and value assessment",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sgpa_analyzer = None
data_scanner = None
visualizer = SGPAVisualizer()
pattern_engine = PatternRecognitionEngine()
optimizer = SGPAOptimizer()
value_calculator = ValueCalculator()
report_generator = SGPAReportGenerator()
template_library = SGPATemplateLibrary()

# In-memory storage for async tasks and reports
analysis_tasks = {}
reports = {}


# Pydantic models
class AnalysisRequest(BaseModel):
    """Request for SGPA analysis"""
    client_name: str = Field(..., description="Client name")
    project_name: str = Field(..., description="Project name")
    analysis_type: str = Field("system", description="Type of analysis: code, data, or system")
    code: Optional[str] = Field(None, description="Code to analyze (for code analysis)")
    language: Optional[str] = Field("python", description="Programming language")
    data: Optional[Dict] = Field(None, description="Data to analyze")
    system_data: Optional[Dict] = Field(None, description="System data for comprehensive analysis")


class ValueAssessmentRequest(BaseModel):
    """Request for value assessment"""
    integrity_score: float = Field(0.7, ge=0, le=1)
    alignment_score: float = Field(0.7, ge=0, le=1)
    efficiency_gain: float = Field(0.2, ge=0, le=1)
    data_volume: int = Field(10000, gt=0)
    team_size: int = Field(5, gt=0)
    avg_salary: float = Field(100000, gt=0)
    annual_operations: int = Field(50000, gt=0)
    cost_per_operation: float = Field(5.0, gt=0)
    implementation_cost: float = Field(50000, gt=0)


class DataIntegrityRequest(BaseModel):
    """Request for data integrity scan"""
    data: List[Dict] = Field(..., description="Data to scan")
    required_fields: Optional[List[str]] = Field(None, description="Required fields")
    validation_rules: Optional[Dict] = Field(None, description="Validation rules")


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    global sgpa_analyzer, data_scanner
    sgpa_analyzer = SGPAAnalyzerAgent()
    data_scanner = DataIntegrityScannerAgent()
    await sgpa_analyzer.start()
    await data_scanner.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown agents"""
    if sgpa_analyzer:
        await sgpa_analyzer.stop()
    if data_scanner:
        await data_scanner.stop()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "SGPA API",
        "version": "1.0.0",
        "description": "Sacred Geometric Principles of Alignment API",
        "endpoints": {
            "analysis": "/api/v1/analysis",
            "value": "/api/v1/value",
            "integrity": "/api/v1/integrity",
            "templates": "/api/v1/templates",
            "visualizations": "/api/v1/visualizations",
            "reports": "/api/v1/reports",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "sgpa_analyzer": "active" if sgpa_analyzer else "inactive",
            "data_scanner": "active" if data_scanner else "inactive",
        },
    }


# SGPA Analysis Endpoints
@app.post("/api/v1/analysis")
async def create_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Create a new SGPA analysis

    Analyzes code, data, or system using sacred geometry principles
    """
    if not sgpa_analyzer:
        raise HTTPException(status_code=503, detail="SGPA Analyzer not initialized")

    task_id = str(uuid.uuid4())

    # Create task for agent
    metadata = {
        "task_type": f"analyze_{request.analysis_type}",
        "client_name": request.client_name,
        "project_name": request.project_name,
    }

    if request.analysis_type == "code":
        metadata["code"] = request.code
        metadata["language"] = request.language
    elif request.analysis_type == "data":
        metadata["data"] = request.data
    else:  # system
        metadata["system_data"] = request.system_data or {}

    task = Task(
        task_id=task_id,
        task_type="sgpa_analysis",
        metadata=metadata,
    )

    # Store task
    analysis_tasks[task_id] = {
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "request": request.dict(),
    }

    # Execute analysis in background
    background_tasks.add_task(execute_analysis, task_id, task)

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Analysis started. Use GET /api/v1/analysis/{task_id} to check status",
    }


async def execute_analysis(task_id: str, task: Task):
    """Execute analysis task"""
    try:
        result = await sgpa_analyzer.execute_task(task)
        analysis_tasks[task_id]["status"] = "completed"
        analysis_tasks[task_id]["result"] = result.result
        analysis_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
    except Exception as e:
        analysis_tasks[task_id]["status"] = "failed"
        analysis_tasks[task_id]["error"] = str(e)
        analysis_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/api/v1/analysis/{task_id}")
async def get_analysis(task_id: str):
    """Get analysis results by task ID"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    return analysis_tasks[task_id]


@app.get("/api/v1/analysis")
async def list_analyses():
    """List all analysis tasks"""
    return {
        "total": len(analysis_tasks),
        "tasks": [
            {
                "task_id": tid,
                "status": task["status"],
                "created_at": task["created_at"],
                "client_name": task["request"].get("client_name"),
                "project_name": task["request"].get("project_name"),
            }
            for tid, task in analysis_tasks.items()
        ],
    }


# Value Assessment Endpoints
@app.post("/api/v1/value")
async def calculate_value(request: ValueAssessmentRequest):
    """
    Calculate comprehensive value metrics

    Returns ROI, cost savings, and value delivered
    """
    value_metrics = value_calculator.calculate_comprehensive_value(
        integrity_score=request.integrity_score,
        alignment_score=request.alignment_score,
        efficiency_gain=request.efficiency_gain,
        data_volume=request.data_volume,
        team_size=request.team_size,
        avg_salary=request.avg_salary,
        annual_operations=request.annual_operations,
        cost_per_operation=request.cost_per_operation,
        implementation_cost=request.implementation_cost,
    )

    return {
        "value_metrics": {
            "total_value_score": value_metrics.total_value_score,
            "data_integrity_value": value_metrics.data_integrity_value,
            "optimization_value": value_metrics.optimization_value,
            "alignment_value": value_metrics.alignment_value,
            "efficiency_gain_value": value_metrics.efficiency_gain_value,
            "time_savings_hours": value_metrics.time_savings_hours,
            "cost_savings": value_metrics.cost_savings,
            "roi_percentage": value_metrics.roi_percentage,
            "payback_period_months": value_metrics.payback_period_months,
        },
        "summary": {
            "annual_benefit": value_metrics.cost_savings + value_metrics.efficiency_gain_value,
            "3_year_benefit": (value_metrics.cost_savings + value_metrics.efficiency_gain_value) * 3,
            "recommendation": "Proceed with optimization" if value_metrics.roi_percentage > 100 else "Review carefully",
        },
    }


# Data Integrity Endpoints
@app.post("/api/v1/integrity")
async def scan_data_integrity(request: DataIntegrityRequest, background_tasks: BackgroundTasks):
    """
    Scan data integrity

    Returns integrity score, issues found, and recommendations
    """
    if not data_scanner:
        raise HTTPException(status_code=503, detail="Data Scanner not initialized")

    task_id = str(uuid.uuid4())

    task = Task(
        task_id=task_id,
        task_type="data_integrity",
        metadata={
            "task_type": "scan_full",
            "data": request.data,
            "required_fields": request.required_fields or [],
            "validation_rules": request.validation_rules or {},
        },
    )

    analysis_tasks[task_id] = {
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(execute_integrity_scan, task_id, task)

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Scan started. Use GET /api/v1/integrity/{task_id} to check status",
    }


async def execute_integrity_scan(task_id: str, task: Task):
    """Execute integrity scan"""
    try:
        result = await data_scanner.execute_task(task)
        analysis_tasks[task_id]["status"] = "completed"
        analysis_tasks[task_id]["result"] = result.result
        analysis_tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
    except Exception as e:
        analysis_tasks[task_id]["status"] = "failed"
        analysis_tasks[task_id]["error"] = str(e)


@app.get("/api/v1/integrity/{task_id}")
async def get_integrity_scan(task_id: str):
    """Get integrity scan results"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Scan task not found")

    return analysis_tasks[task_id]


# Templates & Protocols Endpoints
@app.get("/api/v1/templates")
async def get_templates():
    """Get all SGPA templates and protocols"""
    return {
        "templates": template_library.get_all_templates(),
        "total_count": len(template_library.get_all_templates()),
    }


@app.get("/api/v1/templates/{template_name}")
async def get_template(template_name: str):
    """Get specific template by name"""
    templates = template_library.get_all_templates()
    if template_name not in templates:
        raise HTTPException(status_code=404, detail="Template not found")

    return templates[template_name]


@app.get("/api/v1/templates/category/{category}")
async def get_templates_by_category(category: str):
    """Get templates filtered by category"""
    templates = template_library.get_template_by_category(category)
    if not templates:
        raise HTTPException(status_code=404, detail=f"No templates found for category: {category}")

    return {"category": category, "templates": templates, "count": len(templates)}


# Visualization Endpoints
@app.get("/api/v1/visualizations/golden-spiral")
async def get_golden_spiral():
    """Generate golden spiral SVG"""
    svg = visualizer.generate_golden_spiral()
    return HTMLResponse(content=svg, media_type="image/svg+xml")


@app.get("/api/v1/visualizations/flower-of-life")
async def get_flower_of_life():
    """Generate Flower of Life SVG"""
    svg = visualizer.generate_flower_of_life()
    return HTMLResponse(content=svg, media_type="image/svg+xml")


@app.get("/api/v1/visualizations/metatrons-cube")
async def get_metatrons_cube():
    """Generate Metatron's Cube SVG"""
    svg = visualizer.generate_metatrons_cube()
    return HTMLResponse(content=svg, media_type="image/svg+xml")


@app.get("/api/v1/visualizations/alignment-gauge")
async def get_alignment_gauge(score: float = 0.75, label: str = "Alignment Score"):
    """Generate alignment gauge SVG"""
    if not 0 <= score <= 1:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 1")

    svg = visualizer.generate_alignment_gauge(score, label)
    return HTMLResponse(content=svg, media_type="image/svg+xml")


# Report Endpoints
@app.post("/api/v1/reports")
async def generate_report(
    task_id: str,
    client_info: Dict,
    value_params: Optional[ValueAssessmentRequest] = None,
):
    """
    Generate comprehensive SGPA report

    Requires completed analysis task_id
    """
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    if analysis_tasks[task_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    analysis_result = analysis_tasks[task_id]["result"]

    # Create alignment score
    alignment_data = analysis_result.get("alignment", {})
    alignment = AlignmentScore(
        overall_score=alignment_data.get("overall_score", 0.5),
        golden_ratio_alignment=alignment_data.get("golden_ratio", 0.5),
        fibonacci_alignment=alignment_data.get("fibonacci", 0.5),
        symmetry_alignment=alignment_data.get("symmetry", 0.5),
        harmonic_alignment=alignment_data.get("harmonic", 0.5),
        flow_alignment=alignment_data.get("flow", 0.5),
        details={},
    )

    # Calculate value metrics if not provided
    if value_params:
        value_metrics = value_calculator.calculate_comprehensive_value(
            integrity_score=value_params.integrity_score,
            alignment_score=alignment.overall_score,
            efficiency_gain=value_params.efficiency_gain,
            data_volume=value_params.data_volume,
            team_size=value_params.team_size,
            avg_salary=value_params.avg_salary,
            annual_operations=value_params.annual_operations,
            cost_per_operation=value_params.cost_per_operation,
            implementation_cost=value_params.implementation_cost,
        )
    else:
        # Default value metrics
        value_metrics = ValueMetrics(
            total_value_score=0.7,
            data_integrity_value=50000,
            optimization_value=30000,
            alignment_value=20000,
            efficiency_gain_value=25000,
            time_savings_hours=500,
            cost_savings=80000,
            roi_percentage=250,
            payback_period_months=4.8,
        )

    # Create optimization plan
    optimization_plan = optimizer.create_optimization_plan(alignment, {})

    # Generate report
    report = report_generator.generate_complete_report(
        client_info=client_info,
        alignment=alignment,
        value_metrics=value_metrics,
        optimization_plan=optimization_plan,
        patterns_detected=analysis_result.get("structure_analysis", {}).get("patterns_detected", []),
    )

    # Store report
    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "report": report,
        "generated_at": datetime.utcnow().isoformat(),
        "task_id": task_id,
    }

    return {
        "report_id": report_id,
        "report": report,
        "download_links": {
            "json": f"/api/v1/reports/{report_id}/download?format=json",
            "html": f"/api/v1/reports/{report_id}/download?format=html",
        },
    }


@app.get("/api/v1/reports/{report_id}")
async def get_report(report_id: str):
    """Get report by ID"""
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")

    return reports[report_id]


@app.get("/api/v1/reports/{report_id}/download")
async def download_report(report_id: str, format: str = "json"):
    """Download report in specified format"""
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")

    report = reports[report_id]["report"]

    if format == "json":
        return JSONResponse(content=report)
    elif format == "html":
        html_content = report_generator._generate_html_report(report)
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'html'")


# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Interactive SGPA dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>SGPA Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { color: white; text-align: center; margin-bottom: 40px; font-size: 48px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); transition: transform 0.3s; }
            .card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.3); }
            .card h2 { color: #667eea; margin-bottom: 15px; font-size: 24px; }
            .card p { color: #666; line-height: 1.6; margin-bottom: 20px; }
            .btn { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; transition: opacity 0.3s; }
            .btn:hover { opacity: 0.9; }
            .endpoint { background: #f5f5f5; padding: 8px 12px; border-radius: 4px; font-family: monospace; margin: 5px 0; font-size: 14px; }
            .viz-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 40px; }
            .viz-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); text-align: center; }
            .viz-card h3 { color: #667eea; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔮 Sacred Geometric Principles of Alignment Dashboard</h1>

            <div class="grid">
                <div class="card">
                    <h2>📊 SGPA Analysis</h2>
                    <p>Analyze your code, data, or systems using sacred geometry principles for optimal alignment and harmony.</p>
                    <div class="endpoint">POST /api/v1/analysis</div>
                    <div class="endpoint">GET /api/v1/analysis/{task_id}</div>
                </div>

                <div class="card">
                    <h2>💎 Value Assessment</h2>
                    <p>Calculate the true value of optimizations with ROI projections and comprehensive value metrics.</p>
                    <div class="endpoint">POST /api/v1/value</div>
                </div>

                <div class="card">
                    <h2>🔍 Data Integrity</h2>
                    <p>Scan your data for completeness, consistency, and accuracy with sacred geometry validation.</p>
                    <div class="endpoint">POST /api/v1/integrity</div>
                    <div class="endpoint">GET /api/v1/integrity/{task_id}</div>
                </div>

                <div class="card">
                    <h2>📚 Templates & Protocols</h2>
                    <p>Access pre-built optimization templates, formulas, and protocols aligned with sacred geometry.</p>
                    <div class="endpoint">GET /api/v1/templates</div>
                    <div class="endpoint">GET /api/v1/templates/{name}</div>
                </div>

                <div class="card">
                    <h2>📈 Reports</h2>
                    <p>Generate comprehensive SGPA reports with visualizations, roadmaps, and value assessments.</p>
                    <div class="endpoint">POST /api/v1/reports</div>
                    <div class="endpoint">GET /api/v1/reports/{id}/download</div>
                </div>

                <div class="card">
                    <h2>🎨 Visualizations</h2>
                    <p>Sacred geometry visualizations including golden spiral, Flower of Life, and alignment gauges.</p>
                    <div class="endpoint">GET /api/v1/visualizations/*</div>
                </div>
            </div>

            <div class="viz-grid">
                <div class="viz-card">
                    <h3>Golden Spiral</h3>
                    <img src="/api/v1/visualizations/golden-spiral" alt="Golden Spiral" style="max-width: 100%; height: auto;">
                </div>
                <div class="viz-card">
                    <h3>Flower of Life</h3>
                    <img src="/api/v1/visualizations/flower-of-life" alt="Flower of Life" style="max-width: 100%; height: auto;">
                </div>
                <div class="viz-card">
                    <h3>Metatron's Cube</h3>
                    <img src="/api/v1/visualizations/metatrons-cube" alt="Metatron's Cube" style="max-width: 100%; height: auto;">
                </div>
                <div class="viz-card">
                    <h3>Alignment Gauge</h3>
                    <img src="/api/v1/visualizations/alignment-gauge?score=0.85" alt="Alignment Gauge" style="max-width: 100%; height: auto;">
                </div>
            </div>

            <div style="text-align: center; margin-top: 60px; color: white;">
                <p>🌟 Powered by Sacred Geometric Principles of Alignment Framework 🌟</p>
                <p style="margin-top: 10px; opacity: 0.8;">API Documentation: <a href="/docs" style="color: #FFD700;">/docs</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
