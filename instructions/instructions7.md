You are generating POV-Ray 3.7 code that is intended for ANIMATION.

The base file already contains:
- `#version 3.7`
- all standard include files (colors, textures, metals, glass, shapes, woods, stones, golds)
- one `global_settings { ... }` block

Do NOT output:
- `#version`
- any `#include`
- any `global_settings`

Your output is appended into the base file and must be directly renderable.

Your ONLY task: output the full POV-Ray scene BODY that:
- Compiles in POV-Ray 3.7 with no manual fixing.
- Uses the built-in variable `clock` (0.0 → 1.0) to animate the scene.
- Constructs a clean, minimalist **3D Zaguán AI logo reveal**.
- Uses only CSG primitives (no meshes, no isosurfaces, no macros).
- Produces a stable, cinematic animation for ANY frame between 0 and 1.

==================================================
1. GENERAL RULES
==================================================

- Output **RAW POV-Ray SDL only** – no Markdown, no comments unless extremely short section headers (e.g. `// Camera`).
- Do NOT use:
  - `isosurface`
  - user-defined `function`
  - `#macro`
  - `media`, volumetrics, photons
  - `mesh` or `mesh2`
  - any custom external files
- All identifiers MUST be declared before use.
- All `{` and `}` MUST match.
- Keep the logo centered at the origin.
- Do NOT add any geometry besides:
  - background
  - floor
  - logo symbol (archway + bar + arrow)
  - “ZAGUÁN AI” text via block letters
- Absolutely no props, characters, scenery, clutter, fog, or environment.

==================================================
2. BRAND & VISUAL STYLE
==================================================

Recreate the Zaguán AI logo using simple 3D geometry:

- A stylized archway in teal.
- A golden horizontal “passage” bar.
- A golden arrow pointing right.
- Under it: “ZAGUÁN AI” built from block letters.

Brand palette:

- Teal:  `rgb <0.06, 0.34, 0.43>`
- Gold:  `rgb <0.86, 0.69, 0.34>`
- Background (studio): `rgb <0.96, 0.96, 0.94>`

Scene design:

- Clean studio aesthetic.
- Simple reflective floor.
- No walls or extra objects.

==================================================
3. ANIMATION BEHAVIOR
==================================================

Over `clock` 0 → 1:

- At 0.0:
  - Background + floor are visible.
  - Logo symbol + letters are *below* the floor (hidden).
  - Camera is farther back and slightly off-center.

- 0.15 → 0.70:
  - The **logo symbol** (arch + bar + arrow) rises upward,
    overshoots slightly, settles cleanly.

- 0.35 → 0.85:
  - The **text** (“ZAGUÁN AI”) rises *later* and with a smaller overshoot.

- 0.30 → 0.80:
  - Camera moves in a smooth arc closer to the logo.

- 0.50 → 0.90:
  - A teal/gold pulse light brightens once and fades.

- At 1.0:
  - Everything is stable, aligned, and motionless.

==================================================
4. REQUIRED STRUCTURE (ORDER)
==================================================

Your output MUST follow this exact order:

a) `#declare` constants (PI, timing parameters, easing values)  
b) Camera block (using `clock`)  
c) Light sources (key light, fill light, pulse light)  
d) Background + floor plane  
e) Textures (Teal_Texture, Gold_Texture, Floor_Texture)  
f) Logo geometry (archway, top bar, arrow)  
g) Block-letter geometry for “ZAGUÁN AI”

Nothing else.

==================================================
5. CONSTANTS & TIMING
==================================================

You MUST define:

- `#declare PI = 3.14159;`

Symbol timing:

- `#declare RiseStart_Symbol = 0.15;`
- `#declare RiseEnd_Symbol   = 0.70;`

Text timing:

- `#declare RiseStart_Text = 0.35;`
- `#declare RiseEnd_Text   = 0.85;`

Camera timing:

- `#declare CamStart = 0.0;`
- `#declare CamEnd   = 0.8;`

Easing example (or equivalent):

- `#declare T_Symbol = min(max((clock - RiseStart_Symbol)/(RiseEnd_Symbol - RiseStart_Symbol),0),1);`
- `#declare T_Text   = min(max((clock - RiseStart_Text  )/(RiseEnd_Text   - RiseStart_Text  ),0),1);`
- `#declare Ease_Symbol = T_Symbol*T_Symbol*(3 - 2*T_Symbol);`
- `#declare Ease_Text   = T_Text*T_Text*(3 - 2*T_Text);`

Camera ease:

- `#declare CamT = min(max((clock - CamStart)/(CamEnd - CamStart),0),1);`
- `#declare Ease_Cam = CamT*CamT*(3 - 2*CamT);`

You may create small overshoots using additive terms (no macros).

==================================================
6. CAMERA (MUST USE EASE_Cam)
==================================================

- Perspective camera.
- Angle between 35 and 50.
- Start position (example): `<-6, 3, -14>`
- End position (example):   `<-2, 4, -8>`
- Interpolate via `Ease_Cam`.

- `look_at` must remain fixed at the logo center `<0, 2, 0>`.

No depth-of-field.

==================================================
7. LIGHTING
==================================================

You MUST define **exactly three** lights:

1. **Key Light**
   - Slightly above + in front of logo.
   - Warm neutral: `rgb <1,0.97,0.9>`

2. **Fill Light**
   - Weaker.
   - Cooler tone: `rgb <0.7,0.85,1>`

3. **Pulse Light**
   - Near logo center.
   - Color is a mix of teal and gold.
   - Uses a pulse variable:

     ```
     #declare PulseT = min(max((clock - 0.5)/0.4,0),1);
     #declare Pulse = sin(PI * PulseT);
     ```

   - Light intensity = base_color * Pulse.

No area lights. No ambient-only hacks.

==================================================
8. BACKGROUND & FLOOR
==================================================

Background:

- `background { color rgb <0.96,0.96,0.94> }`

Floor:

- `plane { y, 0 texture { Floor_Texture } }`
- Reflection MUST be between `0.05` and `0.2`.
- Bump/normal MUST be subtle (`0.05` → `0.15`).

==================================================
9. TEXTURES
==================================================

Define:

### Teal
```
#declare Teal_Texture = texture {
pigment { color rgb <0.06, 0.34, 0.43> }
finish { specular 0.2 roughness 0.02 reflection 0.05 }
}

```

### Gold
```

#declare Gold_Texture = texture {
pigment { color rgb <0.86, 0.69, 0.34> }
finish { specular 0.3 roughness 0.02 reflection 0.08 }
}

```

### Floor
```

#declare Floor_Texture = texture {
pigment { color rgb <0.96,0.96,0.94> }
normal  { bumps 0.05 }
finish  { specular 0.1 reflection 0.1 }
}

```

You may adjust slightly but MUST follow constraints.

==================================================
10. LOGO GEOMETRY (ARCH + BAR + ARROW)
==================================================

You MUST construct the logo symbol from simple CSG:

- Left vertical pillar (teal).
- Top lintel / arch segment (teal).
- Horizontal golden passage bar (box, slim height).
- Arrow head (gold), using cone, box, or combination.

Constraints:

- All elements must fit within:
  - x ∈ [-3, 3]
  - y ∈ [0, 4]
  - z ∈ [-0.5, 0.5]

- All parts MUST have z-depth in the range `0.2`–`0.5`.

- Bars MUST be thinner vertically than the pillar width.

Symbol animation:

- Use `Ease_Symbol` for vertical rise.
- Include a very small overshoot (e.g. rise slightly above final Y, then settle).

==================================================
11. BLOCK LETTER TEXT (“ZAGUÁN AI”)
==================================================

You MUST construct letters using boxes/unions (NO text{} object).

- Build “ZAGUÁN” in teal using Teal_Texture.
- Build “AI” in gold using Gold_Texture.
- Letters must be:
  - Centered horizontally
  - Resting at floor level
  - Immediately below the logo symbol
  - Proportional and readable

Text animation:

- Must use `Ease_Text` (later rise, smaller overshoot).
- Stable by `clock = 1.0`.

==================================================
12. FINAL REQUIREMENTS
==================================================

Your output MUST contain:

- `#declare` PI and all timing/easing variables.
- Exactly one camera block.
- Three lights (key, fill, pulse).
- One background block.
- One floor plane.
- Teal_Texture, Gold_Texture, Floor_Texture.
- Full logo symbol geometry.
- Full ZAGUÁN AI text via block letters.
- Proper animation for symbol & text.
- NO undefined identifiers.
- NO macros.
- NO includes.
- NO global_settings.
- NO additional geometry.

Output ONLY the POV-Ray scene code body.

