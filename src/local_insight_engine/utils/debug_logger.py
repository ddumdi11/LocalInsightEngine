"""
Enhanced Debug Logger for LocalInsightEngine
Provides comprehensive logging with configurable output paths and detailed debugging capabilities.
"""

import logging
import os
import tempfile
import datetime
import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Union
import json


class LocalInsightDebugLogger:
    """Enhanced logger for LocalInsightEngine with configurable output and detailed debugging"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.log_dir = self._setup_log_directory()
        self.log_file = self._setup_log_file()
        self.logger = self._setup_logger()

        # Performance tracking
        self.performance_data = {}
        self.step_counter = 0

        # Log initialization
        self._log_initialization()

    def _load_config(self, config_path: Optional[Path] = None) -> configparser.ConfigParser:
        """Load configuration from localinsightengine.conf"""
        config = configparser.ConfigParser()

        # Default config path in project root
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / "localinsightengine.conf"

        if config_path.exists():
            config.read(config_path)
        else:
            # Create default config if not exists
            self._create_default_config(config_path)
            config.read(config_path)

        return config

    def _create_default_config(self, config_path: Path):
        """Create default configuration file if it doesn't exist"""
        default_config = """# LocalInsightEngine Configuration File
[Logging]
log_directory = .
log_filename = localinsightengine.log
log_level = DEBUG
console_output = true
max_log_size_mb = 50
backup_count = 5

[Database]
database_path = data/qa_sessions.db
auto_create_db = true
enable_fts5 = true

[Analysis]
default_factual_mode = false
max_qa_chunks = 100
enable_semantic_search = true
min_keyword_length = 3

[Performance]
enable_performance_logging = true
log_chunk_details = true
log_entity_details = true
"""
        config_path.write_text(default_config, encoding='utf-8')

    def _setup_log_directory(self) -> Path:
        """Setup log directory based on configuration"""
        log_dir_config = self.config.get('Logging', 'log_directory', fallback='temp')

        if log_dir_config.lower() == 'temp':
            # Use system temp directory
            log_dir = Path(tempfile.gettempdir()) / "LocalInsightEngine"
        elif log_dir_config == '.':
            # Use project directory
            project_root = Path(__file__).parent.parent.parent.parent
            log_dir = project_root
        else:
            # Use specified directory
            log_dir = Path(log_dir_config)

        log_dir.mkdir(exist_ok=True, parents=True)
        return log_dir

    def _setup_log_file(self) -> Path:
        """Setup log file path"""
        log_filename = self.config.get('Logging', 'log_filename', fallback='localinsightengine.log')
        return self.log_dir / log_filename

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("LocalInsightEngine")

        # Set log level from config
        log_level = self.config.get('Logging', 'log_level', fallback='DEBUG')
        logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        max_size = self.config.getint('Logging', 'max_log_size_mb', fallback=50) * 1024 * 1024
        backup_count = self.config.getint('Logging', 'backup_count', fallback=5)

        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler (optional)
        console_output = self.config.getboolean('Logging', 'console_output', fallback=True)
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

        # Enhanced formatter with more details
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        if console_output:
            console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        if console_output:
            logger.addHandler(console_handler)

        return logger

    def _log_initialization(self):
        """Log initialization information"""
        self.logger.info("=" * 80)
        self.logger.info(f"LocalInsightEngine Debug Logger - {datetime.datetime.now()}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"Log directory: {self.log_dir}")
        self.logger.info(f"Configuration loaded from: {self.config}")
        self.logger.info("=" * 80)

    def step(self, step_name: str, details: Dict[str, Any] = None):
        """Log a major step in the analysis process"""
        self.step_counter += 1
        self.logger.info(f"STEP {self.step_counter}: {step_name}")
        if details:
            for key, value in details.items():
                self.logger.info(f"  {key}: {value}")

    def debug(self, message: str, data: Any = None):
        """Log debug information"""
        self.logger.debug(f"DEBUG: {message}")
        if data is not None:
            if isinstance(data, (dict, list)):
                self.logger.debug(f"  Data: {json.dumps(data, indent=2, default=str)}")
            else:
                self.logger.debug(f"  Data: {data}")

    def info(self, message: str, data: Any = None):
        """Log info information"""
        self.logger.info(f"INFO: {message}")
        if data is not None:
            self.logger.info(f"  Data: {data}")

    def warning(self, message: str, data: Any = None):
        """Log warning information"""
        self.logger.warning(f"WARNING: {message}")
        if data is not None:
            self.logger.warning(f"  Data: {data}")

    def error(self, message: str, exception: Exception = None, data: Any = None):
        """Log error information"""
        self.logger.error(f"ERROR: {message}")
        if exception:
            self.logger.error(f"  Exception: {exception}")
            self.logger.error(f"  Type: {type(exception).__name__}")
            import traceback
            self.logger.error(f"  Traceback: {traceback.format_exc()}")
        if data is not None:
            self.logger.error(f"  Data: {data}")

    def performance_start(self, operation: str):
        """Start performance tracking for an operation"""
        if self.config.getboolean('Performance', 'enable_performance_logging', fallback=True):
            import time
            self.performance_data[operation] = {
                'start_time': time.time(),
                'start_timestamp': datetime.datetime.now()
            }
            self.logger.debug(f"PERF START: {operation}")

    def performance_end(self, operation: str, details: Dict[str, Any] = None):
        """End performance tracking for an operation"""
        if self.config.getboolean('Performance', 'enable_performance_logging', fallback=True):
            import time
            if operation in self.performance_data:
                end_time = time.time()
                duration = end_time - self.performance_data[operation]['start_time']

                self.logger.info(f"PERF END: {operation} - Duration: {duration:.3f}s")
                if details:
                    for key, value in details.items():
                        self.logger.info(f"  {key}: {value}")

                # Clean up
                del self.performance_data[operation]
            else:
                self.logger.warning(f"PERF END: {operation} - No start time recorded")

    def file_info(self, file_path: Union[str, Path], description: str = ""):
        """Log file information"""
        file_path = Path(file_path)
        if file_path.exists():
            size = file_path.stat().st_size
            self.logger.info(f"FILE: {description} - {file_path}")
            self.logger.info(f"  Size: {size} bytes ({size / 1024:.1f} KB)")
            self.logger.info(f"  Modified: {datetime.datetime.fromtimestamp(file_path.stat().st_mtime)}")
        else:
            self.logger.error(f"FILE NOT FOUND: {description} - {file_path}")

    def document_analysis(self, doc_path: Path, stats: Dict[str, Any]):
        """Log document analysis statistics"""
        self.logger.info(f"DOCUMENT ANALYSIS: {doc_path.name}")
        for key, value in stats.items():
            self.logger.info(f"  {key}: {value}")

    def chunk_details(self, chunk_id: str, chunk_data: Dict[str, Any]):
        """Log detailed chunk information"""
        if self.config.getboolean('Performance', 'log_chunk_details', fallback=True):
            self.logger.debug(f"CHUNK: {chunk_id}")
            for key, value in chunk_data.items():
                if key == 'content' and len(str(value)) > 200:
                    self.logger.debug(f"  {key}: {str(value)[:200]}... (truncated)")
                else:
                    self.logger.debug(f"  {key}: {value}")

    def entity_extraction(self, entities: list, source: str = ""):
        """Log entity extraction results"""
        if self.config.getboolean('Performance', 'log_entity_details', fallback=True):
            self.logger.info(f"ENTITIES EXTRACTED: {len(entities)} from {source}")
            for i, entity in enumerate(entities[:10]):  # Log first 10 entities
                if isinstance(entity, dict):
                    self.logger.debug(f"  {i+1}: {entity}")
                else:
                    self.logger.debug(f"  {i+1}: {entity}")
            if len(entities) > 10:
                self.logger.debug(f"  ... and {len(entities) - 10} more entities")

    def database_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log database operations"""
        self.logger.info(f"DATABASE: {operation}")
        if details:
            for key, value in details.items():
                self.logger.info(f"  {key}: {value}")

    def qa_session(self, question: str, answer: str, context_chunks: int, confidence: float = None):
        """Log Q&A session details"""
        self.logger.info(f"Q&A SESSION:")
        self.logger.info(f"  Question: {question}")
        self.logger.info(f"  Answer length: {len(answer)} characters")
        self.logger.info(f"  Context chunks used: {context_chunks}")
        if confidence is not None:
            self.logger.info(f"  Confidence: {confidence}")
        self.logger.debug(f"  Full Answer: {answer}")

    def test_dependencies(self):
        """Test and log all LocalInsightEngine dependencies"""
        self.step("Testing LocalInsightEngine Dependencies")

        dependencies = [
            'spacy', 'sqlalchemy', 'pydantic', 'anthropic',
            'pathlib', 'logging', 'sqlite3', 'configparser'
        ]

        for dep in dependencies:
            try:
                __import__(dep)
                self.logger.info(f"✅ {dep}: Available")
            except ImportError as e:
                self.logger.error(f"❌ {dep}: Failed")
                self.error(f"{dep} import failed", e)

        # Test spaCy models
        try:
            import spacy
            models = ['de_core_news_sm', 'en_core_web_sm']
            for model in models:
                try:
                    nlp = spacy.load(model)
                    self.logger.info(f"✅ spaCy model {model}: Available")
                except OSError:
                    self.logger.warning(f"⚠️ spaCy model {model}: Not installed")
        except ImportError:
            self.logger.error("❌ spaCy: Not available")

    def get_log_path(self) -> str:
        """Return the path to the log file"""
        return str(self.log_file)

    def get_config_value(self, section: str, key: str, fallback: Any = None):
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)


# Global logger instance
debug_logger = LocalInsightDebugLogger()