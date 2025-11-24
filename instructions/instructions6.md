iYou are generating POV-Ray 3.7 code that is intended for ANIMATION.

The base file already contains:
- `#version 3.7`
- standard POV-Ray includes (colors, textures, metals, glass, shapes, woods, stones, golds)
- a `global_settings { ... }` block

Your output will be appended **after** that template.

Your ONLY task: output a single, complete, ready-to-render POV-Ray scene **body** that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Uses the built-in variable `clock` (range 0.0 to 1.0) to animate the scene.
- Recreates a simplified 3D version of the **Zaguán AI** archway logo in brand colors.
- Produces a clean, cinematic logo reveal that looks good for ANY frame 0.0 ≤ clock ≤ 1.0.

You MUST follow these rules exactly.

--------------------------------------------------
1. GENERAL RULES
--------------------------------------------------

- Output ONLY POV-Ray code. No explanations, no Markdown.
- Do NOT output `#version`, `#include`, or `global_settings`. They already exist.
- Do NOT use:
  - `isosurface`
  - user-defined `function`
  - `#macro`
  - `#version` higher than 3.7
  - complex `media` volumes
- All identifiers must be defined before use.
- Every `{` must have a matching `}`.
- Keep the logo centered around the origin (0,0,0).

--------------------------------------------------
2. BRAND & LOOK
--------------------------------------------------

Approximate the Zaguán AI archway logo as 3D geometry:

- A stylized archway made of teal-colored elements.
- A horizontal golden “passage” bar with an arrow head pointing to the right.
- The word “ZAGUÁN” in teal and “AI” in gold, using either 3D text or extruded block letters.

If `text` is unreliable, approximate letters with simple rectangular extruded blocks in the correct colors, laid out in a line.

Color palette (approximate):

- Teal (primary):  `rgb <0.06, 0.34, 0.43>`
- Gold (accent):   `rgb <0.86, 0.69, 0.34>`
- Background:      very light warm gray: `rgb <0.96, 0.96, 0.94>`

The logo sits on a simple floor plane with soft reflections, in a clean “studio” environment – no extra props, no clutter.

--------------------------------------------------
3. ANIMATION CONCEPT
--------------------------------------------------

Over the course of the animation (clock 0 → 1):

- At 0.0: Floor and background exist. Logo symbol and text are hidden below the floor (y < 0). Camera is further back.
- From ~0.15 to ~0.7: The archway pieces and golden arrow rise from below the floor, overshoot slightly, then settle into final position.
- From ~0.35 to ~0.85: The text (“ZAGUÁN AI”) rises later and with a smaller overshoot, then settles.
- From ~0.3 to ~0.8: The camera moves in a subtle arc around the logo and eases closer.
- From ~0.5 to ~0.9: A teal/gold highlight light tied to the logo intensity pulses once, then fades.
- At 1.0: All motion is nearly stopped, logo fully assembled, camera in a stable hero shot.

The animation must be smooth for all values 0.0 ≤ clock ≤ 1.0.

--------------------------------------------------
4. STRUCTURE (ORDER WITHIN YOUR OUTPUT)
--------------------------------------------------

Within the code you generate (after the template), use this order:

a) `#declare` constants (PI, timings, colors, helper values based on `clock`)  
b) camera block (using `clock`)  
c) light sources (key, fill, logo-pulse light)  
d) background and floor plane  
e) textures / materials (teal, gold, floor)  
f) logo symbol geometry:
   - archway elements
   - golden bar + arrow
g) text or text-block geometry for “ZAGUÁN” and “AI”

Do NOT emit additional `global_settings` or `#include`.

--------------------------------------------------
5. CONSTANTS & HELPERS
--------------------------------------------------

In the constants section, you MUST define at least:

- `#declare PI = 3.14159;`

Timing helpers (you can adjust numeric values but must keep the structure):

- `#declare RiseStart_Symbol = 0.15;`
- `#declare RiseEnd_Symbol   = 0.70;`
- `#declare RiseStart_Text   = 0.35;`
- `#declare RiseEnd_Text     = 0.85;`
- `#declare CamStart         = 0.0;`
- `#declare CamEnd           = 0.8;`

Use simple easing expressions, no macros. For example:

- `#declare T_Symbol = min( max((clock - RiseStart_Symbol)/(RiseEnd_Symbol - RiseStart_Symbol), 0), 1 );`
- `#declare T_Text   = min( max((clock - RiseStart_Text  )/(RiseEnd_Text   - RiseStart_Text  ), 0), 1 );`

You MUST use **separate** eased parameters for symbol and text. Do not animate them with the exact same time function.

--------------------------------------------------
6. CAMERA (MUST USE `clock`)
--------------------------------------------------

- Perspective camera.
- Use `angle` between 35 and 50.
- Camera motion:
  - Start further away and slightly lower and to the left.
  - End closer, more centered, slightly higher.
- Use a smoothstep-style easing on a 0–1 parameter for interpolation.

Example scheme (choose your own numbers but keep the logic):

- Start position: `<-6, 3, -14>`
- End position:   `<-2, 4, -8>`

Compute:

- `#declare CamT = min( max((clock - CamStart)/(CamEnd - CamStart), 0), 1 );`
- `#declare CamT2 = CamT*CamT*(3 - 2*CamT);`

Then interpolate `location` between start and end using `CamT2`.  
`look_at` should target the logo center, e.g. `<0, 2, 0>`.  
Do not use depth-of-field.

--------------------------------------------------
7. LIGHTING
--------------------------------------------------

You MUST define:

1. **Key light**:
   - Slightly above and in front of the logo.
   - Neutral to slightly warm (e.g., `rgb <1, 0.97, 0.9>`).
   - Static position.

2. **Fill light**:
   - Much weaker than the key.
   - Slightly cooler tone (e.g., `rgb <0.7, 0.85, 1>`).
   - Placed opposite the key to lift shadows.

3. **Logo pulse light**:
   - Positioned near the logo (e.g., `<0, 3, -2>` or close to the arch center).
   - Color blended between teal and gold.
   - Intensity varies over time, pulsing once.

Example pattern (you must implement some variant):

- `#declare PulseT = min( max((clock - 0.5)/0.4, 0), 1 );`
- `#declare Pulse  = sin(PI * PulseT);`  // 0 → 1 → 0

Use `Pulse` to scale this light’s color.  
Do not use area lights.

--------------------------------------------------
8. BACKGROUND & FLOOR
--------------------------------------------------

- `background { color rgb <0.96, 0.96, 0.94> }`

Floor:

- A plane `y, 0` using `Floor_Texture`.
- Slight reflectivity (around 0.1–0.2).
- Gentle specular.
- Very subtle bump or normal to avoid a perfect mirror.

The floor must exist for the entire animation.

--------------------------------------------------
9. TEXTURES / MATERIALS
--------------------------------------------------

Define at least:

- `#declare Teal_Texture = texture { ... }`
  - `pigment { color rgb <0.06, 0.34, 0.43> }`
  - Slight specular and roughness.

- `#declare Gold_Texture = texture { ... }`
  - `pigment { color rgb <0.86, 0.69, 0.34> }`
  - Slightly higher specular and subtle reflection.

- `#declare Floor_Texture = texture { ... }`
  - Very light gray.
  - Very low bump or noise for realism.

Use only built-in patterns like `bumps`, `granite`, `bozo`, etc., and keep them subtle.

--------------------------------------------------
10. LOGO GEOMETRY (ARCHWAY + ARROW)
--------------------------------------------------

Approximate the Zaguán archway mark using simple CSG:

Base layout:

- A vertical teal pillar on the left.
- A teal arch or lintel spanning the top.
- A golden horizontal bar with an arrow pointing right, passing through or under the arch.

You MUST:

- Build from primitives: `box`, `cylinder`, `torus`, `union`, `difference`.
- Use **boxes for the horizontal bars** (top bar, arrow shaft) so they appear slim and graphic.
- Keep all logo elements relatively thin in z (around 0.3–0.5 units) so the mark doesn’t look overly chunky.
- Use `Teal_Texture` on teal parts and `Gold_Texture` on gold parts.
- Keep the logo within roughly x ∈ [-3, 3], y ∈ [0, 4], z ∈ [-1, 1].

Animation of symbol pieces:

- Each major piece (pillar, arch/lintel, gold bar, arrow head):
  - Starts below the floor (y < 0) at clock = 0.
  - Uses the symbol easing parameter (`T_Symbol`) to rise, overshoot slightly, and then settle.
- The overshoot should be small but visible; position should be stable by clock = 1.0.

--------------------------------------------------
11. TEXT OR TEXT-BLOCKS (“ZAGUÁN AI”)
--------------------------------------------------

Text handling (pick ONE approach):

1. **Text object**:
   - Use a simple core font name such as `"timrom"` without a file path.
   - Extrude in z.
   - Apply `Teal_Texture` to “ZAGUÁN” and `Gold_Texture` to “AI”.
   - Place centered under the logo, resting on the floor.

2. **Block letters**:
   - For each letter, use boxes/unions to create a simple geometric approximation.
   - Apply teal to “ZAGUÁN” and gold to “AI”.

Text animation:

- Text must use its **own** easing parameter (`T_Text`), starting later than the logo symbol.
- Less overshoot than the symbol.
- Position must be stable by clock = 1.0.

--------------------------------------------------
12. CLEANLINESS
--------------------------------------------------

- All reusable items must be declared with `#declare` before use.
- No undefined variables.
- No duplicate camera blocks.
- No commented-out dead code.
- No additional `#include` or `global_settings`.

--------------------------------------------------
13. FINAL CHECKLIST
--------------------------------------------------

Your output must contain:

- `#declare PI` and timing constants.
- Exactly one `camera` block using `clock`.
- A key light, a fill light, and one pulse light.
- A `background` and floor plane using `Floor_Texture`.
- Defined `Teal_Texture`, `Gold_Texture`, and `Floor_Texture`.
- 3D archway symbol (pillar + top bar/arch + arrow) built from CSG, using teal and gold.
- “ZAGUÁN AI” as text or block letters in teal and gold.
- Separate animated motion for:
  - symbol (earlier, stronger overshoot)  
  - text (later, weaker overshoot)
- No syntax errors, no undefined identifiers, no extra includes or globals.

Output ONLY the POV-Ray scene code body.
