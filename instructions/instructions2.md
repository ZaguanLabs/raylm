You are generating POV-Ray 3.7 code.

Your ONLY task: output a single, complete, ready-to-render .pov scene that will compile in POV-Ray 3.7 **without manual fixes**.

Follow these rules strictly:

1. GENERAL RULES
   - Output ONLY POV-Ray code. No explanations, no Markdown, no comments outside of POV-Ray `//` comments.
   - Target: POV-Ray 3.7, no experimental features.
   - Do NOT use:
     - `isosurface`
     - `function`-based CSG
     - `#macro`
     - `#version` higher than 3.7
     - Any `#include` other than `colors.inc` and `textures.inc`
   - Code MUST be syntactically valid: every `{` has a `}`, no stray commas, no undefined identifiers.

2. THEME & LOOK
   - Scene: a gigantic ancient monolith in a desert at sunrise.
   - Mood: calm, eerie, majestic.
   - Composition:
     - Foreground: sand with visible ripples and at least one broken stone block.
     - Midground: the main monolith with carved geometric patterns.
     - Background: distant dunes fading into light haze.

3. STRUCTURE TEMPLATE (YOU MUST FOLLOW THIS ORDER)
   You MUST structure your code in this order:

   a) Global settings and includes  
   b) Camera  
   c) Light source(s)  
   d) Sky and atmosphere (simple)  
   e) Reusable textures  
   f) Ground plane (desert)  
   g) Foreground details (rock, broken pillar)  
   h) Main monolith  
   i) Optional small details (scattered stones, etc.)

4. GLOBAL SETTINGS
   - Use `global_settings` with:
     - `assumed_gamma 1.0`
     - moderate radiosity (simple, not over-tuned)
   - Example style (you MUST adapt, not copy blindly):

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

   - You may adjust numbers but keep them reasonable.

5. CAMERA
   - Perspective camera.
   - Location: near ground, slightly off-center, looking up toward the monolith.
   - Focal length: use `angle` between 35 and 55.
   - No depth-of-field for now (easier to keep things valid).

6. LIGHTING
   - Main light: low-angle warm sun (like early sunrise).
   - One directional light or a distant light at low altitude.
   - Optionally: a very faint fill light to avoid totally black shadows, but keep contrast high.

7. SKY & ATMOSPHERE
   - Simple `sky_sphere` with subtle gradient: darker at zenith, lighter near horizon.
   - Optional: simple `fog` with light color to add depth.
   - Do NOT use complex `media` or volume scattering: too error-prone.

8. TEXTURES
   - Define at least:
     - A sand texture: layered pigment + `bump` or `normal` to suggest ripples.
     - A stone texture for the monolith and broken blocks.
   - Use only built-in patterns: `granite`, `bumps`, `wrinkles`, `bozo`, etc.
   - Keep finish realistic:
     - sand: mostly diffuse, low specular
     - stone: diffuse with small specular and roughness

   Example style (you MUST create your own, not copy exactly):

     #declare Sand_Texture = texture {
       pigment {
         color rgb <0.85, 0.75, 0.55>
       }
       normal {
         bumps 0.6
         scale 0.3
       }
       finish {
         diffuse 0.9
         specular 0.05
       }
     }

9. GROUND (DESERT)
   - Use a large plane `y, 0` with the sand texture.
   - Add variation using `texture { Sand_Texture }` and scaling to make ripples plausible at human scale.

10. FOREGROUND ELEMENTS
   - At least one broken stone block or fragment:
     - Use simple CSG: `difference { box {...} ... }` to make a chipped corner.
     - Place it near the camera, partially buried in sand.

11. MAIN MONOLITH
   - Tall structure (at least 40 units in height).
   - Built from simple CSG primitives:
     - `box`, `cylinder`, `difference`, `union`
   - Add carved patterns by subtracting or intersecting with smaller shapes:
     - shallow grooves using long thin boxes in `difference`
   - Use the stone texture (or a derived variant).

12. SMALL DETAILS
   - Optional, but recommended:
     - a few scattered stones
     - slight tilt of some elements to avoid everything looking perfect

13. NAMING AND CLEANLINESS
   - Every reusable element must be defined with `#declare` before use.
   - No undefined identifiers. If you name `Monolith_Texture`, you must define it.
   - Keep indentation readable.

14. FINAL CHECKLIST (YOU MUST SATISFY ALL)
   - Exactly ONE `camera` block.
   - At least ONE `light_source` block.
   - At least ONE plane for ground.
   - At least ONE large monolith object.
   - At least ONE foreground stone or broken block.
   - All `#declare` variables used are defined.
   - No `TODO`, no comments about missing parts.

Now generate the complete POV-Ray scene, following all the rules above. Output ONLY the .pov code.
