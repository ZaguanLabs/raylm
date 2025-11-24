# RayLM: LLM-Powered POV-Ray Scene Generator

RayLM is a Python script that leverages Large Language Models (LLMs) to automatically generate complex 3D scenes for POV-Ray (Persistence of Vision Raytracer). Unlike traditional approaches that require manual scene creation, RayLM automates the entire process using AI.

## How It Works

RayLM uses a multi-stage AI-powered workflow to generate and render POV-Ray scenes:

1. **Code Generation**: A generator LLM (default: Gemini 3 Pro) directly translates your text prompt into POV-Ray SDL (Scene Description Language) code, including camera, lighting, geometry, and materials.

2. **Syntax Verification**: A verifier LLM (default: Claude Sonnet 4.5) reviews the generated code for syntax errors, compliance with POV-Ray 3.7 standards, and structural correctness.

3. **Rendering**: POV-Ray renders the scene into an image or animation (using FFmpeg for video stitching).

4. **Auto-Repair Loop**: If rendering fails due to syntax errors, the verifier LLM automatically fixes the code and retries (up to 3 attempts).

This approach ensures high-quality, render-ready POV-Ray code with minimal manual intervention.

## Best Practices & Considerations

### Prompt Engineering for Optimal Results

To achieve the best possible output, your prompts should be:

- **Detailed and Specific**: Include precise descriptions of objects, positions, colors, materials, and lighting conditions
- **POV-Ray Aware**: Use POV-Ray-specific terminology and instructions when possible (e.g., "use a sphere with a chrome texture", "place a light_source at <10, 20, -30>")
- **Structured**: Break down complex scenes into clear components (geometry, materials, camera position, lighting)

### Example of a Good Prompt

Instead of: *"A red ball"*

Use: *"Create a sphere at the origin with radius 1.0, using a pigment of color red with a phong finish value of 0.9 and phong_size of 60 for a glossy appearance. Position the camera at <0, 2, -5> looking at <0, 0, 0>. Add a white light_source at <10, 10, -10> with intensity 1.5."*

### Iterative Refinement

The `instructions/` directory contains examples of prompt iterations developed with ChatGPT's assistance. These demonstrate how to progressively refine prompts to achieve better results. Review these files to understand effective prompting strategies for POV-Ray scene generation.

## Features

- **AI-Powered Scene Creation**: Automatically generates complex 3D scenes without manual modeling
- **Two-Step Generation Process**: Ensures coherent and well-structured scenes
- **POV-Ray Integration**: Outputs ready-to-render POV-Ray files
- **Flexible Prompting**: Accepts user prompts or generates random scenes
- **High-Quality Results**: Creates scenes with proper lighting, materials, and composition

## Requirements

- Python 3.7+
- **Zaguán API key** - Register at https://zaguanai.com
- **POV-Ray renderer (MANDATORY)** - Available at https://github.com/POV-Ray/povray
- **FFmpeg** (required for animation mode) - Available at https://ffmpeg.org

## Installation

1. Install POV-Ray from https://github.com/POV-Ray/povray
   - Follow the official installation instructions for your operating system
   - Ensure the `povray` command is available in your system PATH

2. Install FFmpeg (for animation support):
   - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from https://ffmpeg.org

3. Install Python dependencies:
```bash
pip install openai python-dotenv
```

**Note**: Only two Python packages are required:
- `openai` (required) - Used to communicate with the Zaguán Gateway
- `python-dotenv` (optional) - For loading environment variables from `.env` files

4. Set up your Zaguán API credentials:
```bash
export ZAGUAN_API_KEY="your_api_key_here"
export ZAGUAN_BASE_URL="your_zaguan_base_url"  # Optional
```

Or create a `.env` file in the project directory:
```
ZAGUAN_API_KEY=your_api_key_here
ZAGUAN_BASE_URL=your_zaguan_base_url
```

## Command Line Options

```bash
python raylm3.5.py [PROMPT] [options]
```

### Basic Options
- `PROMPT`: Scene description (positional argument, optional if using `--file` or `--render`)
- `-h, --help`: Show help message and exit
- `-f FILE, --file FILE`: Load prompt from a text file
- `--dry-run`: Generate and save POV-Ray code only (no rendering)
- `--render FILE`: Render an existing .pov file (skips AI generation)

### Animation Options
- `--animate`: Enable animation mode
- `--duration SECONDS`: Animation duration in seconds (default: 2.0)

### Rendering Options
- `--preview`: Fast, low-quality preview render (320x240 @ Q4)
- `--size {480p,720p,1080p,4k}`: Use preset resolution
- `--width WIDTH`: Custom width in pixels
- `--height HEIGHT`: Custom height in pixels
- `--fps FPS`: Frames per second for animation (default: 24)
- `--timeout SECONDS`: Render timeout in seconds (default: infinite)

### Model Options
- `--model MODEL`: Override default models (applies to both generator and verifier)

## Usage Examples

### 1. Basic Scene Generation
Generate a scene with a simple prompt:
```bash
python raylm3.5.py "A futuristic cityscape at sunset with flying cars"
```

### 2. Load Prompt from File
Use a text file containing your scene description:
```bash
python raylm3.5.py --file my_scene_prompt.txt
```

### 3. Generate Code Only (No Rendering)
Create POV-Ray code without rendering it:
```bash
python raylm3.5.py "A spaceship landing on Mars" --dry-run
```

### 4. Render Existing POV-Ray File
Render a previously generated or manually created .pov file:
```bash
python raylm3.5.py --render output/scenes/scene_20241124_120000.pov
```

### 5. Generate Animation
Create a 5-second animation at 30 FPS:
```bash
python raylm3.5.py "A rotating crystal sculpture" --animate --duration 5 --fps 30
```

### 6. High-Quality 4K Render
Generate a 4K resolution image:
```bash
python raylm3.5.py "A tranquil forest with a waterfall" --size 4k
```

### 7. Custom Resolution
Specify exact width and height:
```bash
python raylm3.5.py "An underwater coral reef" --width 2560 --height 1440
```

### 8. Quick Preview
Fast, low-quality preview for testing:
```bash
python raylm3.5.py "A mountain landscape" --preview
```

### 9. Use Custom Model
Override the default AI models:
```bash
python raylm3.5.py "A cyberpunk street" --model zaguanai/claude-sonnet-4.5-latest
```

### 10. Animation with Timeout
Generate animation with a render timeout to prevent hanging:
```bash
python raylm3.5.py "Spinning geometric shapes" --animate --duration 3 --timeout 300
```

### 11. Combine Prompt and File
Combine a file prompt with additional text:
```bash
python raylm3.5.py "with dramatic lighting" --file base_scene.txt
```

## Important Notes

### Zaguán API
This version (v3.5 - The Zaguán Edition) uses the Zaguán AI Gateway to access multiple LLM providers through a unified interface. You must have a valid `ZAGUAN_API_KEY` set in your environment or `.env` file. The script will exit with an error if the API key is not found.

Default models:
- **Generator**: `zaguanai/gemini-3-pro-preview`
- **Verifier**: `zaguanai/claude-sonnet-4.5-latest`

### POV-Ray Requirement
POV-Ray is a mandatory requirement for rendering. The script calls the `povray` command to render generated scenes. Without POV-Ray properly installed and accessible in your system PATH, the script will fail during the rendering phase.

### FFmpeg Requirement
FFmpeg is required only for animation mode (`--animate`). If you're only generating static images, FFmpeg is not necessary.

## Example Output

RayLM can generate scenes ranging from simple geometric arrangements to complex architectural visualizations, fantasy landscapes, and abstract art - all automatically created by the AI and rendered into video format.

## How It Differs From Standard LLM Usage

Rather than just describing scenes in text, RayLM actually produces executable POV-Ray code that can be directly rendered into photorealistic videos. This bridges the gap between creative AI and practical 3D rendering.

## License

This project is licensed under the MIT License - see the LICENSE file for details.