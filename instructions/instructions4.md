You are generating POV-Ray 3.7 code that is intended for ANIMATION.

Your ONLY task: output a single, complete, ready-to-render .pov scene that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Uses the built-in variable `clock` (assumed range 0.0 to 1.0) to animate the scene.
- Looks good for ANY frame in the interval 0.0 ≤ clock ≤ 1.0.

You MUST follow these rules exactly:

1. GENERAL RULES
   - Output ONLY POV-Ray code. No explanations, no Markdown.
   - Target: POV-Ray 3.7.
   - Allowed includes: only `colors.inc` and `textures.inc`.
   - Do NOT use:
     - `isosurface`
     - user-defined `function`
     - `#macro`
     - `#version` higher than 3.7
     - complex `media` volumes
   - All identifiers must be defined before use.
   - Every `{` must have a matching `}`.

2. THEME & ANIMATION CONCEPT

   Scene: An ancient monolith in a desert at sunrise.

   Over the course of the animation (clock from 0 to 1):
   - The CAMERA slowly moves in an arc around the monolith and slightly forward.
   - The MONOLITH slowly rotates around its vertical axis (y-axis).
   - A small hovering probe (a simple sphere with metallic texture) orbits the monolith.

   The idea:
   - At clock=0: camera further away and to the left; monolith rotation angle 0; probe near the far side.
   - At clock=1: camera closer and more centered; monolith rotated ~90–120 degrees; probe circled significantly.

3. MANDATORY STRUCTURE (ORDER)

   You MUST structure your code in this order:

   a) `#include` directives  
   b) `global_settings`  
   c) `#declare` constants (e.g., paths, radii, animation helpers, PI)  
   d) camera block (using `clock`)  
   e) light sources (sun + optional fill + probe light)  
   f) sky and optional fog  
   g) textures (sand, stone, metal)  
   h) ground plane  
   i) monolith object (animated rotation)  
   j) probe object (orbiting using `clock`)  
   k) optional scattered stones

4. GLOBAL SETTINGS

   - Use `assumed_gamma 1.0`.
   - Use simple radiosity as in this STYLE (adapt, do not copy verbatim):

     global_settings {
       assumed_gamma 1.0
       radiosity {
         pretrace_start 0.08
         pretrace_end   0.01
         count 100
         nearest_count 5
         recursion_limit 1
         low_error_factor 0.5
       }
     }

5. CAMERA (MUST USE `clock`)

   - Perspective camera.
   - Use `angle` between 35 and 55.
   - Camera motion MUST be smooth and non-jerky:
     - Either:
       - Use linear interpolation between a start and end position, OR
       - Preferably, define a simple `spline` path (e.g. `linear_spline` or `cubic_spline`) and sample it with `CamPath(clock)`.
   - Example concept (PSEUDOCODE ONLY, do not literally copy values):
     - Start position: < -80, 10, -40 >
     - End position:   < -30, 15, -10 >
   - `look_at` should always roughly point at the monolith center, with a slight vertical or lateral offset that changes with `clock` for subtle motion.
   - You may add a very subtle “breathing” FOV effect, e.g.:
     - `angle 40 + 2 * sin(clock * 2 * PI)`
     - If you use `sin`/`cos`, you MUST define `#declare PI = 3.14159;` in the constants section.

6. LIGHTING

   - Main light: low-angle warm sun (as if sunrise).
     - Position it far away in a direction that makes the monolith cast long shadows.
   - Optional: very faint fill light with a cooler tone to lift deep shadows without killing contrast.
   - The lighting should not be static:
     - You may slightly vary the intensity or color temperature over time, using `sin(clock * n * PI)` modulation to keep it subtle.
   - No area lights (to keep syntax simple and render time under control).

7. SKY & FOG

   - Use a `sky_sphere` with a soft gradient (darker zenith, lighter horizon).
   - Optional: simple `fog` with large `distance` to suggest atmospheric depth. Keep it subtle so the monolith and probe remain clearly visible.

8. TEXTURES

   Define at least these textures with `#declare`:

   - `Sand_Texture`:
     - warm sandy color
     - `normal` bumps to simulate ripples
   - `Stone_Texture`:
     - neutral stone color
     - subtle noise and roughness
   - `Metal_Texture`:
     - cool or slightly colored metal
     - noticeable specular and some reflection (but not mirror-perfect)

   Use only built-in patterns (`granite`, `bozo`, `bumps`, `wrinkles`, etc.).

9. GROUND (DESERT)

   - A plane `y, 0` with `Sand_Texture`.
   - Scale the texture so ripple pattern size looks plausible at human scale.
   - Use only one plane (no height fields).

10. MONOLITH (MUST ANIMATE ROTATION)

   - Constructed via CSG from basic primitives: `box`, `cylinder`, `difference`, `union`.
   - Tall structure: at least 40 units high.
   - Add simple carved detail using `difference` with thin boxes.
   - The whole monolith must be rotated around y-axis using `clock`, e.g.:

     rotate <0, SomeAngle * clock, 0>

     where `SomeAngle` is between 90 and 150 degrees.

   - Apply `Stone_Texture` (or a variant).
   - Small tilts, bevels or offsets are allowed to make it feel less perfectly machined.

11. HOVERING PROBE (MUST ORBIT USING `clock`)

   - A small sphere or simple CSG shape representing a probe.
   - Use `Metal_Texture`.
   - Position: orbit around monolith in a horizontal circle using sine/cosine of `clock`.

   Example STYLE (you must implement your own numbers):

   - radius ~ 10–20 units from monolith center.
   - height ~ 10–20 units above ground.
   - position = < cos(clock * 2*PI)*radius, height, sin(clock * 2*PI)*radius >

   - Attach a light source to the probe so it glows and illuminates nearby geometry:
     - Light position exactly at the probe position.
     - Color and/or intensity may vary slightly over time using `sin`/`cos` to simulate pulsation.
   - You may add a faint secondary light slightly ahead of the probe along its orbit path (e.g. a point close to the ground) to suggest light spilling onto the sand.

12. OPTIONAL SMALL DETAILS

   - A few scattered stone chunks (simple boxes or irregular unions) around the base of the monolith.
   - Slight random rotations/tilts to avoid a sterile look.
   - These objects should also be affected by the probe’s moving light (i.e., just regular geometry in the scene).

13. NAMING & CLEANLINESS

   - All reusable items must be declared with `#declare` before they’re used.
   - Define `#declare PI = 3.14159;` if you use trigonometric functions with angles.
   - No undefined variables.
   - Indent in a readable way.
   - No commented-out unfinished code.

14. FINAL CHECKLIST (ALL REQUIRED)

   Your final code MUST have:

   - `#include "colors.inc"`
   - `global_settings` with `assumed_gamma` and radiosity.
   - Exactly one `camera` block, using `clock` to animate motion (linear or spline-based).
   - At least one main `light_source` for the sun.
   - A light attached to the probe that moves with it.
   - One `sky_sphere` (and optional fog).
   - A ground plane with sand texture.
   - A monolith object whose rotation depends on `clock`.
   - A hovering probe whose orbit depends on `clock`.
   - No syntax errors, no undefined identifiers.

Now generate the complete POV-Ray scene using these rules. Output ONLY the .pov code.
