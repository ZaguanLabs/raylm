#!/usr/bin/env python3
"""
rayLM: Text-to-POV-Ray Scene Generator (v3.5 - The Zaguán Edition)
------------------------------------------------------------------
Changes in this version:
1. NATIVE ZAGUÁN SUPPORT: Uses ZAGUAN_API_KEY and ZAGUAN_BASE_URL.
2. GATEWAY MODE: Removed Anthropic SDK; all traffic goes via Zaguán gateway using OpenAI client.
3. ONBOARDING: Helpful error message if API key is missing.
"""

import os
import sys
import re
import subprocess
import argparse
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

# Try to load .env, but don't crash if missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==========================================
# ⚙  USER CONFIGURATION
# ==========================================

# Default models via Zaguán Gateway
MODEL_GENERATOR = "zaguanai/gemini-3-pro-preview"
MODEL_VERIFIER  = "zaguanai/claude-sonnet-4.5-latest"

# ==========================================

SIZE_PRESETS = {
    "480p":  (854, 480),
    "720p":  (1280, 720),
    "1080p": (1920, 1080),
    "4k":    (3840, 2160),
}

# --- The Template ---
BASE_SCENE_TEMPLATE = """
#version 3.7;

// --- Standard Includes ---
#include "colors.inc"
#include "textures.inc"
#include "glass.inc"
#include "metals.inc"
#include "golds.inc"
#include "stones.inc"
#include "woods.inc"
#include "shapes.inc"

global_settings {
    assumed_gamma 1.0
    max_trace_level 20
}

// Note: No default camera or lights. The AI MUST generate them.
"""

# ==============================================================================
#  SYSTEM PROMPTS
# ==============================================================================

SYSTEM_PROMPT_GEN = r"""
You are rayLM, a high-fidelity POV-Ray 3.7 Scene Description Generator.

Your role: Translate user requests into syntactically correct, render-ready POV-Ray SDL code.

=================================================
CORE OUTPUT RULES
=================================================
1. Output ONLY raw POV-Ray SDL code.
   - No explanations
   - No comments unless user explicitly requests comments
   - No markdown fences

2. The following include files are already provided and MUST NOT be redefined:
   - colors.inc
   - textures.inc
   - metals.inc
   - glass.inc
   - shapes.inc
   - woods.inc
   - stones.inc
   - golds.inc

3. You MUST generate:
   - exactly one camera block
   - at least one light_source block
   - all geometry described by the user

4. Never use:
   - isosurfaces
   - parametric functions
   - mesh2
   - unsupported features
   - macros (#macro)
   - version > 3.7

5. Maintain strict POV-Ray nesting:
   - texture { pigment { color rgb <...> } finish { ... } }
   - object { ... translate <...> rotate <...> scale <...> }

6. All vectors MUST use angle-bracket syntax <x,y,z>.

=================================================
CAMERA SPECIFICATION
=================================================
If user does not specify a camera:
- default to:
  camera { location <0, 2, -5> look_at <0,0,0> right x*image_width/image_height }

If user does specify a camera:
- follow instructions exactly.

=================================================
LIGHTING SPECIFICATION
=================================================
If user provides lighting instructions:
- follow them precisely.

If user does NOT specify lighting:
- provide at least one white light_source positioned logically
  (e.g., above and behind the camera).

=================================================
GEOMETRY SPECIFICATION
=================================================
Allowed primitives:
- sphere, box, cylinder, cone, torus, plane
- union, difference, intersection, merge

If user mentions motion or animation:
- use clock (0.0 to 1.0) only
- ensure all animated values evaluate cleanly at 0.0 and 1.0

=================================================
FAIL-SAFE RULES
=================================================
- All braces must balance.
- All identifiers must be declared before use.
- No references to files or fonts that do not exist.
- Use only standard materials unless user defines new ones.

=================================================
STRATEGY
=================================================
- Interpret all user descriptions literally.
- Do not impose style, tone, mood, or artistic preference unless the user asks.
- Only describe geometry and materials required by the user.

When constructing letters from boxes, you MUST:
- Never use negative scaling (e.g. scale <-1,1,1>).
- Never mirror geometry.
- Always build letter geometry facing positive +z direction.
- Keep all letter unions aligned with increasing +x for correct left-to-right layout.
"""

SYSTEM_PROMPT_VERIFIER = r"""
You are rayLM-Verifier, a strict POV-Ray 3.7 Syntax Officer.

INPUTS:
1. User request
2. Draft code

REQUIRED OUTPUT:
- Return ONLY corrected SDL code with no commentary, no markdown.

VERIFICATION PROCEDURE:
1. Syntax:
   - Balanced braces
   - Valid nesting of pigment/finish/texture
   - Valid camera block
   - At least one light_source
   - No unknown keywords
   - No macros
   - No isosurfaces

2. Safety:
   - No external font files unless standard POV-Ray core fonts
   - No undefined identifiers
   - No duplicate camera blocks
   - No repeated global_settings unless required by user

3. Compliance:
   - All required geometry appears
   - Animation uses clock correctly if present

RETURN:
- Fully corrected SDL code only.
"""

class RayLMConfig:
    def __init__(self):
        # 1. Load Zaguán credentials
        self.zaguan_api_key = os.getenv("ZAGUAN_API_KEY")
        self.zaguan_base_url = os.getenv("ZAGUAN_BASE_URL")

        # 2. Verify Credentials
        if not self.zaguan_api_key:
            print("\n" + "!"*60)
            print(" ERROR: Zaguán API key not found in environment variables.")
            print(" Please set ZAGUAN_API_KEY.")
            print(" Register at https://zaguanai.com and get your key.")
            print("!"*60 + "\n")
            sys.exit(1)

        # 3. Model Defaults
        self.model_gen = MODEL_GENERATOR
        self.model_ver = MODEL_VERIFIER

        # 4. Processing Defaults
        self.max_retries = 3
        self.output_dir = Path("output")
        self.scenes_dir = self.output_dir / "scenes"
        self.temp_dir = Path(tempfile.gettempdir()) / "raylm"

        # Rendering Defaults
        self.width = 800
        self.height = 600
        self.fps = 24
        self.quality = 9
        self.timeout = None

        # Create Directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

class LLMClient:
    def __init__(self, config: RayLMConfig):
        self.config = config

    def generate_draft(self, user_request: str) -> str:
        return self._call_zaguan(SYSTEM_PROMPT_GEN, user_request, self.config.model_gen)

    def verify_draft(self, user_request: str, draft_code: str) -> str:
        verification_payload = f"""
### 1. USER REQUEST
{user_request}

### 2. DRAFT CODE
{draft_code}

Review the code. Fix syntax errors. Ensure compliance with POV-Ray 3.7 standards.
Return FINAL CODE only.
"""
        return self._call_zaguan(SYSTEM_PROMPT_VERIFIER, verification_payload, self.config.model_ver)

    def fix_runtime_error(self, code: str, error: str) -> str:
        fix_prompt = f"""
### RENDERER ERROR
{error}

### FAILED CODE
{code}

Fix the syntax error shown in the log. Return ONLY valid SDL code.
"""
        return self._call_zaguan("You are a POV-Ray Debugger.", fix_prompt, self.config.model_ver)

    def _call_zaguan(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """
        Unified call to Zaguán Gateway using standard OpenAI Client.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI module not found. Run: pip install openai")

        try:
            # We use the standard OpenAI client, but point it to Zaguán's Base URL
            client = OpenAI(
                api_key=self.config.zaguan_api_key,
                base_url=self.config.zaguan_base_url
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            return self._clean_code(response.choices[0].message.content)
        except Exception as e:
            raise RuntimeError(f"Zaguán API Error: {str(e)}")

    def _clean_code(self, code: str) -> str:
        if not code: return ""
        code = re.sub(r'^```(?:povray|pov)?\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
        return code.strip()

class POVRayRenderer:
    def __init__(self, config: RayLMConfig):
        self.config = config

    def check_installed(self) -> bool:
        return shutil.which("povray") is not None

    def render_image(self, scene_file: Path, output_file: Path) -> Tuple[bool, Optional[str]]:
        cmd = [
            "povray",
            f"+I{scene_file}",
            f"+O{output_file}",
            f"+W{self.config.width}",
            f"+H{self.config.height}",
            f"+Q{self.config.quality}",
            "+FN", "-D", "+A0.3"
        ]
        return self._run_povray(cmd, cwd=scene_file.parent)

    def render_animation(self, scene_file: Path, output_dir: Path, num_frames: int) -> Tuple[bool, Optional[str]]:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(exist_ok=True)

        cmd = [
            "povray",
            f"+I{scene_file}",
            f"+O{output_dir}/raw_",
            f"+W{self.config.width}",
            f"+H{self.config.height}",
            f"+Q{self.config.quality}",
            "+FN", "-D",
            f"+KFF{num_frames}", "+KI0.0", "+KF1.0"
        ]
        return self._run_povray(cmd, cwd=scene_file.parent)

    def _run_povray(self, cmd: List[str], cwd: Path) -> Tuple[bool, Optional[str]]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=cwd
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr + "\n" + result.stdout
        except subprocess.TimeoutExpired:
            return False, "Rendering timed out."
        except Exception as e:
            return False, str(e)

class VideoStitcher:
    def check_installed(self) -> bool:
        return shutil.which("ffmpeg") is not None

    def normalize_frames(self, frames_dir: Path) -> bool:
        files = sorted(list(frames_dir.glob("*.png")))
        if not files: return False

        for i, file_path in enumerate(files):
            new_name = frames_dir / f"img_{i+1:04d}.png"
            file_path.rename(new_name)
        return True

    def stitch(self, frames_dir: Path, output_file: Path, fps: int) -> Tuple[bool, Optional[str]]:
        if not self.normalize_frames(frames_dir):
            return False, "No frames found."

        input_pattern = frames_dir / "img_%04d.png"
        cmd = [
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(input_pattern),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(output_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=None)
            if result.returncode == 0: return True, None
            return False, result.stderr
        except Exception as e:
            return False, str(e)

class RayLM:
    def __init__(self, config: RayLMConfig):
        self.config = config
        self.llm = LLMClient(config)
        self.renderer = POVRayRenderer(config)
        self.stitcher = VideoStitcher()

    def _save_history_file(self, code: str) -> Path:
        """Saves a standalone .pov file to the history directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scene_{timestamp}.pov"
        filepath = self.config.scenes_dir / filename

        with open(filepath, 'w') as f:
            f.write(BASE_SCENE_TEMPLATE)
            f.write("\n// --- AI Generated Content Below ---\n")
            f.write(code)
        return filepath

    def _create_temp_scene(self, code: str) -> Path:
        """Creates a temp file for the render/repair loop (includes template)"""
        scene_file = self.config.temp_dir / "scene.pov"
        with open(scene_file, 'w') as f:
            f.write(BASE_SCENE_TEMPLATE)
            f.write("\n// --- AI Generated Content Below ---\n")
            f.write(code)
        return scene_file

    def _extract_relevant_error(self, full_log: str) -> str:
        lines = full_log.splitlines()
        relevant = []
        capture = False
        for line in lines:
            if "Parse Error" in line or "Fatal error" in line:
                relevant.append(line)
                capture = True
            elif "Parse Warning" in line:
                continue
            elif capture and len(relevant) < 10:
                relevant.append(line)
        return "\n".join(relevant) if relevant else "\n".join(lines[-20:])

    def run(self, full_prompt: str, animate: bool, duration: float, no_render: bool, render_file: str):
        if not self.renderer.check_installed():
            print("ERROR: 'povray' not found.")
            return
        if animate and not self.stitcher.check_installed():
            print("ERROR: 'ffmpeg' not found.")
            return

        print("=" * 60)
        print(f"🚀 rayLM v3.5 (The Zaguán Edition)")
        print(f"   - Gateway: {self.config.zaguan_base_url or 'Default OpenAI'}")
        print(f"   - Res:     {self.config.width}x{self.config.height} @ Q{self.config.quality}")
        if self.config.timeout:
            print(f"   - Timeout: {self.config.timeout}s")
        print("=" * 60)

        # --- PATH SELECTION ---
        scene_path_to_render = None
        current_code = None

        if render_file:
            # ➡ DIRECT RENDER MODE
            print(f"\n📁 Mode: Render Existing File")
            p = Path(render_file)
            if not p.exists():
                print(f"ERROR: File not found: {render_file}")
                return
            scene_path_to_render = p
            print(f"   Target: {scene_path_to_render}")

        else:
            # ➡ GENERATION MODE
            print(f"\n🧠 Mode: Zaguán Generation")
            print(f"   - Gen: {self.config.model_gen}")
            print(f"   - Ver: {self.config.model_ver}")

            # 1. GENERATE
            print("\n⚙  Generating SDL Code...")
            draft_code = self.llm.generate_draft(full_prompt)

            # 2. VERIFY
            print("\n🔍 Verifying Syntax & Compliance...")
            current_code = self.llm.verify_draft(full_prompt, draft_code)

            # 3. SAVE HISTORY
            saved_path = self._save_history_file(current_code)
            print(f"\n💾 Saved to History: {saved_path}")

            if no_render:
                print("\n✨ Code Generation Complete. Exiting.")
                return

            # Prepare for rendering loop
            scene_path_to_render = self._create_temp_scene(current_code)

        # --- RENDER LOOP ---
        can_auto_repair = (current_code is not None)

        for attempt in range(self.config.max_retries):
            print(f"\n🎬 Render Attempt {attempt + 1}")

            if can_auto_repair and attempt > 0:
                 scene_path_to_render = self._create_temp_scene(current_code)

            success = False
            error = None
            output_path = None
            is_syntax = True

            if animate:
                frames = int(duration * self.config.fps)
                frames_dir = self.config.temp_dir / "frames"

                print(f"   Rendering Animation ({frames} frames)...")
                print("   (Press Ctrl+C to abort if stuck)")
                success, error = self.renderer.render_animation(scene_path_to_render, frames_dir, frames)

                if success:
                    print("   Stitching Video...")
                    out_vid = self.config.output_dir / f"anim_{int(time.time())}.mp4"
                    vid_success, vid_err = self.stitcher.stitch(frames_dir, out_vid, self.config.fps)
                    if vid_success: output_path = out_vid
                    else:
                        success = False
                        error = f"Stitching: {vid_err}"
                        is_syntax = False
                    if frames_dir.exists(): shutil.rmtree(frames_dir, ignore_errors=True)
            else:
                print("   Rendering Image...")
                print("   (Press Ctrl+C to abort if stuck)")
                out_img = self.config.output_dir / f"render_{int(time.time())}.png"
                success, error = self.renderer.render_image(scene_path_to_render, out_img)
                if success: output_path = out_img

            if success:
                print(f"\n✅ Output: {output_path}")
                return
            else:
                print(f"❌ Failed.")
                if not is_syntax:
                    print(f"   System Error: {error}")
                    break

                clean_error = self._extract_relevant_error(error)
                print(f"   Error: {clean_error}")

                if can_auto_repair and attempt < self.config.max_retries - 1:
                    print("   🚑 Auto-repairing via Zaguán...")
                    current_code = self.llm.fix_runtime_error(current_code, clean_error)
                else:
                    if not can_auto_repair:
                        print("   (Auto-repair unavailable in --render mode)")
                    print("   💀 Retries exhausted.")
                    return

def main():
    parser = argparse.ArgumentParser(description="rayLM: Zaguán AI POV-Ray Generator")
    parser.add_argument("prompt", nargs="?", help="Scene description")
    parser.add_argument("--file", "-f", help="Load prompt from file")

    parser.add_argument("--no-render", action="store_true", help="Generate and save only (no render)")
    parser.add_argument("--render", help="Render an existing .pov file (skips AI)")

    parser.add_argument("--animate", action="store_true", help="Animation mode")
    parser.add_argument("--duration", type=float, default=2.0)

    parser.add_argument("--preview", action="store_true", help="Fast, low-quality preview render")
    parser.add_argument("--size", choices=SIZE_PRESETS.keys())
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--timeout", type=int, help="Render timeout in seconds (Default: Infinite)")

    parser.add_argument("--model", help="Override models")

    args = parser.parse_args()

    # Validation
    if args.render:
        final_prompt = ""
    else:
        full_prompt_parts = []
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    c = f.read().strip()
                    if c: full_prompt_parts.append(c)
            except Exception as e:
                print(f"File Error: {e}")
                sys.exit(1)
        if args.prompt: full_prompt_parts.append(args.prompt)

        if not full_prompt_parts:
            parser.error("You must provide PROMPT/--file OR use --render.")
        final_prompt = "\n".join(full_prompt_parts)

    config = RayLMConfig()
    if args.model:
        config.model_gen = args.model
        config.model_ver = args.model

    # Handle Preview Mode
    if args.preview:
        config.width = 320
        config.height = 240
        config.quality = 4
        print(">> PREVIEW MODE ACTIVE: 320x240 @ Q4")
    else:
        if args.size: config.width, config.height = SIZE_PRESETS[args.size]
        if args.width: config.width = args.width
        if args.height: config.height = args.height

    config.fps = args.fps
    config.timeout = args.timeout

    app = RayLM(config)
    try:
        app.run(final_prompt, args.animate, args.duration, args.no_render, args.render)
    except KeyboardInterrupt:
        print("\nAborted.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
