"""
Advanced Code Analyzer

Sophisticated code analysis engine with deep semantic understanding,
pattern recognition, and intelligent insights for programming tasks.
"""

import ast
import re
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import tree_sitter
from tree_sitter import Language, Parser
import structlog

logger = structlog.get_logger(__name__)


class CodeLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"


class AnalysisType(str, Enum):
    """Types of code analysis."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    STRUCTURE = "structure"
    COMPLEXITY = "complexity"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DEPENDENCIES = "dependencies"
    PATTERNS = "patterns"
    DOCUMENTATION = "documentation"


class Severity(str, Enum):
    """Issue severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CodeLocation:
    """Represents a location in source code."""
    file_path: str
    line_start: int
    line_end: int
    column_start: int
    column_end: int


@dataclass
class CodeIssue:
    """Represents a code analysis issue."""
    issue_id: str
    type: str
    severity: Severity
    message: str
    description: str
    location: CodeLocation
    suggestions: List[str]
    metadata: Dict[str, Any]


@dataclass
class CodeMetrics:
    """Code quality and complexity metrics."""
    lines_of_code: int = 0
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0
    technical_debt_ratio: float = 0.0
    test_coverage: float = 0.0
    duplication_ratio: float = 0.0
    documentation_ratio: float = 0.0


@dataclass
class CodeStructure:
    """Represents code structure information."""
    classes: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    imports: List[Dict[str, Any]]
    dependencies: List[str]
    exports: List[Dict[str, Any]]
    interfaces: List[Dict[str, Any]]
    types: List[Dict[str, Any]]


@dataclass
class AnalysisResult:
    """Complete code analysis result."""
    analysis_id: str
    file_path: str
    language: CodeLanguage
    analysis_types: List[AnalysisType]
    metrics: CodeMetrics
    structure: CodeStructure
    issues: List[CodeIssue]
    patterns: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float
    execution_time: float
    metadata: Dict[str, Any]


class CodeAnalyzer:
    """
    Advanced code analyzer with multi-language support and deep semantic analysis.
    
    Provides comprehensive code analysis including syntax validation, semantic
    understanding, quality assessment, security analysis, and intelligent insights.
    """
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.analyzer_id = str(uuid.uuid4())
        self.logger = structlog.get_logger(__name__).bind(analyzer_id=self.analyzer_id)
        
        # Language parsers
        self.parsers: Dict[CodeLanguage, Parser] = {}
        self.languages: Dict[CodeLanguage, Language] = {}
        
        # Analysis rules and patterns
        self.quality_rules = self._load_quality_rules()
        self.security_patterns = self._load_security_patterns()
        self.performance_patterns = self._load_performance_patterns()
        self.design_patterns = self._load_design_patterns()
        
        # Initialize parsers
        self._initialize_parsers()
    
    def _initialize_parsers(self) -> None:
        """Initialize Tree-sitter parsers for supported languages."""
        try:
            # This would typically load compiled language libraries
            # For now, we'll simulate the initialization
            self.logger.info("Initializing language parsers")
            
            # In a real implementation, you would:
            # 1. Build Tree-sitter language libraries
            # 2. Load them into Language objects
            # 3. Create parsers for each language
            
            # Example for Python (would need actual compiled library):
            # python_lang = Language(tree_sitter_python.language(), "python")
            # python_parser = Parser()
            # python_parser.set_language(python_lang)
            # self.parsers[CodeLanguage.PYTHON] = python_parser
            
        except Exception as e:
            self.logger.error("Failed to initialize parsers", error=str(e))
    
    async def analyze_code(
        self,
        code: str,
        file_path: str = "",
        language: Optional[CodeLanguage] = None,
        analysis_types: Optional[List[AnalysisType]] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive code analysis.
        
        Args:
            code: Source code to analyze
            file_path: Path to the source file
            language: Programming language (auto-detected if not provided)
            analysis_types: Types of analysis to perform (all if not provided)
        
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        self.logger.info(
            "Starting code analysis",
            analysis_id=analysis_id,
            file_path=file_path,
            code_length=len(code)
        )
        
        try:
            # Auto-detect language if not provided
            if language is None:
                language = self._detect_language(code, file_path)
            
            # Default to all analysis types if not specified
            if analysis_types is None:
                analysis_types = list(AnalysisType)
            
            # Initialize result structure
            result = AnalysisResult(
                analysis_id=analysis_id,
                file_path=file_path,
                language=language,
                analysis_types=analysis_types,
                metrics=CodeMetrics(),
                structure=CodeStructure(
                    classes=[], functions=[], variables=[], imports=[],
                    dependencies=[], exports=[], interfaces=[], types=[]
                ),
                issues=[],
                patterns=[],
                suggestions=[],
                confidence=0.0,
                execution_time=0.0,
                metadata={}
            )
            
            # Perform requested analyses
            if AnalysisType.SYNTAX in analysis_types:
                await self._analyze_syntax(code, language, result)
            
            if AnalysisType.SEMANTIC in analysis_types:
                await self._analyze_semantics(code, language, result)
            
            if AnalysisType.STRUCTURE in analysis_types:
                await self._analyze_structure(code, language, result)
            
            if AnalysisType.COMPLEXITY in analysis_types:
                await self._analyze_complexity(code, language, result)
            
            if AnalysisType.QUALITY in analysis_types:
                await self._analyze_quality(code, language, result)
            
            if AnalysisType.SECURITY in analysis_types:
                await self._analyze_security(code, language, result)
            
            if AnalysisType.PERFORMANCE in analysis_types:
                await self._analyze_performance(code, language, result)
            
            if AnalysisType.DEPENDENCIES in analysis_types:
                await self._analyze_dependencies(code, language, result)
            
            if AnalysisType.PATTERNS in analysis_types:
                await self._analyze_patterns(code, language, result)
            
            if AnalysisType.DOCUMENTATION in analysis_types:
                await self._analyze_documentation(code, language, result)
            
            # Calculate overall confidence
            result.confidence = self._calculate_confidence(result)
            result.execution_time = time.time() - start_time
            
            self.logger.info(
                "Code analysis completed",
                analysis_id=analysis_id,
                issues_found=len(result.issues),
                confidence=result.confidence,
                execution_time=result.execution_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Code analysis failed", analysis_id=analysis_id, error=str(e))
            raise
    
    def _detect_language(self, code: str, file_path: str) -> CodeLanguage:
        """Auto-detect programming language from code and file path."""
        # Check file extension first
        if file_path:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            extension_map = {
                '.py': CodeLanguage.PYTHON,
                '.js': CodeLanguage.JAVASCRIPT,
                '.ts': CodeLanguage.TYPESCRIPT,
                '.java': CodeLanguage.JAVA,
                '.cpp': CodeLanguage.CPP,
                '.cc': CodeLanguage.CPP,
                '.cxx': CodeLanguage.CPP,
                '.rs': CodeLanguage.RUST,
                '.go': CodeLanguage.GO,
                '.cs': CodeLanguage.CSHARP,
                '.rb': CodeLanguage.RUBY,
                '.php': CodeLanguage.PHP,
            }
            
            if extension in extension_map:
                return extension_map[extension]
        
        # Analyze code patterns for language detection
        patterns = {
            CodeLanguage.PYTHON: [
                r'def\s+\w+\s*\(',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'if\s+__name__\s*==\s*["\']__main__["\']',
            ],
            CodeLanguage.JAVASCRIPT: [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'require\s*\(',
            ],
            CodeLanguage.TYPESCRIPT: [
                r'interface\s+\w+',
                r'type\s+\w+\s*=',
                r':\s*\w+\s*=',
                r'export\s+interface',
            ],
            CodeLanguage.JAVA: [
                r'public\s+class\s+\w+',
                r'public\s+static\s+void\s+main',
                r'import\s+java\.',
                r'@\w+',
            ],
        }
        
        scores = {}
        for language, language_patterns in patterns.items():
            score = 0
            for pattern in language_patterns:
                if re.search(pattern, code, re.MULTILINE):
                    score += 1
            scores[language] = score
        
        # Return language with highest score, default to Python
        if scores:
            return max(scores, key=scores.get)
        
        return CodeLanguage.PYTHON
    
    async def _analyze_syntax(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code syntax and detect syntax errors."""
        try:
            if language == CodeLanguage.PYTHON:
                # Use Python AST for syntax analysis
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    issue = CodeIssue(
                        issue_id=str(uuid.uuid4()),
                        type="syntax_error",
                        severity=Severity.CRITICAL,
                        message=f"Syntax error: {e.msg}",
                        description=f"Python syntax error at line {e.lineno}",
                        location=CodeLocation(
                            file_path=result.file_path,
                            line_start=e.lineno or 1,
                            line_end=e.lineno or 1,
                            column_start=e.offset or 1,
                            column_end=e.offset or 1
                        ),
                        suggestions=["Fix the syntax error before proceeding"],
                        metadata={"error_type": "syntax", "python_error": str(e)}
                    )
                    result.issues.append(issue)
            
            # For other languages, we would use Tree-sitter or language-specific parsers
            
        except Exception as e:
            self.logger.error("Syntax analysis failed", error=str(e))
    
    async def _analyze_semantics(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code semantics and meaning."""
        # This would involve more sophisticated analysis
        # For now, we'll do basic semantic checks
        
        if language == CodeLanguage.PYTHON:
            try:
                tree = ast.parse(code)
                
                # Check for undefined variables (basic analysis)
                defined_vars = set()
                used_vars = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Store):
                            defined_vars.add(node.id)
                        elif isinstance(node.ctx, ast.Load):
                            used_vars.add(node.id)
                
                # Find potentially undefined variables
                undefined_vars = used_vars - defined_vars - {'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple'}
                
                for var in undefined_vars:
                    issue = CodeIssue(
                        issue_id=str(uuid.uuid4()),
                        type="undefined_variable",
                        severity=Severity.MEDIUM,
                        message=f"Potentially undefined variable: {var}",
                        description=f"Variable '{var}' is used but may not be defined",
                        location=CodeLocation(
                            file_path=result.file_path,
                            line_start=1, line_end=1, column_start=1, column_end=1
                        ),
                        suggestions=[f"Define variable '{var}' before using it"],
                        metadata={"variable_name": var}
                    )
                    result.issues.append(issue)
                    
            except Exception as e:
                self.logger.error("Semantic analysis failed", error=str(e))
    
    async def _analyze_structure(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code structure and extract components."""
        if language == CodeLanguage.PYTHON:
            try:
                tree = ast.parse(code)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "line_start": node.lineno,
                            "line_end": getattr(node, 'end_lineno', node.lineno),
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                            "docstring": ast.get_docstring(node),
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                        }
                        result.structure.functions.append(func_info)
                    
                    elif isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "line_start": node.lineno,
                            "line_end": getattr(node, 'end_lineno', node.lineno),
                            "bases": [ast.unparse(base) for base in node.bases],
                            "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                            "docstring": ast.get_docstring(node),
                            "methods": [],
                        }
                        
                        # Extract methods
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = {
                                    "name": item.name,
                                    "line_start": item.lineno,
                                    "args": [arg.arg for arg in item.args.args],
                                    "is_property": any(
                                        isinstance(dec, ast.Name) and dec.id == 'property'
                                        for dec in item.decorator_list
                                    ),
                                }
                                class_info["methods"].append(method_info)
                        
                        result.structure.classes.append(class_info)
                    
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            import_info = {
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                                "type": "import"
                            }
                            result.structure.imports.append(import_info)
                    
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            import_info = {
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                                "type": "from_import"
                            }
                            result.structure.imports.append(import_info)
                            
            except Exception as e:
                self.logger.error("Structure analysis failed", error=str(e))
    
    async def _analyze_complexity(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code complexity metrics."""
        if language == CodeLanguage.PYTHON:
            try:
                tree = ast.parse(code)
                
                # Calculate basic metrics
                result.metrics.lines_of_code = len(code.splitlines())
                
                # Calculate cyclomatic complexity (simplified)
                complexity = 1  # Base complexity
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        complexity += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity += len(node.values) - 1
                
                result.metrics.cyclomatic_complexity = complexity
                
                # Cognitive complexity (simplified approximation)
                result.metrics.cognitive_complexity = min(complexity * 1.2, 50)
                
                # Maintainability index (simplified calculation)
                loc = result.metrics.lines_of_code
                cc = result.metrics.cyclomatic_complexity
                result.metrics.maintainability_index = max(0, 171 - 5.2 * math.log(loc) - 0.23 * cc)
                
            except Exception as e:
                self.logger.error("Complexity analysis failed", error=str(e))
    
    async def _analyze_quality(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code quality and best practices."""
        # Check for common quality issues
        quality_checks = [
            (r'print\s*\(', "debug_print", "Debug print statement found", Severity.LOW),
            (r'TODO|FIXME|HACK', "todo_comment", "TODO/FIXME comment found", Severity.INFO),
            (r'^\s*#.*$', "comment_line", "Comment found", Severity.INFO),
        ]
        
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern, issue_type, message, severity in quality_checks:
                if re.search(pattern, line, re.IGNORECASE):
                    if issue_type != "comment_line" or "TODO" in line.upper():  # Only report TODO comments
                        issue = CodeIssue(
                            issue_id=str(uuid.uuid4()),
                            type=issue_type,
                            severity=severity,
                            message=message,
                            description=f"Quality issue found at line {i}",
                            location=CodeLocation(
                                file_path=result.file_path,
                                line_start=i, line_end=i,
                                column_start=1, column_end=len(line)
                            ),
                            suggestions=self._get_quality_suggestions(issue_type),
                            metadata={"line_content": line.strip()}
                        )
                        result.issues.append(issue)
    
    async def _analyze_security(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code for security vulnerabilities."""
        security_patterns = [
            (r'eval\s*\(', "code_injection", "Potential code injection vulnerability", Severity.HIGH),
            (r'exec\s*\(', "code_execution", "Dangerous code execution", Severity.HIGH),
            (r'input\s*\(.*\)', "user_input", "Unvalidated user input", Severity.MEDIUM),
            (r'password\s*=\s*["\'][^"\']+["\']', "hardcoded_password", "Hardcoded password", Severity.CRITICAL),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "hardcoded_api_key", "Hardcoded API key", Severity.CRITICAL),
        ]
        
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern, vuln_type, message, severity in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = CodeIssue(
                        issue_id=str(uuid.uuid4()),
                        type=vuln_type,
                        severity=severity,
                        message=message,
                        description=f"Security vulnerability found at line {i}",
                        location=CodeLocation(
                            file_path=result.file_path,
                            line_start=i, line_end=i,
                            column_start=1, column_end=len(line)
                        ),
                        suggestions=self._get_security_suggestions(vuln_type),
                        metadata={"vulnerability_type": vuln_type}
                    )
                    result.issues.append(issue)
    
    async def _analyze_performance(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code for performance issues."""
        # Basic performance pattern detection
        perf_patterns = [
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', "inefficient_loop", "Inefficient loop pattern", Severity.MEDIUM),
            (r'\.append\s*\(.*\)\s*$', "list_append_in_loop", "List append in loop", Severity.LOW),
        ]
        
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern, perf_type, message, severity in perf_patterns:
                if re.search(pattern, line):
                    issue = CodeIssue(
                        issue_id=str(uuid.uuid4()),
                        type=perf_type,
                        severity=severity,
                        message=message,
                        description=f"Performance issue found at line {i}",
                        location=CodeLocation(
                            file_path=result.file_path,
                            line_start=i, line_end=i,
                            column_start=1, column_end=len(line)
                        ),
                        suggestions=self._get_performance_suggestions(perf_type),
                        metadata={"performance_issue": perf_type}
                    )
                    result.issues.append(issue)
    
    async def _analyze_dependencies(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code dependencies."""
        # Extract dependencies from imports
        dependencies = set()
        
        if language == CodeLanguage.PYTHON:
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, code)
                dependencies.update(matches)
        
        result.structure.dependencies = list(dependencies)
    
    async def _analyze_patterns(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code for design patterns and anti-patterns."""
        # Detect common design patterns
        patterns = []
        
        if language == CodeLanguage.PYTHON:
            # Singleton pattern detection
            if re.search(r'class\s+\w+.*:\s*\n.*__new__', code, re.MULTILINE | re.DOTALL):
                patterns.append({
                    "type": "singleton",
                    "name": "Singleton Pattern",
                    "description": "Singleton pattern detected",
                    "confidence": 0.8
                })
            
            # Factory pattern detection
            if re.search(r'def\s+create_\w+|def\s+make_\w+', code):
                patterns.append({
                    "type": "factory",
                    "name": "Factory Pattern",
                    "description": "Factory pattern detected",
                    "confidence": 0.6
                })
        
        result.patterns = patterns
    
    async def _analyze_documentation(self, code: str, language: CodeLanguage, result: AnalysisResult) -> None:
        """Analyze code documentation coverage."""
        if language == CodeLanguage.PYTHON:
            try:
                tree = ast.parse(code)
                
                total_functions = 0
                documented_functions = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1
                
                if total_functions > 0:
                    result.metrics.documentation_ratio = documented_functions / total_functions
                
                # Check for missing docstrings
                if result.metrics.documentation_ratio < 0.5:
                    issue = CodeIssue(
                        issue_id=str(uuid.uuid4()),
                        type="missing_documentation",
                        severity=Severity.MEDIUM,
                        message="Low documentation coverage",
                        description=f"Only {documented_functions}/{total_functions} functions have docstrings",
                        location=CodeLocation(
                            file_path=result.file_path,
                            line_start=1, line_end=1, column_start=1, column_end=1
                        ),
                        suggestions=["Add docstrings to functions and classes"],
                        metadata={"coverage": result.metrics.documentation_ratio}
                    )
                    result.issues.append(issue)
                    
            except Exception as e:
                self.logger.error("Documentation analysis failed", error=str(e))
    
    def _calculate_confidence(self, result: AnalysisResult) -> float:
        """Calculate overall confidence in the analysis."""
        base_confidence = 0.8
        
        # Reduce confidence for syntax errors
        syntax_errors = [issue for issue in result.issues if issue.type == "syntax_error"]
        if syntax_errors:
            base_confidence *= 0.5
        
        # Adjust based on code length
        if result.metrics.lines_of_code < 10:
            base_confidence *= 0.9
        
        return min(base_confidence, 1.0)
    
    def _get_quality_suggestions(self, issue_type: str) -> List[str]:
        """Get suggestions for quality issues."""
        suggestions_map = {
            "debug_print": ["Remove debug print statements", "Use logging instead of print"],
            "todo_comment": ["Address TODO items", "Create tickets for pending work"],
        }
        return suggestions_map.get(issue_type, ["Review and fix this issue"])
    
    def _get_security_suggestions(self, vuln_type: str) -> List[str]:
        """Get suggestions for security vulnerabilities."""
        suggestions_map = {
            "code_injection": ["Avoid using eval()", "Use safer alternatives like ast.literal_eval()"],
            "code_execution": ["Avoid using exec()", "Use safer alternatives"],
            "hardcoded_password": ["Use environment variables", "Use secure credential storage"],
            "hardcoded_api_key": ["Use environment variables", "Use secure configuration management"],
        }
        return suggestions_map.get(vuln_type, ["Review security implications"])
    
    def _get_performance_suggestions(self, perf_type: str) -> List[str]:
        """Get suggestions for performance issues."""
        suggestions_map = {
            "inefficient_loop": ["Use enumerate() instead of range(len())", "Consider list comprehensions"],
            "list_append_in_loop": ["Consider list comprehensions", "Pre-allocate list size if known"],
        }
        return suggestions_map.get(perf_type, ["Review performance implications"])
    
    def _load_quality_rules(self) -> Dict[str, Any]:
        """Load code quality rules."""
        return {}
    
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security vulnerability patterns."""
        return {}
    
    def _load_performance_patterns(self) -> Dict[str, Any]:
        """Load performance issue patterns."""
        return {}
    
    def _load_design_patterns(self) -> Dict[str, Any]:
        """Load design pattern definitions."""
        return {}


# Import time for metrics calculation
import time
import math
