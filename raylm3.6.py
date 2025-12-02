#!/usr/bin/env python3
"""
RayLM v3.6: Enhanced AI-Powered POV-Ray Scene Generator

A robust Python application that generates 3D scenes for POV-Ray using Large Language Models.
Features enhanced error handling, performance monitoring, and improved reliability.

Author: RayLM Development Team
Version: 3.6.0
Date: December 2, 2025
License: MIT
"""

from pathlib import Path
import os
import sys
import subprocess
import time
import uuid
import tempfile
import argparse
import json
from typing import Tuple, Optional, List, Dict, Any, Union
import re
import shutil
import logging
import signal
from datetime import datetime
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
import math
import threading
from functools import wraps

try:
    from openai import OpenAI, APIError, RateLimitError, Timeout
except ImportError:
    print("Error: openai package is required. Install it with: pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv package not found. Environment variables may not be loaded properly.")
    load_dotenv = lambda: None

# Enhanced logging configuration
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up comprehensive logging configuration."""
    logger = logging.getLogger("RayLM")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

load_dotenv()

# Enhanced configuration with dataclasses
@dataclass
class RayLMConfig:
    """Enhanced configuration for RayLM application."""
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    temp_dir: Path = field(default_factory=lambda: Path(tempfile.gettempdir()) / "raylm_temp")
    scene_dir: str = "scenes"
    render_dir: str = "renders"
    povinc_dir: Path = field(default_factory=lambda: Path(__file__).parent / "povinc")
    
    # API Configuration
    base_url: Optional[str] = field(default_factory=lambda: os.getenv("ZAGUAN_BASE_URL"))
    api_key: str = field(default_factory=lambda: os.getenv("ZAGUAN_API_KEY", ""))
    
    # Model Configuration
    generator_model: str = "zaguanai/gemini-3-pro-preview"
    verifier_model: str = "zaguanai/claude-sonnet-4.5-latest"
    
    # Rendering Configuration
    default_width: int = 1920
    default_height: int = 1080
    default_quality: int = 9
    default_timeout: int = 300  # 5 minutes
    
    # Animation Configuration
    default_fps: int = 30
    default_duration: int = 5
    
    # Performance Settings
    max_retries: int = 3
    retry_delay: float = 1.0
    api_timeout: float = 60.0
    
    # Validation Settings
    validate_syntax: bool = True
    backup_generations: bool = True
    cleanup_temp_files: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        if not self.api_key:
            issues.append("ZAGUAN_API_KEY environment variable is required")
        
        if not self.base_url:
            logger.warning("ZAGUAN_BASE_URL not set, using default OpenAI endpoint")
        
        # Validate paths
        if not self.temp_dir.exists():
            try:
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create temp directory {self.temp_dir}: {e}")
        
        return issues

# Custom exceptions for better error handling
class RayLMError(Exception):
    """Base exception for RayLM errors."""
    pass

class RayLMConfigurationError(RayLMError):
    """Configuration-related errors."""
    pass

class RayLMAPIError(RayLMError):
    """API-related errors."""
    pass

class RayLMRenderingError(RayLMError):
    """Rendering-related errors."""
    pass

class RayLMValidationError(RayLMError):
    """Validation-related errors."""
    pass

class RayLMTimeoutError(RayLMError):
    """Timeout-related errors."""
    pass

# Performance monitoring utilities
@dataclass
class PerformanceMetrics:
    """Performance tracking for operations."""
    operation: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def complete(self, error: Optional[str] = None) -> None:
        """Mark operation as complete."""
        self.end_time = time.time()
        if error:
            self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            'duration': self.duration,
            'error': self.error,
            'metadata': self.metadata
        }

# Advanced validation system
class ValidationSystem:
    """Comprehensive validation for scene generation pipeline."""
    
    @staticmethod
    def validate_prompt(prompt: str) -> Tuple[bool, List[str]]:
        """Validate prompt for scene generation."""
        errors = []
        
        if not prompt or not prompt.strip():
            errors.append("Prompt cannot be empty")
        
        if len(prompt.strip()) < 5:
            errors.append("Prompt must be at least 5 characters long")
        
        # Check for potentially problematic content
        dangerous_patterns = ['exec(', 'eval(', 'system(', 'subprocess']
        for pattern in dangerous_patterns:
            if pattern in prompt.lower():
                errors.append(f"Prompt contains potentially dangerous pattern: {pattern}")
        
        # Check for language patterns that might confuse AI
        if prompt.count('{') != prompt.count('}'):
            errors.append("Unbalanced braces in prompt")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_scene_code(scene_code: str) -> Tuple[bool, List[str]]:
        """Comprehensive validation of POV-Ray scene code."""
        errors = []
        warnings = []
        
        if not scene_code or not scene_code.strip():
            errors.append("Scene code cannot be empty")
            return False, errors
        
        # Check for balanced braces
        open_braces = scene_code.count('{')
        close_braces = scene_code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")
        
        # Check for common POV-Ray includes
        required_includes = ['colors.inc', 'textures.inc', 'finish.inc']
        for include in required_includes:
            if f'#include "{include}"' not in scene_code and f'#include "{include}"\n' not in scene_code:
                warnings.append(f"Scene code may be missing include: {include}")
        
        # Check for basic POV-Ray structure
        if 'camera' not in scene_code.lower():
            warnings.append("No camera definition found in scene")
        
        if 'light_source' not in scene_code.lower():
            warnings.append("No light source definition found in scene")
        
        # Check for common syntax issues
        syntax_patterns = [
            (r'camera\s*{[^}]*location\s*\(\s*[^)]*\)\s*}', "Camera location found"),
            (r'camera\s*{[^}]*look_at\s*\(\s*[^)]*\)\s*}', "Camera look_at found"),
        ]
        
        for pattern, description in syntax_patterns:
            if not re.search(pattern, scene_code, re.IGNORECASE | re.DOTALL):
                warnings.append(f"{description} may be incomplete")
        
        # Log warnings
        for warning in warnings:
            logger.warning(warning)
        
        return len(errors) == 0, errors + warnings
    
    @staticmethod
    def validate_resolution(width: int, height: int) -> Tuple[bool, List[str]]:
        """Validate render resolution."""
        errors = []
        
        if width is None or height is None:
            errors.append("Width and height cannot be None")
            return False, errors
        
        if width <= 0 or height <= 0:
            errors.append("Width and height must be positive")
        
        if width > 8192 or height > 8192:
            errors.append("Resolution too high (maximum 8192x8192)")
        
        if width * height > 50_000_000:  # 50MP limit
            errors.append("Resolution too high (maximum 50 megapixels)")
        
        return len(errors) == 0, errors

# Enhanced file management
class FileManager:
    """Advanced file and directory management."""
    
    def __init__(self, config: RayLMConfig):
        self.config = config
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.config.output_dir,
            self.config.output_dir / self.config.scene_dir,
            self.config.output_dir / self.config.render_dir,
            self.config.temp_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    def create_scene_filename(self, prompt: str, timestamp: Optional[str] = None) -> Path:
        """Create a safe filename for scene code."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize prompt for filename
        safe_prompt = re.sub(r'[^\w\s-]', '', prompt.lower())
        safe_prompt = re.sub(r'[-\s]+', '_', safe_prompt)
        safe_prompt = safe_prompt[:30].strip('_')
        
        return self.config.output_dir / self.config.scene_dir / f"scene_{timestamp}_{safe_prompt}.pov"
    
    def create_output_filename(self, prompt: str, timestamp: Optional[str] = None, 
                              extension: str = "png") -> Path:
        """Create a safe filename for rendered output."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize prompt for filename
        safe_prompt = re.sub(r'[^\w\s-]', '', prompt.lower())
        safe_prompt = re.sub(r'[-\s]+', '_', safe_prompt)
        safe_prompt = safe_prompt[:30].strip('_')
        
        return self.config.output_dir / self.config.render_dir / f"render_{timestamp}_{safe_prompt}.{extension}"
    
    def create_temp_filename(self, suffix: str = "", prefix: str = "raylm_") -> Path:
        """Create a temporary file in the temp directory."""
        temp_file = tempfile.mktemp(suffix=suffix, prefix=prefix, dir=str(self.config.temp_dir))
        return Path(temp_file)
    
    def cleanup_temp_files(self, pattern: str = "raylm_*") -> None:
        """Clean up temporary files."""
        if not self.config.cleanup_temp_files:
            return
        
        try:
            for temp_file in self.config.temp_dir.glob(pattern):
                if temp_file.is_file():
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")
    
    def backup_scene(self, scene_code: str, filename: Path) -> Optional[Path]:
        """Create a backup of scene code if enabled."""
        if not self.config.backup_generations:
            return None
        
        try:
            backup_filename = filename.with_suffix('.backup.pov')
            with open(backup_filename, 'w') as f:
                f.write(scene_code)
            logger.debug(f"Scene backup created: {backup_filename}")
            return backup_filename
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            return None
    
    def save_metadata(self, metrics: PerformanceMetrics, filename: Path) -> None:
        """Save performance metadata to JSON file."""
        try:
            metadata_file = filename.with_suffix('.metadata.json')
            metadata = {
                'raylm_version': '3.6.0',
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics.to_dict()
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Metadata saved: {metadata_file}")
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")

# Enhanced LLM client with retry logic
class LLMClient:
    """Enhanced LLM client with retry logic and error handling."""
    
    def __init__(self, config: RayLMConfig):
        self.config = config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            client_config = {"api_key": self.config.api_key}
            if self.config.base_url:
                client_config["base_url"] = self.config.base_url
            
            self._client = OpenAI(**client_config)
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise RayLMConfigurationError(f"Failed to initialize LLM client: {e}")
    
    def generate_scene_code(self, prompt: str, metrics: PerformanceMetrics) -> str:
        """Generate POV-Ray scene code with retry logic."""
        
        # Enhanced system prompt for better code generation
        system_prompt = """You are a professional POV-Ray scene generator with expertise in 3D graphics and rendering.

IMPORTANT REQUIREMENTS:
1. Generate ONLY valid POV-Ray SDL code - no explanations, markdown, or additional text
2. Include these essential includes: colors.inc, textures.inc, finish.inc, metals.inc, stones.inc, woods.inc
3. Always include: camera, lights, and at least one 3D object
4. Use proper POV-Ray syntax and conventions
5. Add helpful comments for complex parts
6. Ensure complete and syntactically correct code
7. Use appropriate materials, textures, and lighting

Example structure:
```
#include "colors.inc"
#include "textures.inc"

// Scene description
camera {
    location <0, 2, -5>
    look_at <0, 1, 0>
}

light_source {
    <10, 10, -10>
    color White
}

object {
    sphere {
        <0, 1, 0>, 1
        texture {
            pigment { color Red }
            finish { specular 0.4 }
        }
    }
}
```
"""
        
        user_prompt = f"""Generate a POV-Ray scene for: {prompt}

Ensure the scene is complete, visually interesting, and uses proper POV-Ray SDL syntax. Include all necessary components (camera, lights, objects, materials)."""
        
        def _make_api_call():
            return self._client.chat.completions.create(
                model=self.config.generator_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                timeout=self.config.api_timeout
            )
        
        try:
            print(f"🎨 Generating scene code with {self.config.generator_model}")
            logger.info(f"Generating scene code with model: {self.config.generator_model}")
            
            # Show progress during generation
            print("⏳ Contacting AI model...", end="", flush=True)
            
            response = self._retry_api_call(_make_api_call)
            
            print(" ✅")
            print("📝 Processing AI response...", end="", flush=True)
            
            scene_code = response.choices[0].message.content.strip()
            
            # Basic validation
            is_valid, errors = ValidationSystem.validate_scene_code(scene_code)
            if not is_valid:
                logger.warning(f"Generated code validation failed: {errors}")
                # Try to fix common issues
                scene_code = fix_common_issues(scene_code)
            
            logger.debug(f"Generated scene code (length: {len(scene_code)} chars)")
            print(f" ✅ ({len(scene_code)} chars)")
            
            metrics.metadata['model_used'] = self.config.generator_model
            metrics.metadata['prompt_length'] = len(prompt)
            metrics.metadata['response_length'] = len(scene_code)
            
            logger.info(f"Scene code generated successfully ({len(scene_code)} characters)")
            return scene_code
            
        except Exception as e:
            metrics.complete(str(e))
            logger.error(f"Failed to generate scene code: {e}")
            raise RayLMAPIError(f"Scene code generation failed: {e}")
    
    def verify_scene_code(self, scene_code: str, prompt: str, metrics: PerformanceMetrics) -> str:
        """Verify and correct POV-Ray scene code."""
        
        system_prompt = """You are an expert POV-Ray code reviewer and validator.

Your task is to:
1. Verify the syntax and completeness of POV-Ray code
2. Fix any syntax errors, missing includes, or structural issues
3. Ensure the code follows POV-Ray best practices
4. Return ONLY the corrected POV-Ray code
5. Do NOT add explanations, comments, or markdown

CRITICAL REQUIREMENTS:
- Must include: colors.inc, textures.inc, finish.inc
- Must have camera, light_source, and at least one object
- All braces must be balanced
- All statements must be properly terminated
- Use proper POV-Ray SDL syntax

Return ONLY the corrected code, nothing else."""
        
        user_prompt = f"""Please review and correct this POV-Ray code:

Original Prompt: {prompt}

POV-Ray Code:
{scene_code}

Return only the corrected POV-Ray code."""
        
        def _make_api_call():
            return self._client.chat.completions.create(
                model=self.config.verifier_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=3000,
                timeout=self.config.api_timeout
            )
        
        try:
            print(f"🔍 Verifying scene code with {self.config.verifier_model}")
            logger.info(f"Verifying scene code with model: {self.config.verifier_model}")
            
            print("⏳ Contacting verification model...", end="", flush=True)
            
            response = self._retry_api_call(_make_api_call)
            
            print(" ✅")
            print("🔧 Processing verification...", end="", flush=True)
            
            corrected_code = response.choices[0].message.content.strip()
            
            # Validate the corrected code
            is_valid, errors = ValidationSystem.validate_scene_code(corrected_code)
            if not is_valid:
                logger.error(f"Corrected code still has issues: {errors}")
                raise ValueError(f"Verification failed: {errors}")
            
            logger.debug(f"Corrected scene code (length: {len(corrected_code)} chars)")
            print(f" ✅ ({len(corrected_code)} chars)")
            
            metrics.metadata['verification_model'] = self.config.verifier_model
            logger.info(f"Scene code verified and corrected ({len(corrected_code)} characters)")
            return corrected_code
            
        except Exception as e:
            metrics.complete(str(e))
            logger.error(f"Failed to verify scene code: {e}")
            raise RayLMAPIError(f"Scene code verification failed: {e}")
    
    def _retry_api_call(self, api_call_func):
        """Retry API calls with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return api_call_func()
                
            except (RateLimitError, APIError) as e:
                last_exception = e
                if attempt == self.config.max_retries - 1:
                    break
                
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"API call attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                
            except (Timeout, Exception) as e:
                last_exception = e
                if attempt == self.config.max_retries - 1:
                    break
                
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"API call attempt {attempt + 1} timed out: {e}. Retrying in {delay}s...")
                time.sleep(delay)
        
        raise last_exception or RayLMAPIError("API call failed after all retries")

def fix_common_issues(scene_code: str) -> str:
    """Fix common issues in generated POV-Ray code."""
    # Add missing includes if they're completely missing
    includes = ['colors.inc', 'textures.inc', 'finish.inc']
    for include in includes:
        if f'#include "{include}"' not in scene_code:
            scene_code = f'#include "{include}"\n' + scene_code
    
    # Fix unbalanced braces by adding closing braces
    open_braces = scene_code.count('{')
    close_braces = scene_code.count('}')
    if open_braces > close_braces:
        scene_code += '}' * (open_braces - close_braces)
    
    return scene_code

# Enhanced POV-Ray renderer
class POVRayRenderer:
    """Enhanced POV-Ray renderer with comprehensive error handling."""
    
    def __init__(self, config: RayLMConfig):
        self.config = config
        self._validate_povray_installation()
    
    def _validate_povray_installation(self) -> None:
        """Validate that POV-Ray is properly installed."""
        try:
            result = subprocess.run(
                ['povray', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"POV-Ray found: {version_info}")
            else:
                raise RayLMConfigurationError("POV-Ray installation verification failed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RayLMConfigurationError("POV-Ray not found. Please install POV-Ray 3.7 or later.")
    
    def create_ini_file(self, scene_file: Path, output_file: Path, 
                       width: int, height: int, quality: int = 9,
                       antialiasing: str = "on", antialiasing_threshold: float = 0.3,
                       antialiasing_depth: int = 2, clock_value: Optional[float] = None) -> Path:
        """Create POV-Ray INI configuration file."""
        
        # Basic validation
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")
        
        if not scene_file.exists():
            raise FileNotFoundError(f"Scene file does not exist: {scene_file}")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        ini_content = f"""Input_File_Name="{scene_file.resolve()}"
Output_File_Name="{output_file.resolve()}"
Width={width}
Height={height}
Antialias={antialiasing}
Antialias_Threshold={antialiasing_threshold}
Antialias_Depth={antialiasing_depth}
Quality={quality}
Output_Alpha=Off
Display=Off
+W{width}+H{height}
+Q{quality}
+A{antialiasing_threshold}/{antialiasing_depth}
"""
        
        # Add clock parameter for animations if provided
        if clock_value is not None:
            ini_content += f"Clock={clock_value}\n"
        
        ini_file = scene_file.with_suffix(".ini")
        
        try:
            with open(ini_file, "w") as f:
                f.write(ini_content)
            logger.debug(f"INI file created: {ini_file}")
            return ini_file
        except Exception as e:
            logger.error(f"Failed to create INI file: {e}")
            raise RayLMRenderingError(f"INI file creation failed: {e}")
    
    def render_scene(self, scene_file: Path, output_file: Path, ini_file: Path, 
                    timeout: Optional[int] = None, metrics: Optional[PerformanceMetrics] = None) -> bool:
        """Render POV-Ray scene with comprehensive error handling."""
        
        if timeout is None:
            timeout = self.config.default_timeout
        
        cmd = [
            "povray", 
            str(ini_file),
            "+P",  # Progress reporting
            "+V"   # Verbose output
        ]
        
        start_time = time.time()
        
        try:
            logger.info(f"Rendering scene: {scene_file.name} -> {output_file.name}")
            
            print(f"🖼️  Starting POV-Ray render ({width}x{height}, Q{quality})...")
            print(f"   This may take a while. Progress will be shown below:")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=scene_file.parent
            )
            
            render_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Render completed successfully!")
                logger.info(f"Rendering completed successfully in {render_time:.2f}s: {output_file}")
                
                # Verify output file was created
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    print(f"📁 Output file: {output_file.name} ({file_size / 1024:.1f} KB)")
                    logger.info(f"Output file size: {file_size / 1024:.2f} KB")
                    
                    if metrics:
                        metrics.metadata['render_time'] = render_time
                        metrics.metadata['output_size'] = file_size
                        metrics.metadata['command'] = ' '.join(cmd)
                    
                    return True
                else:
                    print(f"⚠️  POV-Ray reported success but output file not found")
                    logger.warning(f"POV-Ray reported success but output file not found: {output_file}")
                    return False
                    
            else:
                print(f"❌ Render failed (error code {result.returncode})")
                logger.error(f"Rendering failed with error code {result.returncode}")
                logger.error(f"Command: {' '.join(cmd)}")
                logger.error(f"Error output: {result.stderr}")
                
                if result.stdout:
                    logger.debug(f"Standard output: {result.stdout}")
                
                if metrics:
                    metrics.complete(f"POV-Ray error code {result.returncode}: {result.stderr}")
                
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"Rendering timed out after {timeout} seconds"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            if metrics:
                metrics.complete(error_msg)
            
            raise RayLMTimeoutError(error_msg)
            
        except Exception as e:
            logger.error(f"Rendering failed with exception: {e}")
            
            if metrics:
                metrics.complete(str(e))
            
            raise RayLMRenderingError(f"Rendering failed: {e}")

# Enhanced main application class
class RayLM:
    """Enhanced RayLM application with comprehensive error handling and monitoring."""
    
    def __init__(self, config: Optional[RayLMConfig] = None):
        self.config = config or RayLMConfig()
        self._validate_configuration()
        
        # Initialize components
        self.file_manager = FileManager(self.config)
        self.llm_client = LLMClient(self.config)
        self.renderer = POVRayRenderer(self.config)
        
        logger.info("RayLM v3.6 initialized successfully")
    
    def _validate_configuration(self) -> None:
        """Validate the application configuration."""
        issues = self.config.validate()
        if issues:
            for issue in issues:
                if "ZAGUAN_API_KEY" in issue:
                    logger.error(issue)
            raise RayLMConfigurationError(f"Configuration issues: {issues}")
    
    def _parse_resolution_preset(self, resolution: str) -> Tuple[int, int]:
        """Parse resolution preset to width and height."""
        resolutions = {
            "480p": (854, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "1440p": (2560, 1440),
            "4k": (3840, 2160)
        }
        
        if resolution in resolutions:
            return resolutions[resolution]
        else:
            raise RayLMValidationError(f"Unknown resolution preset: {resolution}")
    
    def _validate_dimensions(self, width: int, height: int) -> None:
        """Validate resolution dimensions."""
        if width is None or height is None:
            raise RayLMValidationError("Resolution dimensions cannot be None")
        
        is_valid, errors = ValidationSystem.validate_resolution(width, height)
        if not is_valid:
            raise RayLMValidationError(f"Invalid resolution: {errors}")
    
    def _generate_animation_frames(self, scene_code: str, prompt: str, metrics: PerformanceMetrics,
                                  scene_file: Path, output_file: Path,
                                  width: int, height: int, quality: int,
                                  timeout: int, fps: int, total_frames: int) -> List[Path]:
        """Generate animation frames by varying the clock parameter."""
        logger.info(f"Generating animation with {total_frames} frames")
        
        if total_frames <= 0:
            raise ValueError("Number of frames must be positive")
        
        frame_files = []
        temp_files = []  # Track temporary files for cleanup
        
        try:
            for i in range(total_frames):
                clock_value = i / max(1, (total_frames - 1))
                print(f"   🎬 Frame {i+1:3d}/{total_frames} (clock={clock_value:.3f})...", end="", flush=True)
                
                # Create frame-specific filenames
                frame_suffix = f"_frame_{i:03d}"
                temp_scene_file = self.file_manager.create_scene_filename(
                    prompt, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                ).with_name(f"{scene_file.stem}{frame_suffix}.pov")
                temp_ini_file = temp_scene_file.with_suffix(".ini")
                frame_output_file = self.file_manager.create_output_filename(
                    prompt, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                ).with_name(f"{output_file.stem}{frame_suffix}.png")
                
                temp_files.extend([temp_scene_file, temp_ini_file])
                
                # Inject clock value into scene code
                animated_scene_code = self._inject_clock_value(scene_code, clock_value)
                
                # Validate the animated scene code
                is_valid, errors = ValidationSystem.validate_scene_code(animated_scene_code)
                if not is_valid:
                    print(f" ⚠️  (validation failed)")
                    logger.warning(f"Frame {i+1} code validation failed: {errors}")
                    continue
                
                try:
                    # Write scene file
                    with open(temp_scene_file, "w") as f:
                        f.write(animated_scene_code)
                    
                    # Create INI file with clock parameter
                    self._validate_dimensions(width, height)
                    ini_file = self.renderer.create_ini_file(
                        temp_scene_file, frame_output_file, 
                        width, height, quality,
                        clock_value=clock_value
                    )
                    
                    # Render the frame
                    render_start = time.time()
                    if self.renderer.render_scene(temp_scene_file, frame_output_file, ini_file, timeout):
                        frame_time = time.time() - render_start
                        print(f" ✅ ({frame_time:.1f}s)")
                        frame_files.append(frame_output_file)
                    else:
                        print(f" ❌")
                        logger.warning(f"Failed to render frame {i+1}")
                        
                except Exception as e:
                    print(f" ❌ ({e})")
                    logger.error(f"Error rendering frame {i+1}: {e}")
                    
            logger.info(f"Animation generation completed. Successfully rendered {len(frame_files)}/{total_frames} frames.")
            return frame_files
            
        except Exception as e:
            logger.error(f"Animation generation failed: {e}")
            raise
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                        logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_file}: {e}")
    
    def _inject_clock_value(self, scene_code: str, clock_value: float) -> str:
        """Inject clock value into POV-Ray scene code."""
        # Look for existing clock declaration and replace it
        clock_pattern = r'#declare\s+Clock\s*=\s*[^;]+;'
        if re.search(clock_pattern, scene_code, re.IGNORECASE):
            # Replace existing clock declaration
            scene_code = re.sub(clock_pattern, f'#declare Clock = {clock_value};', scene_code, flags=re.IGNORECASE)
        else:
            # Add clock declaration after includes
            include_end = scene_code.find('\n\n')
            if include_end == -1:
                include_end = scene_code.find('\n')
            if include_end != -1:
                scene_code = scene_code[:include_end] + f'\n#declare Clock = {clock_value};' + scene_code[include_end:]
            else:
                # Fallback: prepend clock declaration
                scene_code = f'#declare Clock = {clock_value};\n' + scene_code
        
        return scene_code
    
    def generate_scene(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a POV-Ray scene with comprehensive error handling."""
        
        print(f"\n🚀 Starting RayLM v3.6 scene generation...")
        print(f"📝 Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        metrics = PerformanceMetrics("scene_generation")
        
        try:
            # Validate prompt
            print("🔍 Validating prompt...", end="", flush=True)
            is_valid, errors = ValidationSystem.validate_prompt(prompt)
            if not is_valid:
                print(f" ❌")
                print(f"   Validation errors: {', '.join(errors)}")
                raise RayLMValidationError(f"Invalid prompt: {errors}")
            print(" ✅")
            
            logger.info(f"Starting scene generation for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            
            # Extract parameters with defaults
            print("⚙️  Configuring parameters...")
            width = kwargs.get('width', self.config.default_width)
            height = kwargs.get('height', self.config.default_height)
            
            # Handle resolution presets if width/height are None
            resolution = kwargs.get('resolution')
            if resolution and (width is None or height is None):
                width, height = self._parse_resolution_preset(resolution)
            
            # Ensure we have valid dimensions
            if width is None or height is None:
                width, height = self.config.default_width, self.config.default_height
            
            quality = kwargs.get('quality', self.config.default_quality)
            timeout = kwargs.get('timeout', self.config.default_timeout)
            no_render = kwargs.get('no_render', False)
            preview = kwargs.get('preview', False)
            animate = kwargs.get('animate', False)
            duration = kwargs.get('duration', self.config.default_duration)
            fps = kwargs.get('fps', self.config.default_fps)
            frames = kwargs.get('frames')
            
            # Configure preview mode
            if preview:
                width, height = 320, 240
                quality = 4
                print("   Preview mode: 320x240, Q4 quality")
            else:
                print(f"   Resolution: {width}x{height}, Quality: {quality}")
                print(f"   Timeout: {timeout}s, Timeout: {timeout}s")
            
            if animate:
                print(f"   Animation: {frames or duration*fps} frames at {fps} FPS")
            
            print("✅ Configuration complete")
            
            # Generate scene code
            print("\n🎨 AI Scene Generation Phase")
            print("=" * 50)
            scene_code = self.llm_client.generate_scene_code(prompt, metrics)
            
            # Validate generated code
            if self.config.validate_syntax:
                print("🔍 Validating generated scene code...", end="", flush=True)
                is_valid, errors = ValidationSystem.validate_scene_code(scene_code)
                if not is_valid:
                    print(f" ⚠️  (found {len(errors)} issues)")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    print(" ✅")
            
            # Create filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_file = self.file_manager.create_scene_filename(prompt, timestamp)
            output_file = self.file_manager.create_output_filename(prompt, timestamp)
            
            print(f"\n💾 File Management Phase")
            print("=" * 50)
            
            # Save scene code
            print(f"💾 Saving scene code to {scene_file.name}...", end="", flush=True)
            with open(scene_file, 'w') as f:
                f.write(scene_code)
            print(" ✅")
            
            # Create backup if enabled
            if self.config.backup_generations:
                print(f"🛡️  Creating backup...", end="", flush=True)
                backup_file = self.file_manager.backup_scene(scene_code, scene_file)
                if backup_file:
                    print(f" ✅ ({backup_file.name})")
                else:
                    print(" ⚠️  (backup failed)")
            
            metrics.metadata['scene_file'] = str(scene_file)
            metrics.metadata['output_file'] = str(output_file)
            metrics.metadata['backup_file'] = str(backup_file) if backup_file else None
            
            logger.info(f"Scene code saved to: {scene_file}")
            
            metrics.metadata['prompt'] = prompt
            metrics.metadata['parameters'] = {
                'width': width,
                'height': height,
                'quality': quality,
                'timeout': timeout,
                'preview': preview,
                'animate': animate
            }
            
            # Verify scene code
            if self.config.verifier_model:
                print(f"\n🔍 AI Verification Phase")
                print("=" * 50)
                try:
                    print(f"🔄 Running verification with {self.config.verifier_model}...")
                    verification_start = time.time()
                    
                    print("⏳ Contacting verification model...", end="", flush=True)
                    scene_code = self.llm_client.verify_scene_code(scene_code, prompt, metrics)
                    verification_time = time.time() - verification_start
                    
                    # Save verified code
                    print(f" ✅ ({verification_time:.1f}s)")
                    print(f"💾 Saving verified scene code...", end="", flush=True)
                    with open(scene_file, 'w') as f:
                        f.write(scene_code)
                    print(" ✅")
                    
                    metrics.metadata['verification_time'] = verification_time
                    logger.info(f"Scene code verified and updated ({verification_time:.2f}s)")
                    
                except Exception as e:
                    print(f" ⚠️  Verification failed: {e}")
                    logger.warning(f"Scene verification failed: {e}")
                    metrics.metadata['verification_error'] = str(e)
            
            if no_render:
                print(f"\n✅ Code generation completed (no rendering)")
                metrics.complete()
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'scene_code': scene_code,
                    'metrics': metrics
                }
            
            # Animation branch
            if animate:
                print(f"\n🎬 Animation Generation Phase")
                print("=" * 50)
                
                frames = frames or (duration * fps)
                frame_files = self._generate_animation_frames(
                    scene_code, prompt, metrics, scene_file, output_file, 
                    width, height, quality, timeout, fps, frames
                )
                
                if not frame_files:
                    print(f"❌ No frames were generated")
                    metrics.complete("No frames generated")
                    return {
                        'success': False,
                        'error': "No frames generated",
                        'metrics': metrics
                    }
                
                # Render animation
                animation_output = self.file_manager.create_output_filename(
                    prompt, timestamp, extension="mp4"
                )
                
                print(f"🎬 Creating animation from {len(frame_files)} frames...")
                animation_success = self.render_animation(
                    frame_files, animation_output, fps, metrics
                )
                
                if animation_success:
                    print(f"\n🎉 Animation generation completed successfully!")
                    metrics.complete()
                    
                    # Save metadata
                    self.file_manager.save_metadata(metrics, animation_output)
                    
                    return {
                        'success': True,
                        'scene_file': scene_file,
                        'output_file': animation_output,
                        'scene_code': scene_code,
                        'metrics': metrics
                    }
                else:
                    print(f"\n❌ Animation rendering failed")
                    metrics.complete("Animation rendering failed")
                    return {
                        'success': False,
                        'scene_file': scene_file,
                        'error': "Animation rendering failed",
                        'metrics': metrics
                    }
            
            # Render scene branch
            print(f"\n🖼️  POV-Ray Rendering Phase")
            print("=" * 50)
            render_metrics = PerformanceMetrics("scene_rendering")
            
            self._validate_dimensions(width, height)
            
            ini_file = self.renderer.create_ini_file(
                scene_file, output_file, width, height, quality
            )
            
            success = self.renderer.render_scene(scene_file, output_file, ini_file, timeout, render_metrics)
            
            if success:
                print(f"\n🎉 Generation completed successfully!")
                metrics.complete()
                
                # Save metadata
                self.file_manager.save_metadata(metrics, output_file)
                
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'output_file': output_file,
                    'scene_code': scene_code,
                    'metrics': metrics
                }
            else:
                print(f"\n❌ Render failed")
                metrics.complete("Rendering failed")
                return {
                    'success': False,
                    'scene_file': scene_file,
                    'error': "Rendering failed",
                    'metrics': metrics
                }
            
        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            metrics.complete(str(e))
            raise
    
    def render_animation(self, frame_files: List[Path], output_path: Path, fps: int,
                        metrics: Optional[PerformanceMetrics] = None) -> bool:
        """Render animation from frames using FFmpeg."""
        
        if not frame_files:
            logger.error("No frame files to render")
            return False
        
        # Check FFmpeg availability
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10, check=True)
            print("✅ FFmpeg available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ FFmpeg not found. Cannot create animation.")
            logger.error("FFmpeg not found. Cannot create animation.")
            return False
        
        # Validate frame files exist
        missing_files = [f for f in frame_files if not f.exists()]
        if missing_files:
            print(f"❌ Missing frame files: {missing_files}")
            logger.error(f"Missing frame files: {missing_files}")
            return False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create frame list file for FFmpeg
        temp_list_file = output_path.with_suffix(".txt")
        
        print(f"📝 Creating frame list...", end="", flush=True)
        with open(temp_list_file, "w") as f:
            for frame_file in sorted(frame_files):
                f.write(f"file '{frame_file.name}'\n")
                f.write(f"duration {1/fps}\n")
            # Add the last frame again to close the sequence
            f.write(f"file '{frame_files[-1].name}'\n")
        print(" ✅")
        
        # Enhanced FFmpeg command with better quality settings
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-f", "concat",
            "-safe", "0",
            "-i", str(temp_list_file),
            "-c:v", "libx264",
            "-preset", "medium",  # Balance between speed and quality
            "-crf", "23",  # Quality level (lower = better quality)
            "-pix_fmt", "yuv420p",  # Compatibility
            "-vf", f"fps={fps}",
            "-movflags", "+faststart",  # For better web compatibility
            str(output_path)
        ]
        
        start_time = time.time()
        
        try:
            print(f"🎥 Starting FFmpeg encoding...")
            print(f"   This may take several minutes...")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=600,  # 10 minutes timeout
                cwd=output_path.parent
            )
            
            render_time = time.time() - start_time
            
            # Clean up frame list file
            temp_list_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"✅ Animation rendered successfully!")
                logger.info(f"Animation rendered successfully in {render_time:.2f}s: {output_path}")
                
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"📁 Animation: {output_path.name} ({file_size / (1024*1024):.1f} MB)")
                    logger.info(f"Animation file size: {file_size / (1024*1024):.2f} MB")
                    
                    if metrics:
                        metrics.metadata['render_time'] = render_time
                        metrics.metadata['output_size'] = file_size
                        metrics.metadata['frame_count'] = len(frame_files)
                        metrics.metadata['fps'] = fps
                
                return True
                
            else:
                print(f"❌ Animation rendering failed (error code {result.returncode})")
                logger.error(f"Animation rendering failed with error code {result.returncode}")
                logger.error(f"Command: {' '.join(cmd)}")
                logger.error(f"Error output: {result.stderr}")
                
                if metrics:
                    metrics.complete(f"FFmpeg error code {result.returncode}: {result.stderr}")
                
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Animation rendering timed out after 600 seconds"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            temp_list_file.unlink(missing_ok=True)
            
            if metrics:
                metrics.complete(error_msg)
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to create frame list or run FFmpeg: {e}")
            logger.error(f"Failed to create frame list or run FFmpeg: {e}")
            temp_list_file.unlink(missing_ok=True)
            return False
    
    def render_existing_file(self, scene_file: Path, **kwargs) -> Dict[str, Any]:
        """Render an existing POV-Ray scene file."""
        
        metrics = PerformanceMetrics("file_rendering")
        
        try:
            if not scene_file.exists():
                raise RayLMValidationError(f"Scene file does not exist: {scene_file}")
            
            width = kwargs.get('width', self.config.default_width)
            height = kwargs.get('height', self.config.default_height)
            quality = kwargs.get('quality', self.config.default_quality)
            timeout = kwargs.get('timeout', self.config.default_timeout)
            
            logger.info(f"Rendering existing file: {scene_file}")
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.file_manager.create_output_filename(
                scene_file.stem, timestamp
            )
            
            # Render the scene
            render_start = time.time()
            ini_file = self.renderer.create_ini_file(
                scene_file, output_file, width, height, quality
            )
            
            success = self.renderer.render_scene(scene_file, output_file, ini_file, timeout, metrics)
            
            if success:
                metrics.complete()
                
                # Save metadata
                self.file_manager.save_metadata(metrics, output_file)
                
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'output_file': output_file,
                    'metrics': metrics
                }
            else:
                metrics.complete("Rendering failed")
                return {
                    'success': False,
                    'scene_file': scene_file,
                    'error': "Rendering failed",
                    'metrics': metrics
                }
            
        except Exception as e:
            logger.error(f"File rendering failed: {e}")
            metrics.complete(str(e))
            raise

# Main function and command-line interface
def main():
    """Enhanced main function with comprehensive argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="""RayLM v3.6: Enhanced AI-Powered POV-Ray Scene Generator
        
Generate 3D scenes for POV-Ray using Large Language Models with advanced
error handling, performance monitoring, and improved reliability.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Generate a scene from prompt
  python raylm3.6.py "A futuristic city at sunset with flying cars"
  
  # Generate with custom resolution
  python raylm3.6.py "A medieval castle" --width 2560 --height 1440 --quality 10
  
  # Generate animation
  python raylm3.6.py "A rotating crystal sculpture" --animate --duration 10 --fps 30
  
  # Render existing POV-Ray code using the OpenAI client with retry logic and improved error handling
                
        raise RayLMConfigurationError(f"Failed to initialize OpenAI client: {e}")
    
    def generate_scene_code(self, prompt: str, metrics: PerformanceMetrics) -> str:
        """Generate POV-Ray scene code with retry logic."""
        
        # Enhanced system prompt for better code generation
        system_prompt = """You are a professional POV-Ray scene generator with expertise in 3D graphics and rendering.

IMPORTANT REQUIREMENTS:
1. Generate ONLY valid POV-Ray SDL code - no explanations, markdown, or additional text
2. Include these essential includes: colors.inc, textures.inc, finish.inc, metals.inc, stones.inc, woods.inc
3. Always include: camera, lights, and at least one 3D object
4. Use proper POV-Ray syntax and conventions
5. Add helpful comments for complex parts
6. Ensure complete and syntactically correct code
7. Use appropriate materials, textures, and lighting

Example structure:
```
#include "colors.inc"
#include "textures.inc"
#include "finish.inc"
#include "metals.inc"
#include "stones.inc"
#include "woods.inc"

camera {
    location <0, 2, -5>
    look_at <0, 1, 0>
}

light_source {
    <10, 10, -10>
    color White
}

object {
    sphere {
        <0, 1, 0>, 1
        texture {
            pigment { color Red }
            finish { specular 0.4 }
        }
    }
}
```
"""
        
        user_prompt = f"""Generate a POV-Ray scene for: {prompt}

Ensure the scene is complete, visually interesting, and uses proper POV-Ray SDL syntax. Include all necessary components (camera, lights, objects, materials)."""
        
        def _make_api_call():
            return self._client.chat.completions.create(
                model=self.config.generator_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                timeout=self.config.api_timeout
            )
        
        try:
            print(f"🎨 Generating scene code with model: {self.config.generator_model}")
            logger.info(f"Generating scene code with model: {self.config.generator_model}")
            
            # Show progress during generation
            print("⏳ Contacting AI model...", end="", flush=True)
            
            response = self._retry_api_call(_make_api_call)
            
            print(" ✅")
            print("📝 Processing AI response...", end="", flush=True)
            
            scene_code = response.choices[0].message.content.strip()
            
            # Basic validation
            is_valid, errors = ValidationSystem.validate_scene_code(scene_code)
            if not is_valid:
                logger.warning(f"Generated code validation failed: {errors}")
                # Try to fix common issues
                scene_code = fix_common_issues(scene_code)
            
            logger.debug(f"Generated scene code (length: {len(scene_code)} chars)")
            print(f" ✅ ({len(scene_code)} chars)")
            
            metrics.metadata['model_used'] = self.config.generator_model
            metrics.metadata['prompt_length'] = len(prompt)
            metrics.metadata['response_length'] = len(scene_code)
            
            logger.info(f"Scene code generated successfully ({len(scene_code)} characters)")
            return scene_code
            
        except Exception as e:
            metrics.complete(str(e))
            logger.error(f"Failed to generate scene code: {e}")
            raise RayLMAPIError(f"Scene code generation failed: {e}")
    
    def verify_scene_code(self, scene_code: str, prompt: str, metrics: PerformanceMetrics) -> str:
        """Verify and correct POV-Ray scene code."""
        
        system_prompt = """You are an expert POV-Ray code reviewer and validator.

Your task is to:
1. Verify the syntax and completeness of POV-Ray code
2. Fix any syntax errors, missing includes, or structural issues
3. Ensure the code follows POV-Ray best practices
4. Return ONLY the corrected POV-Ray code
5. Do NOT add explanations, comments, or markdown

CRITICAL REQUIREMENTS:
- Must include: colors.inc, textures.inc, finish.inc
- Must have camera, light_source, and at least one object
- All braces must be balanced
- All statements must be properly terminated
- Use proper POV-Ray SDL syntax

Return ONLY the corrected code, nothing else."""
        
        user_prompt = f"""Please review and correct this POV-Ray code:

Original Prompt: {prompt}

POV-Ray Code:
{scene_code}

Return only the corrected POV-Ray code."""
        
        def _make_api_call():
            return self._client.chat.completions.create(
                model=self.config.verifier_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=3000,
                timeout=self.config.api_timeout
            )
        
        try:
            print(f"🔍 Verifying scene code with model: {self.config.verifier_model}")
            logger.info(f"Verifying scene code with model: {self.config.verifier_model}")
            
            print("⏳ Contacting verification model...", end="", flush=True)
            
            response = self._retry_api_call(_make_api_call)
            
            print(" ✅")
            print("🔧 Processing verification...", end="", flush=True)
            
            corrected_code = response.choices[0].message.content.strip()
            
            # Validate the corrected code
            is_valid, errors = ValidationSystem.validate_scene_code(corrected_code)
            if not is_valid:
                logger.error(f"Corrected code still has issues: {errors}")
                raise ValueError(f"Verification failed: {errors}")
            
            logger.debug(f"Corrected scene code (length: {len(corrected_code)} chars)")
            print(f" ✅ ({len(corrected_code)} chars)")
            
            metrics.metadata['verification_model'] = self.config.verifier_model
            logger.info(f"Scene code verified and corrected ({len(corrected_code)} characters)")
            return corrected_code
            
        except Exception as e:
            metrics.complete(str(e))
            logger.error(f"Failed to verify scene code: {e}")
            raise RayLMAPIError(f"Scene code verification failed: {e}")
    
    def _retry_api_call(self, api_call_func):
        """Retry API calls with exponential backoff."""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return api_call_func()
                
            except (RateLimitError, APIError) as e:
                last_exception = e
                if attempt == self.config.max_retries - 1:
                    break
                
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"API call attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                
            except (Timeout, Exception) as e:
                last_exception = e
                if attempt == self.config.max_retries - 1:
                    break
                
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"API call attempt {attempt + 1} timed out: {e}. Retrying in {delay}s...")
                time.sleep(delay)
        
        raise last_exception or RayLMAPIError("API call failed after all retries")

def fix_common_issues(scene_code: str) -> str:
    """Fix common issues in generated POV-Ray code."""
    # Add missing includes if they're completely missing
    includes = ['colors.inc', 'textures.inc', 'finish.inc']
    for include in includes:
        if f'#include "{include}"' not in scene_code:
            scene_code = f'#include "{include}"\n' + scene_code
    
    # Fix unbalanced braces by adding closing braces
    open_braces = scene_code.count('{')
    close_braces = scene_code.count('}')
    if open_braces > close_braces:
        scene_code += '}' * (open_braces - close_braces)
    
    return scene_code

# Enhanced POV-Ray renderer
class POVRayRenderer:
    """Enhanced POV-Ray renderer with comprehensive error handling."""
    
    def __init__(self, config: RayLMConfig):
        self.config = config
        self._validate_povray_installation()
    
    def _validate_povray_installation(self) -> None:
        """Validate that POV-Ray is properly installed."""
        try:
            result = subprocess.run(
                ['povray', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"POV-Ray found: {version_info}")
            else:
                raise RayLMConfigurationError("POV-Ray installation verification failed")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RayLMConfigurationError("POV-Ray not found. Please install POV-Ray 3.7 or later.")
    
    def create_ini_file(self, scene_file: Path, output_file: Path, 
                       width: int, height: int, quality: int = 9,
                       antialiasing: str = "on", antialiasing_threshold: float = 0.3,
                       antialiasing_depth: int = 2, clock_value: Optional[float] = None) -> Path:
        """Create POV-Ray INI configuration file."""
        
        # Basic validation
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")
        
        if not scene_file.exists():
            raise FileNotFoundError(f"Scene file does not exist: {scene_file}")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        ini_content = f"""Input_File_Name="{scene_file.resolve()}"
Output_File_Name="{output_file.resolve()}"
Width={width}
Height={height}
Antialias={antialiasing}
Antialias_Threshold={antialiasing_threshold}
Antialias_Depth={antialiasing_depth}
Quality={quality}
Output_Alpha=Off
Display=Off
+W{width}+H{height}
+Q{quality}
+A{antialiasing_threshold}/{antialiasing_depth}
"""
        
        # Add clock parameter for animations if provided
        if clock_value is not None:
            ini_content += f"Clock={clock_value}\n"
        
        ini_file = scene_file.with_suffix(".ini")
        
        try:
            with open(ini_file, "w") as f:
                f.write(ini_content)
            logger.debug(f"INI file created: {ini_file}")
            return ini_file
        except Exception as e:
            logger.error(f"Failed to create INI file: {e}")
            raise RayLMRenderingError(f"INI file creation failed: {e}")
    
    def render_scene(self, scene_file: Path, output_file: Path, ini_file: Path, 
                    timeout: Optional[int] = None, metrics: Optional[PerformanceMetrics] = None) -> bool:
        """Render POV-Ray scene with comprehensive error handling."""
        
        if timeout is None:
            timeout = self.config.default_timeout
        
        cmd = [
            "povray", 
            str(ini_file),
            "+P",  # Progress reporting
            "+V"   # Verbose output
        ]
        
        start_time = time.time()
        
        try:
            logger.info(f"Rendering scene: {scene_file.name} -> {output_file.name}")
            
            print(f"🖼️  Starting POV-Ray render ({width}x{height}, Q{quality})...")
            print(f"   This may take a while. Progress will be shown below:")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=scene_file.parent
            )
            
            render_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Render completed successfully!")
                logger.info(f"Rendering completed successfully in {render_time:.2f}s: {output_file}")
                
                # Verify output file was created
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    print(f"📁 Output file: {output_file.name} ({file_size / 1024:.1f} KB)")
                    logger.info(f"Output file size: {file_size / 1024:.2f} KB")
                    
                    if metrics:
                        metrics.metadata['render_time'] = render_time
                        metrics.metadata['output_size'] = file_size
                        metrics.metadata['command'] = ' '.join(cmd)
                    
                    return True
                else:
                    print(f"⚠️  POV-Ray reported success but output file not found")
                    logger.warning(f"POV-Ray reported success but output file not found: {output_file}")
                    return False
                    
            else:
                print(f"❌ Render failed (error code {result.returncode})")
                logger.error(f"Rendering failed with error code {result.returncode}")
                logger.error(f"Command: {' '.join(cmd)}")
                logger.error(f"Error output: {result.stderr}")
                
                if result.stdout:
                    logger.debug(f"Standard output: {result.stdout}")
                
                if metrics:
                    metrics.complete(f"POV-Ray error code {result.returncode}: {result.stderr}")
                
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"Rendering timed out after {timeout} seconds"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            if metrics:
                metrics.complete(error_msg)
            
            raise RayLMTimeoutError(error_msg)
            
        except Exception as e:
            logger.error(f"Rendering failed with exception: {e}")
            
            if metrics:
                metrics.complete(str(e))
            
            raise RayLMRenderingError(f"Rendering failed: {e}")

# Enhanced main application class
class RayLM:
    """Enhanced RayLM application with comprehensive error handling and monitoring."""
    
    def __init__(self, config: Optional[RayLMConfig] = None):
        self.config = config or RayLMConfig()
        self._validate_configuration()
        
        # Initialize components
        self.file_manager = FileManager(self.config)
        self.llm_client = LLMClient(self.config)
        self.renderer = POVRayRenderer(self.config)
        
        logger.info("RayLM v3.6 initialized successfully")
    
    def _validate_configuration(self) -> None:
        """Validate the application configuration."""
        issues = self.config.validate()
        if issues:
            for issue in issues:
                if "ZAGUAN_API_KEY" in issue:
                    logger.error(issue)
            raise RayLMConfigurationError(f"Configuration issues: {issues}")
    
    def _parse_resolution_preset(self, resolution: str) -> Tuple[int, int]:
        """Parse resolution preset to width and height."""
        resolutions = {
            "480p": (854, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "1440p": (2560, 1440),
            "4k": (3840, 2160)
        }
        
        if resolution in resolutions:
            return resolutions[resolution]
        else:
            raise RayLMValidationError(f"Unknown resolution preset: {resolution}")
    
    def _validate_dimensions(self, width: int, height: int) -> None:
        """Validate resolution dimensions."""
        if width is None or height is None:
            raise RayLMValidationError("Resolution dimensions cannot be None")
        
        is_valid, errors = ValidationSystem.validate_resolution(width, height)
        if not is_valid:
            raise RayLMValidationError(f"Invalid resolution: {errors}")
    
    def _generate_animation_frames(self, scene_code: str, prompt: str, metrics: PerformanceMetrics,
                                  scene_file: Path, output_file: Path,
                                  width: int, height: int, quality: int,
                                  timeout: int, fps: int, total_frames: int) -> List[Path]:
        """Generate animation frames by varying the clock parameter."""
        logger.info(f"Generating animation with {total_frames} frames")
        
        if total_frames <= 0:
            raise ValueError("Number of frames must be positive")
        
        frame_files = []
        temp_files = []  # Track temporary files for cleanup
        
        try:
            for i in range(total_frames):
                clock_value = i / max(1, (total_frames - 1))
                print(f"   🎬 Frame {i+1:3d}/{total_frames} (clock={clock_value:.3f})...", end="", flush=True)
                
                # Create frame-specific filenames
                frame_suffix = f"_frame_{i:03d}"
                temp_scene_file = self.file_manager.create_scene_filename(
                    prompt, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                ).with_name(f"{scene_file.stem}{frame_suffix}.pov")
                temp_ini_file = temp_scene_file.with_suffix(".ini")
                frame_output_file = self.file_manager.create_output_filename(
                    prompt, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
                ).with_name(f"{output_file.stem}{frame_suffix}.png")
                
                temp_files.extend([temp_scene_file, temp_ini_file])
                
                # Inject clock value into scene code
                animated_scene_code = self._inject_clock_value(scene_code, clock_value)
                
                # Validate the animated scene code
                is_valid, errors = ValidationSystem.validate_scene_code(animated_scene_code)
                if not is_valid:
                    print(f" ⚠️  (validation failed)")
                    logger.warning(f"Frame {i+1} code validation failed: {errors}")
                    continue
                
                try:
                    # Write scene file
                    with open(temp_scene_file, "w") as f:
                        f.write(animated_scene_code)
                    
                    # Create INI file with clock parameter
                    self._validate_dimensions(width, height)
                    ini_file = self.renderer.create_ini_file(
                        temp_scene_file, frame_output_file, 
                        width, height, quality,
                        clock_value=clock_value
                    )
                    
                    # Render the frame
                    render_start = time.time()
                    if self.renderer.render_scene(temp_scene_file, frame_output_file, ini_file, timeout):
                        frame_time = time.time() - render_start
                        print(f" ✅ ({frame_time:.1f}s)")
                        frame_files.append(frame_output_file)
                    else:
                        print(f" ❌")
                        logger.warning(f"Failed to render frame {i+1}")
                        
                except Exception as e:
                    print(f" ❌ ({e})")
                    logger.error(f"Error rendering frame {i+1}: {e}")
                    
            logger.info(f"Animation generation completed. Successfully rendered {len(frame_files)}/{total_frames} frames.")
            return frame_files
            
        except Exception as e:
            logger.error(f"Animation generation failed: {e}")
            raise
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                        logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {temp_file}: {e}")
    
    def _inject_clock_value(self, scene_code: str, clock_value: float) -> str:
        """Inject clock value into POV-Ray scene code."""
        # Look for existing clock declaration and replace it
        clock_pattern = r'#declare\s+Clock\s*=\s*[^;]+;'
        if re.search(clock_pattern, scene_code, re.IGNORECASE):
            # Replace existing clock declaration
            scene_code = re.sub(clock_pattern, f'#declare Clock = {clock_value};', scene_code, flags=re.IGNORECASE)
        else:
            # Add clock declaration after includes
            include_end = scene_code.find('\n\n')
            if include_end == -1:
                include_end = scene_code.find('\n')
            if include_end != -1:
                scene_code = scene_code[:include_end] + f'\n#declare Clock = {clock_value};' + scene_code[include_end:]
            else:
                # Fallback: prepend clock declaration
                scene_code = f'#declare Clock = {clock_value};\n' + scene_code
        
        return scene_code
    
    def generate_scene(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a POV-Ray scene with comprehensive error handling."""
        metrics = PerformanceMetrics("scene_generation")
        
        try:
            # Validate prompt
            is_valid, errors = ValidationSystem.validate_prompt(prompt)
            if not is_valid:
                raise RayLMValidationError(f"Invalid prompt: {}")
            
            logger.info(f"Starting scene generation for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            
            # Extract parameters with defaults
            width = kwargs.get('width', self.config.default_width)
            height = kwargs.get('height', self.config.default_height)
            
            # Handle resolution presets if width/height are None
            resolution = kwargs.get('resolution')
            if resolution and (width is None or height is None):
                width, height = self._parse_resolution_preset(resolution)
            
            # Ensure we have valid dimensions
            if width is None or height is None:
                width, height = self.config.default_width, self.config.default_height
            
            quality = kwargs.get('quality', self.config.default_quality)
            timeout = kwargs.get('timeout', self.config.default_timeout)
            no_render = kwargs.get('no_render', False)
            preview = kwargs.get('preview', False)
            animate = kwargs.get('animate', False)
            duration = kwargs.get('duration', self.config.default_duration)
            fps = kwargs.get('fps', self.config.default_fps)
            frames = kwargs.get('frames')
            
            # Configure preview mode
            if preview:
                width, height = 320, 240
                quality = 4
            
            # Generate scene code
            scene_code = self.llm_client.generate_scene_code(prompt, metrics)
            
            # Validate generated code
            if self.config.validate_syntax:
                is_valid, errors = ValidationSystem.validate_scene_code(scene_code)
                if not is_valid:
                    logger.warning(f"Generated code validation issues: {errors}")
            
            # Create filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_file = self.file_manager.create_scene_filename(prompt, timestamp)
            output_file = self.file_manager.create_output_filename(prompt, timestamp)
            
            # Save scene code
            with open(scene_file, 'w') as f:
                f.write(scene_code)
            
            # Verify scene code
            if self.config.verifier_model:
                try:
                    verification_start = time.time()
                    scene_code = self.llm_client.verify_scene_code(scene_code, prompt, metrics)
                    verification_time = time.time() - verification_start
                    
                    # Save verified code
                    with open(scene_file, 'w') as f:
                        f.write(scene_code)
                    
                    metrics.metadata['verification_time'] = verification_time
                    logger.info(f"Scene code verified and updated ({verification_time:.2f}s)")
                    
                except Exception as e:
                    logger.warning(f"Scene verification failed: {e}")
                    metrics.metadata['verification_error'] = str(e)
            
            if no_render:
                metrics.complete()
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'scene_code': scene_code,
                    'metrics': metrics
                }
            
            # Animation branch
            if animate:
                frames = frames or (duration * fps)
                frame_files = self._generate_animation_frames(
                    scene_code, prompt, metrics, scene_file, output_file, 
                    width, height, quality, timeout, fps, frames
                )
                
                if not frame_files:
                    return {
                        'success': False,
                        'error': "No frames generated",
                        'metrics': metrics
                    }
                
                # Render animation
                animation_output = self.file_manager.create_output_filename(
                    prompt, timestamp, extension="mp4"
                )
                
                animation_success = self.render_animation(
                    frame_files, animation_output, fps, metrics
                )
                
                if animation_success:
                    self.file_manager.save_metadata(metrics, animation_output)
                    
                    return {
                        'success': True,
                        'scene_file': scene_file,
                        'output_file': animation_output,
                        'scene_code': scene_code,
                        'metrics': metrics
                    }
                else:
                    return {
                        'success': False,
                        'scene_file': scene_file,
                        'error': "Animation rendering failed",
                        'metrics': metrics
                    }
            
            # Render scene branch
            render_metrics = PerformanceMetrics("scene_rendering")
            
            ini_file = self.renderer.create_ini_file(
                scene_file, output_file, width, height, quality
            )
            
            success = self.renderer.render_scene(scene_file, output_file, ini_file, timeout, render_metrics)
            
            if success:
                metrics.complete()
                
                # Save metadata
                self.file_manager.save_metadata(metrics, output_file)
                
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'output_file': output_file,
                    'scene_code': scene_code,
                    'metrics': metrics
                }
            else:
                metrics.complete("Rendering failed")
                return {
                    'success': False,
                    'scene_file': scene_file,
                    'error': "Rendering failed",
                    'metrics': metrics
                }
            
        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            metrics.complete(str(e))
            raise
    
    def render_animation(self, frame_files: List[Path], output_path: Path, fps: int,
                        metrics: Optional[PerformanceMetrics] = None) -> bool:
        """Render animation from frames using FFmpeg."""
        
        if not frame_files:
            logger.error("No frame files to render")
            return False
        
        # Check FFmpeg availability
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=10, check=True)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("FFmpeg not found. Cannot create animation.")
            return False
        
        # Validate frame files exist
        missing_files = [f for f in frame_files if not f.exists()]
        if missing_files:
            logger.error(f"Missing frame files: {missing_files}")
            return False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create frame list file for FFmpeg
        temp_list_file = output_path.with_suffix(".txt")
        
        try:
            with open(temp_list_file, "w") as f:
                for frame_file in sorted(frame_files):
                    f.write(f"file '{frame_file.name}'\n")
                    f.write(f"duration {1/fps}\n")
                # Add the last frame again to close the sequence
                f.write(f"file '{frame_files[-1].name}'\n")
            
            # Enhanced FFmpeg command with better quality settings
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-f", "concat",
                "-safe", "0",
                "-i", str(temp_list_file),
                "-c:v", "libx264",
                "-preset", "medium",  # Balance between speed and quality
                "-crf", "23",  # Quality level (lower = better quality)
                "-pix_fmt", "yuv420p",  # Compatibility
                "-vf", f"fps={fps}",
                "-movflags", "+faststart",  # For better web compatibility
                str(output_path)
            ]
            
            start_time = time.time()
            
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600,  # 10 minutes timeout
                    cwd=output_path.parent
                )
                
                render_time = time.time() - start_time
                
                # Clean up frame list file
                temp_list_file.unlink(missing_ok=True)
                
                if result.returncode == 0:
                    logger.info(f"Animation rendered successfully in {render_time:.2f}s: {output_path}")
                    
                    if output_path.exists():
                        file_size = output_path.stat().st_size
                        logger.info(f"Animation file size: {file_size / (1024*1024):.2f} MB")
                        
                        if metrics:
                            metrics.metadata['render_time'] = render_time
                            metrics.metadata['output_size'] = file_size
                            metrics.metadata['frame_count'] = len(frame_files)
                            metrics.metadata['fps'] = fps
                    
                    return True
                    
                else:
                    logger.error(f"Animation rendering failed with error code {result.returncode}")
                    logger.error(f"Command: {' '.join(cmd)}")
                    logger.error(f"Error output: {result.stderr}")
                    
                    if metrics:
                        metrics.complete(f"FFmpeg error code {result.returncode}: {result.stderr}")
                    
                    return False
                    
            except subprocess.TimeoutExpired:
                error_msg = "Animation rendering timed out after 600 seconds"
                logger.error(error_msg)
                temp_list_file.unlink(missing_ok=True)
                
                if metrics:
                    metrics.complete(error_msg)
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to create frame list or run FFmpeg: {e}")
            temp_list_file.unlink(missing_ok=True)
            return False
    
    def render_existing_file(self, scene_file: Path, **kwargs) -> Dict[str, Any]:
        """Render an existing POV-Ray scene file."""
        
        metrics = PerformanceMetrics("file_rendering")
        
        try:
            if not scene_file.exists():
                raise RayLMValidationError(f"Scene file does not exist: {scene_file}")
            
            width = kwargs.get('width', self.config.default_width)
            height = kwargs.get('height', self.config.default_height)
            quality = kwargs.get('quality', self.config.default_quality)
            timeout = kwargs.get('timeout', self.config.default_timeout)
            
            logger.info(f"Rendering existing file: {scene_file}")
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.file_manager.create_output_filename(
                scene_file.stem, timestamp
            )
            
            # Render the scene
            ini_file = self.renderer.create_ini_file(
                scene_file, output_file, width, height, quality
            )
            
            success = self.renderer.render_scene(scene_file, output_file, ini_file, timeout, metrics)
            
            if success:
                metrics.complete()
                
                # Save metadata
                self.file_manager.save_metadata(metrics, output_file)
                
                return {
                    'success': True,
                    'scene_file': scene_file,
                    'output_file': output_file,
                    'metrics': metrics
                }
            else:
                metrics.complete("Rendering failed")
                return {
                    'success': False,
                    'scene_file': scene_file,
                    'error': "Rendering failed",
                    'metrics': metrics
                }
            
        except Exception as e:
            logger.error(f"File rendering failed: {e}")
            metrics.complete(str(e))
            raise

# Main function and command-line interface
def main():
    """Enhanced main function with comprehensive argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="""RayLM v3.6: Enhanced AI-Powered POV-Ray Scene Generator
        
Generate 3D scenes for POV-Ray using Large Language Models with advanced
error handling, performance monitoring, and improved reliability.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Generate a scene from prompt
  python raylm3.6.py "A futuristic city at sunset with flying cars"
  
  # Generate with custom resolution
  python raylm3.6.py "A medieval castle" --width 2560 --height 1440 --quality 10
  
  # Generate animation
  python raylm3.6.py "A rotating crystal sculpture" --animate --duration 10 --fps 30
  
  # Render existing POV-Ray file
  python raylm3.6.py --render scene.pov --quality 9
  
  # Dry run (generate code without rendering)
  python raylm3.6.py "Test scene" --no-render
  
  # Verbose output for debugging
  python raylm3.6.py "Complex scene" --verbose
  
For more information, visit: https://github.com/your-repo/raylm
        """
    )
    
    # Basic arguments
    parser.add_argument("prompt", nargs="?", help="The prompt for scene generation")
    parser.add_argument("--prompt-file", type=Path, help="File containing the prompt")
    
    # Configuration options
    parser.add_argument("--output-dir", type=Path, default=Path("./output"), 
                       help="Output directory (default: ./output)")
    parser.add_argument("--config", type=Path, help="Configuration file (future feature)")
    
    # Resolution and quality
    resolution_group = parser.add_mutually_exclusive_group()
    resolution_group.add_argument("--resolution", 
                                 choices=["480p", "720p", "1080p", "1440p", "4k"], 
                                 default="1080p", 
                                 help="Output resolution (default: 1080p)")
    parser.add_argument("--width", type=int, help="Custom width in pixels")
    parser.add_argument("--height", type=int, help="Custom height in pixels")
    parser.add_argument("--quality", type=int, default=9, choices=range(1, 11), 
                       help="POV-Ray quality setting 1-10 (default: 9)")
    
    # Rendering options
    parser.add_argument("--no-render", action="store_true", 
                       help="Generate code without rendering")
    parser.add_argument("--render", type=Path, 
                       help="Render an existing POV-Ray file")
    parser.add_argument("--timeout", type=int, 
                       help="Timeout for rendering in seconds (default: 300)")
    parser.add_argument("--preview", action="store_true", 
                       help="Quick preview mode (320x240, Q4 quality)")
    
    # Antialiasing
    parser.add_argument("--antialiasing", choices=["on", "off"], default="on", 
                       help="Enable or disable antialiasing (default: on)")
    parser.add_argument("--antialiasing-threshold", type=float, default=0.3, 
                       help="Antialiasing threshold (default: 0.3)")
    parser.add_argument("--antialiasing-depth", type=int, default=2, 
                       help="Antialiasing depth (default: 2)")
    
    # AI models
    parser.add_argument("--model", dest="generator_model", 
                       help="Model for code generation (default: zaguanai/gemini-3-pro-preview)")
    parser.add_argument("--verifier-model", dest="verifier_model", 
                       help="Model for code verification (default: zaguanai/claude-sonnet-4.5-latest)")
    parser.add_argument("--no-verification", action="store_true", 
                       help="Skip code verification step")
    
    # Animation options
    parser.add_argument("--animate", action="store_true", 
                       help="Generate an animation")
    parser.add_argument("--duration", type=int, default=5, 
                       help="Animation duration in seconds (default: 5)")
    parser.add_argument("--fps", type=int, default=30, 
                       help="Animation frames per second (default: 30)")
    parser.add_argument("--frames", type=int, 
                       help="Number of animation frames (overrides --duration)")
    
    # Advanced options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--log-file", type=Path, 
                       help="Log file path (default: raylm.log)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Test configuration without generating anything")
    
    # Debug options
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug mode with extensive logging")
    
    args = parser.parse_args()
    
    # Configure logging level
    log_level = "DEBUG" if args.debug else ("INFO" if args.verbose else "WARNING")
    logger = setup_logging(log_level, str(args.log_file) if args.log_file else None)
    
    try:
        # Initialize RayLM
        config = RayLMConfig(
            output_dir=args.output_dir,
            generator_model=args.generator_model or "zaguanai/gemini-3-pro-preview",
            verifier_model=args.verifier_model or "zaguanai/claude-sonnet-4.5-latest" if not args.no_verification else None,
            default_timeout=args.timeout or 300
        )
        
        raylm = RayLM(config)
        
        if args.render:
            # Render existing file
            result = raylm.render_existing_file(
                args.render,
                width=args.width,
                height=args.height,
                quality=args.quality,
                timeout=args.timeout
            )
        elif args.prompt_file:
            # Read prompt from file
            if not args.prompt_file.exists():
                logger.error(f"Prompt file does not exist: {args.prompt_file}")
                sys.exit(1)
            
            prompt = args.prompt_file.read_text().strip()
            
            if not prompt:
                logger.error("Prompt file is empty")
                sys.exit(1)
            
            # Handle resolution presets
            resolution = args.resolution
            width, height = args.width, args.height
            
            if resolution and (width is None or height is None):
                width, height = raylm._parse_resolution_preset(resolution)
            
            # Ensure valid dimensions
            if width is None or height is None:
                width, height = raylm.config.default_width, raylm.config.default_height
            
            result = raylm.generate_scene(
                prompt,
                width=width,
                height=height,
                quality=args.quality,
                timeout=args.timeout,
                no_render=args.no_render,
                preview=args.preview,
                animate=args.animate,
                duration=args.duration,
                fps=args.fps,
                frames=args.frames,
                resolution=resolution
            )
        elif args.prompt:
            # Handle resolution presets
            resolution = args.resolution
            width, height = args.width, args.height
            
            if resolution and (width is None or height is None):
                width, height = raylm._parse_resolution_preset(resolution)
            
            # Ensure valid dimensions
            if width is None or height is None:
                width, height = raylm.config.default_width, raylm.config.default_height
            
            result = raylm.generate_scene(
                args.prompt,
                width=width,
                height=height,
                quality=args.quality,
                timeout=args.timeout,
                no_render=args.no_render,
                preview=args.preview,
                animate=args.animate,
                duration=args.duration,
                fps=args.fps,
                frames=args.frames,
                resolution=resolution
            )
        else:
            parser.print_help()
            sys.exit(1)
        
        # Handle result
        if result['success']:
            if 'output_file' in result:
                print(f"\n✅ Operation completed successfully!")
                print(f"📁 Scene file: {result['scene_file']}")
                print(f"🖼️  Output file: {result['output_file']}")
                
                # Print performance metrics if available
                metrics = result.get('metrics')
                if metrics and hasattr(metrics, 'duration'):
                    print(f"⏱️  Total time: {metrics.duration:.2f}s")
                    if 'render_time' in metrics.metadata:
                        print(f"🎬 Render time: {metrics.metadata['render_time']:.2f}s")
                    if 'verification_time' in metrics.metadata:
                        print(f"🔍 Verification time: {metrics.metadata['verification_time']:.2f}s")
            else:
                print(f"\n✅ Scene code generated successfully!")
                print(f"📁 Scene file: {result['scene_file']}")
        else:
            print(f"\n❌ Operation failed: {result.get('error', 'Unknown error')}")
            if 'scene_file' in result:
                print(f"📁 Scene file: {result['scene_file']}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except (RayLMConfigurationError, RayLMValidationError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except (RayLMAPIError, RayLMRenderingError) as e:
        logger.error(f"Operation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()