# RayLM Project Context

## Project Overview

RayLM is a Python-based AI-powered tool that automatically generates 3D scenes for POV-Ray (Persistence of Vision Raytracer) using Large Language Models. The project leverages a multi-stage workflow where AI models generate POV-Ray Scene Description Language (SDL) code from text prompts, verify syntax compliance, and handle rendering with automatic error correction.

## Project Type

This is a **Python CLI application** that combines AI/LLM integration with 3D rendering workflows.

## Key Technologies

- **Language**: Python 3.7+
- **AI Integration**: Zaguán AI Gateway (OpenAI-compatible API)
- **3D Rendering**: POV-Ray 3.7
- **Video Processing**: FFmpeg (for animation mode)
- **Dependencies**: `openai`, `python-dotenv`

## Architecture

The application follows a multi-stage pipeline:

1. **Code Generation**: Uses Gemini 3 Pro via Zaguán Gateway to generate POV-Ray SDL code
2. **Syntax Verification**: Uses Claude Sonnet 4.5 to verify and correct code compliance
3. **Rendering**: POV-Ray renders scenes to images or animations
4. **Auto-Repair Loop**: Automatically fixes syntax errors and retries rendering

## Directory Structure

```
/home/stig/dev/ai/zaguan/labs/raylm/
├── raylm3.5.py          # Main application script
├── README.md              # Comprehensive documentation
├── LICENSE                # MIT License
├── QWEN.md                # This file
├── .gitignore            # Git ignore rules
├── instructions/           # Prompt engineering examples
│   ├── instructions.md
│   ├── instructions2.md
│   ├── instructions3.md
│   ├── instructions4.md
│   ├── instructions5.md
│   ├── instructions6.md
│   ├── instructions7.md
│   ├── instructions8.md
│   ├── instructions9.md
│   └── instructions10.md
└── output/                # Generated content (created at runtime)
    ├── scenes/            # Generated POV-Ray scene files
    └── renders/           # Rendered images and animations
```

## Building and Running

### Prerequisites
- Python 3.7+
- POV-Ray renderer (mandatory)
- FFmpeg (for animation mode)
- Zaguán API key

### Installation
```bash
# Install Python dependencies
pip install openai python-dotenv

# Set up Zaguán API credentials
export ZAGUAN_API_KEY="your_api_key_here"
export ZAGUAN_BASE_URL="your_zaguan_base_url"  # Optional
```

### Basic Usage
```bash
# Generate and render a scene
python raylm3.5.py "A futuristic cityscape at sunset with flying cars"

# Generate code only (no rendering)
python raylm3.5.py "A spaceship landing on Mars" --no-render

# Render existing POV-Ray file
python raylm3.5.py --render output/scenes/scene_20241124_120000.pov

# Generate animation
python raylm3.5.py "A rotating crystal sculpture" --animate --duration 5 --fps 30
```

## Development Conventions

### Code Style
- Python 3.7+ compatible
- Type hints used throughout (Python typing module)
- Comprehensive docstrings
- Error handling with meaningful messages

### Project Configuration
- Uses environment variables for configuration (`.env` file supported)
- Default models: `zaguanai/gemini-3-pro-preview` (generator), `zaguanai/claude-sonnet-4.5-latest` (verifier)
- Output directory structure created automatically
- Temporary files managed in system temp directory

### Error Handling
- Graceful handling of missing dependencies
- Automatic retry mechanism for rendering failures
- Timeout support for long-running renders
- Detailed error reporting from POV-Ray and FFmpeg

### Testing
- No formal test suite - relies on manual testing and rendering verification
- Preview mode available for quick testing (320x240 @ Q4)

## Key Features

- **AI-Powered Scene Creation**: Automatic generation of complex 3D scenes
- **Two-Step Verification**: Ensures syntactically correct POV-Ray code
- **Flexible Prompting**: Accepts text prompts or file-based input
- **Animation Support**: Can generate video sequences with FFmpeg
- **Auto-Repair**: Automatically fixes syntax errors in generated code
- **Multiple Resolutions**: Supports preset resolutions (480p, 720p, 1080p, 4K) and custom sizes

## Important Notes

- Requires Zaguán API key - project will not function without it
- POV-Ray installation is mandatory - no fallback rendering available
- Animation mode requires FFmpeg for video stitching
- Generated scenes include standard POV-Ray includes (colors.inc, textures.inc, etc.)
- Supports clock-based animation for time-based rendering