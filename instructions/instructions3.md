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
   c) `#declare` constants (e.g., paths, radii, animation helpers)  
   d) camera block (using `clock`)  
   e) light sources (sun + optional fill)  
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
   - Interpolate camera position and look_at based on `clock`.

   Example concept (PSEUDOCODE ONLY, do not literally copy):
   - Start position: < -80, 10, -40 >
   - End position:   < -30, 15, -10 >
   - Use linear interpolation based on `clock`.

   - `look_at` should always roughly point at the monolith center, but you can add a slight vertical or lateral offset that changes with `clock` for subtle motion.

6. LIGHTING

   - Main light: low-angle warm sun (as if sunrise).
     - Position it far away in a direction that makes the monolith cast long shadows.
   - Optional: very faint fill light with cool tone to lift deep shadows.
   - No area lights (to keep syntax simple and render time under control).

7. SKY & FOG

   - Use a `sky_sphere` with a soft gradient (darker zenith, lighter horizon).
   - Optional: simple `fog` with large `distance` to suggest atmospheric depth.

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
     - noticeable specular and reflection (but not mirror-perfect)

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

11. HOVERING PROBE (MUST ORBIT USING `clock`)

   - A small sphere or simple CSG shape representing a probe.
   - Use `Metal_Texture`.
   - Position: orbit around monolith in a horizontal circle using sine/cosine of `clock`.

   For example STYLE (you must implement your own numbers):

   - radius ~ 10–20 units from monolith center.
   - height ~ 10–20 units above ground.
   - position = < cos(clock * 2*pi)*radius, height, sin(clock * 2*pi)*radius >

   - Optionally add a faint light source near the probe to make it glow.

12. OPTIONAL SMALL DETAILS

   - A few scattered stone chunks (simple boxes or irregular unions) around the base of the monolith.
   - Slight random rotations/tilts to avoid a sterile look.

13. NAMING & CLEANLINESS

   - All reusable items must be declared with `#declare` before they’re used.
   - No undefined variables.
   - Indent in a readable way.
   - No commented-out unfinished code.

14. FINAL CHECKLIST (ALL REQUIRED)

   Your final code MUST have:

   - `#include "colors.inc"`
   - `global_settings` with `assumed_gamma` and radiosity.
   - Exactly one `camera` block, using `clock` to animate motion.
   - At least one `light_source`.
   - One `sky_sphere` (and optional fog).
   - A ground plane with sand texture.
   - A monolith object whose rotation depends on `clock`.
   - A hovering probe whose orbit depends on `clock`.
   - No syntax errors, no undefined identifiers.

Now generate the complete POV-Ray scene using these rules. Output ONLY the .pov code.
