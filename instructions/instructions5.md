You are generating POV-Ray 3.7 code that is intended for ANIMATION.

Your ONLY task: output a single, complete, ready-to-render .pov scene that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Uses the built-in variable `clock` (range 0.0 to 1.0) to animate the scene.
- Recreates a simplified 3D version of the **Zaguán AI** archway logo in brand colors.
- Produces a clean, cinematic logo reveal that looks good for ANY frame 0.0 ≤ clock ≤ 1.0.

You MUST follow these rules exactly.

--------------------------------------------------
1. GENERAL RULES
--------------------------------------------------

- Output ONLY POV-Ray code. No explanations, no Markdown.
- Target: POV-Ray 3.7.
- Allowed includes: only `"colors.inc"` and `"textures.inc"`.
- Do NOT use:
  - `isosurface`
  - user-defined `function`
  - `#macro`
  - `#version` higher than 3.7
  - complex `media` volumes
- All identifiers must be defined before use.
- Every `{` must have a matching `}`.
- Keep the scene centered around the origin (0,0,0) for the logo.

--------------------------------------------------
2. BRAND & LOOK
--------------------------------------------------

You are approximating the Zaguán AI archway logo as 3D geometry:

- A stylized archway made of teal-colored elements.
- A horizontal golden “passage” bar with an arrow head pointing to the right.
- The word “ZAGUÁN” in teal and “AI” in gold, in simple 3D extruded text or blocks that approximate the typography.
  - If text is too error-prone, you may approximate it with simple rectangular extruded blocks in the correct colors, laid out in a line.

Color palette (approximate, use these rgb values):

- Teal (primary):  `rgb <0.06, 0.34, 0.43>`
- Gold (accent):   `rgb <0.86, 0.69, 0.34>`
- Background:      very light warm gray, not pure white: `rgb <0.96, 0.96, 0.94>`

The logo should sit on a simple floor plane with soft reflections, in a clean “studio” environment – no desert, no clutter.

--------------------------------------------------
3. ANIMATION CONCEPT
--------------------------------------------------

Over the course of the animation (clock 0 → 1):

- 0.0: Floor and background exist, but the logo pieces are below the floor (hidden) and the camera is further back.
- 0.2–0.7: The archway pieces and the golden arrow **rise up from below the floor**, overshoot slightly, then settle into final position.
- 0.3–0.8: A subtle camera move: it arcs slightly around the logo and eases closer.
- 0.4–1.0: A soft teal/gold highlight light tied to the logo intensity “pulses” once, then fades.
- 1.0: All motion almost stopped, logo fully assembled, camera locked in a hero shot.

The animation must be smooth for all intermediate values of `clock`, not just at endpoints.

--------------------------------------------------
4. MANDATORY STRUCTURE (ORDER)
--------------------------------------------------

You MUST structure your code in this exact order:

a) `#include` directives  
b) `global_settings`  
c) `#declare` constants (PI, timings, colors, helper functions via expressions)  
d) camera block (using `clock`)  
e) light sources (key, fill, logo-pulse light)  
f) background and floor plane  
g) textures/materials (teal, gold, floor)  
h) logo geometry:
   - archway elements
   - golden bar + arrow
   - text or text-blocks for “ZAGUÁN” and “AI”
i) optional small details (very minimal, e.g., faint reflection tweaks)

Do NOT deviate from this order.

--------------------------------------------------
5. GLOBAL SETTINGS
--------------------------------------------------

- Use `assumed_gamma 1.0`.
- Use simple radiosity for soft GI-style lighting, similar in STYLE to:

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

You may adjust numbers slightly but keep them reasonable.

--------------------------------------------------
6. CONSTANTS & HELPERS
--------------------------------------------------

In the constants section, you MUST at least define:

- `#declare PI = 3.14159;`
- Timing helpers, for example:

  - `#declare RiseStart = 0.1;`
  - `#declare RiseEnd   = 0.7;`
  - `#declare CamStart  = 0.0;`
  - `#declare CamEnd    = 0.8;`

- A helper to ease motion, using a simple power of `clock` (no macros). For example:

  - Use expressions like `SmoothClock = pow( min( max((clock - RiseStart)/(RiseEnd - RiseStart), 0), 1 ), 2 );`

No macros; just `#declare` values computed from `clock`.

--------------------------------------------------
7. CAMERA (MUST USE `clock`)
--------------------------------------------------

- Perspective camera.
- Use `angle` between 35 and 50.
- Camera motion:

  - Start further away and slightly lower and to the left.
  - End closer, more centered, slightly higher.
  - Use linear interpolation with an eased parameter.

Example style (you must implement your own numbers):

- Start position: `<-6, 3, -14>`
- End position:   `<-2, 4, -8>`

Compute:

- `#declare CamT = min( max((clock - CamStart)/(CamEnd - CamStart), 0), 1 );`
- Optionally ease: `#declare CamT2 = CamT*CamT*(3 - 2*CamT);`  // smoothstep-style

Then:

- `location` = lerp between start and end using `CamT2`.
- `look_at` should always target the logo center, e.g. `<0, 2, 0>`.

No depth-of-field.

--------------------------------------------------
8. LIGHTING
--------------------------------------------------

You MUST define:

1. **Key light**:
   - Slightly above and in front of the logo.
   - Neutral to slightly warm color (e.g., `rgb <1, 0.97, 0.9>`).
   - Not animated in position.

2. **Fill light**:
   - Much weaker.
   - Cooler tone (e.g., `rgb <0.7, 0.85, 1>`).
   - Placed opposite to key to lift shadows.

3. **Logo pulse light**:
   - A light located near the logo center (e.g., `<0, 3, -2>`).
   - Color blended between teal and gold.
   - Intensity varies over time, pulsing once between clock ~0.5 and ~0.9.

   Example style (you must adapt):

   - `#declare PulseT = min( max((clock - 0.5)/0.4, 0), 1 );`
   - `#declare Pulse = sin(PI * PulseT);`  // 0 → 1 → 0
   - Use `Pulse` as a multiplier on this light’s color.

No area lights.

--------------------------------------------------
9. BACKGROUND & FLOOR
--------------------------------------------------

- `background { color rgb <0.96,0.96,0.94> }`
- Floor: plane `y, 0` with a subtle glossy/reflective finish:
  - Slight reflectivity (0.1–0.2).
  - Gentle soft specular.
  - Very subtle noise normal to break perfect mirror look.

The floor must be present for the entire animation and must never disappear.

--------------------------------------------------
10. TEXTURES / MATERIALS
--------------------------------------------------

Define at least:

- `#declare Teal_Texture = texture { ... }`
  - `pigment { color rgb <0.06, 0.34, 0.43> }`
  - Slight specular and roughness.
- `#declare Gold_Texture = texture { ... }`
  - `pigment { color rgb <0.86, 0.69, 0.34> }`
  - Slightly higher specular, subtle reflection.
- `#declare Floor_Texture = texture { ... }`
  - Very light gray.
  - Very low bump for realism.

Use only built-in patterns like `bumps`, `granite`, `bozo`, etc. Keep them subtle.

--------------------------------------------------
11. LOGO GEOMETRY (ARCHWAY + ARROW)
--------------------------------------------------

Approximate the Zaguán archway mark using simple CSG:

- Base concept:
  - A vertical teal “pillar” on the left.
  - A curved teal arch forming the top.
  - A golden horizontal bar with an arrow pointing right, passing through/under the arch.

You MUST:

- Build these from primitives: `box`, `cylinder`, `torus`, `union`, `difference`.
- Use `Teal_Texture` on teal parts, `Gold_Texture` on golden parts.
- Keep the whole logo roughly within x = [-3, 3], y = [0, 4], z = [-1, 1].

Animation of logo pieces:

- Each major piece (left pillar, arch segment(s), gold bar, arrow head) should:
  - Start below the floor at `y < 0`.
  - Rise to final `y` around 1–3 using the eased `SmoothClock`.
  - You may give each piece a slightly different start offset (e.g. start rise a bit earlier or later).
  - Add a tiny overshoot: move a bit above final position then settle using a damped expression.

Example style for a piece’s vertical position (pseudocode only):

- `FinalY = 0.0;`  // base at floor
- `RiseAmount = 3.0;`
- `Y = FinalY + (SmoothClock - 0.1)*RiseAmount;`
- Clamp the motion so it’s 0 below RiseStart and constant after RiseEnd.

You must ensure the pieces are in correct final alignment at `clock = 1`.

--------------------------------------------------
12. TEXT OR TEXT-BLOCKS (“ZAGUÁN AI”)
--------------------------------------------------

Text handling (choose ONE approach):

1. If you are confident, you MAY use the built-in `text` object with a simple font name (e.g. `"timrom"` or another standard font).  
   - Extrude it in z.
   - Apply `Teal_Texture` to “ZAGUÁN” and `Gold_Texture` to “AI”.
   - Place text centered under the logo, resting on the floor.

2. If `text` is too risky, approximate with block letters:
   - For each letter, use boxes/unions scaled to form a simple geometric letter.
   - Colors as above.

Text animation:

- Text can fade/slide in slightly later than the symbol:
  - E.g. start rising after `clock > 0.4`.
  - Less dramatic movement than the archway and arrow.

--------------------------------------------------
13. OPTIONAL SMALL DETAILS
--------------------------------------------------

You may add:

- A very faint halo object (transparent sphere or cylinder around the logo) with `finish { ambient 0 diffuse 0 specular 0 reflection 0 }` and `pigment` with low filter, to fake glow.
- Extremely subtle, low-amplitude oscillation of the logo position or scale after assembly (like a tiny “settling” vibration), but keep it gentle.

Do NOT add clutter or extra scene elements.

--------------------------------------------------
14. NAMING & CLEANLINESS
--------------------------------------------------

- All reusable items must be declared with `#declare` before use.
- No undefined variables.
- Indent cleanly.
- No commented-out dead code.

--------------------------------------------------
15. FINAL CHECKLIST (ALL REQUIRED)
--------------------------------------------------

Your final code MUST have:

- `#include "colors.inc"`
- `global_settings` with `assumed_gamma` and radiosity.
- `#declare PI` and other constants.
- Exactly one `camera` block, using `clock` for smooth motion.
- Key, fill, and logo pulse `light_source` blocks.
- `background` and a floor plane with `Floor_Texture`.
- Teal and gold textures defined and used on the logo geometry.
- 3D archway logo built from CSG (no image_map).
- Golden bar + arrow built from CSG.
- “ZAGUÁN AI” as text or text-blocks.
- All major logo components animated to rise and settle via `clock`.
- No syntax errors, no undefined identifiers.

Now generate the complete POV-Ray 3.7 scene using these rules. Output ONLY the .pov code.
