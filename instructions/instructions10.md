You are generating POV-Ray 3.7 code intended for ANIMATION.

Your ONLY task: output a single, complete, ready-to-render .pov scene that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Produces a high-tech “neural AI processing” background.
- Animates a teal arch dropping from above.
- Animates the text “ZAGUÁN AI” rising from below.
- Arch and text meet at the same time and then remain perfectly still.
- Uses `clock` in the range 0–1 to drive animation.
- Uses only safe primitives and allowed constructs.
- Shows off the final logo and arch clearly with extra hold time at the end.

------------------------------------------------------------
1. GENERAL RULES
------------------------------------------------------------

- Output ONLY raw POV-Ray SDL code (no comments, no Markdown, no explanations).
- Allowed includes: "colors.inc", "textures.inc".
- Forbidden:
  - macros
  - isosurfaces
  - user-defined functions
  - media/volumetrics
  - mesh or mesh2
  - #version higher than 3.7
- All identifiers must be declared before use.
- All braces must match.
- Do NOT use negative scaling on any object (no mirroring).

------------------------------------------------------------
2. OVERALL SCENE CONCEPT
------------------------------------------------------------

You will create a modern, neural-tech AI background:

- dark teal / black base
- glowing green/cyan animated bands
- vertical neon rails
- subtle grid structure
- pigments animated over time to evoke “data flow” and “LLM activity”

In front of this background:

- A teal Zaguán arch drops from above.
- The text “ZAGUÁN AI” rises from below:
  - “ZAGUÁN” is pure white.
  - “AI” is gold.
- Arch and text move simultaneously and meet at their final positions at exactly the same time.
- After they meet, they remain completely still while the camera finishes a slow zoom-out and then holds the final hero shot.

The text must always sit slightly in front of the arch in z so it never intersects or hides behind it.

------------------------------------------------------------
3. MANDATORY STRUCTURE (ORDER)
------------------------------------------------------------

Your code MUST follow this order:

a) #include directives  
b) global_settings  
c) #declare constants (PI, timings, easing)  
d) camera block  
e) light sources  
f) BACKGROUND (neural-tech plane, rails, grid)  
g) FLOOR plane  
h) TEXTURES (Teal, Gold, White, Neon, Floor)  
i) LOGO GEOMETRY (arch, bar/arrow, text)  
j) ANIMATION transforms (arch drop + text rise)  
k) optional glow shell

------------------------------------------------------------
4. GLOBAL SETTINGS
------------------------------------------------------------

You MUST include:

global_settings {
  assumed_gamma 1.0
  radiosity {
    pretrace_start 0.08
    pretrace_end   0.01
    count 150
    nearest_count 5
    recursion_limit 1
    low_error_factor 0.5
  }
}

------------------------------------------------------------
5. CONSTANTS & TIMING
------------------------------------------------------------

You MUST declare:

#declare PI = 3.14159;

// Arch & text motion: both start early and finish by 0.40
#declare MotionStart = 0.05;
#declare MotionEnd   = 0.40;

// Camera motion: finishes earlier than end so we have a static hold
#declare CamStart = 0.10;
#declare CamEnd   = 0.80;

// Normalized [0,1] motion parameter (clamped)
#declare T_Motion = min(max((clock - MotionStart)/(MotionEnd - MotionStart), 0), 1);
// Smoothstep easing
#declare Ease_Motion = T_Motion*T_Motion*(3 - 2*T_Motion);

// Camera easing
#declare T_Cam  = min(max((clock - CamStart)/(CamEnd - CamStart), 0), 1);
#declare Ease_Cam = T_Cam*T_Cam*(3 - 2*T_Cam);

// For all clock >= MotionEnd, Ease_Motion MUST be treated as 1.0,
// so arch and text are perfectly still from clock = 0.40 to 1.0.
// For all clock >= CamEnd, Ease_Cam MUST be 1.0 so the camera is static
// from clock = 0.80 to 1.0.

------------------------------------------------------------
6. CAMERA (ZOOM-OUT WITH FINAL HOLD)
------------------------------------------------------------

The camera MUST perform a gentle zoom-out (move farther away),
never zooming in closer than the starting position, and must
guarantee the entire arch is visible at all times.

camera {
  perspective
  angle 40

  // Starts closer, ends farther back and slightly higher
  location <
    0,
    2 + 0.5*Ease_Cam,    // small upward drift
    -10 - 4*Ease_Cam     // pulls back from -10 to -14
  >

  look_at <0, 1.5, 0>
}

From clock >= CamEnd (0.80), the camera location MUST remain constant,
so the last 20% of the animation is a static hero shot.

------------------------------------------------------------
7. LIGHT SOURCES
------------------------------------------------------------

You MUST create:

1. Key light:
   - Slightly above and in front of the logo.
   - Warm neutral color (e.g., rgb <1, 0.97, 0.9>).

2. Fill light:
   - Weaker.
   - Cooler tone (e.g., rgb <0.7, 0.85, 1>).
   - Opposite side of key.

3. Neon backlight:
   - Behind the arch, slightly above it.
   - Cyan/green tone to interact with the background.

You MAY add a gentle time-based brightness modulation to the neon light
using a sin() of clock, but it must not distract from the logo.

No area lights.

------------------------------------------------------------
8. HIGH-TECH AI BACKGROUND
------------------------------------------------------------

You MUST include:

- One large vertical plane behind the logo (e.g., at z = 4).
- A pigment on this plane that:
  - uses bozo/marble/wood patterns
  - uses a color_map of dark teal → bright green/cyan
  - is animated with clock (e.g., translate or phase based on clock)
  - suggests horizontal and/or vertical “data bands” moving over time.

- Several thin neon rails:
  - boxes or cylinders in front of the background plane but behind the logo.
  - use Neon_Texture (see below).
  - some may extend from floor upward.
  - spacing across x-axis.

- Optional thin grid lines:
  - more boxes or cylinders forming a subtle grid.

All background elements must remain behind the arch in z (z > 1.0).

------------------------------------------------------------
9. FLOOR PLANE
------------------------------------------------------------

Create a plane { y, 0 } textured as a dark glossy surface:

- reflection roughly between 0.05 and 0.15
- subtle bump/normal to avoid a perfect mirror
- dark enough that the logo and background dominate the frame

------------------------------------------------------------
10. TEXTURES (MANDATORY)
------------------------------------------------------------

You MUST define at least:

1. Teal_Texture:

   pigment { color rgb <0.06, 0.34, 0.43> }
   finish  { specular 0.2 roughness 0.02 reflection 0.05 }

2. Gold_Texture:

   pigment { color rgb <0.86, 0.69, 0.34> }
   finish  { specular 0.3 roughness 0.02 reflection 0.08 }

3. White_Text_Texture:

   pigment { color rgb <1, 1, 1> }
   finish  { specular 0.25 roughness 0.02 reflection 0.03 }

4. Neon_Texture:

   pigment { color rgb <0.2, 1.0, 0.6> }
   finish  { emission 0.25 diffuse 0.1 specular 0.1 }

5. Floor_Texture:

   dark teal/gray with small bumps and moderate reflection.

------------------------------------------------------------
11. LOGO GEOMETRY (ARCH + BAR/ARROW + TEXT)
------------------------------------------------------------

ARCH SYMBOL:

- Build from simple primitives:
  - vertical pillar: box
  - top beam: box (or curved piece using torus if stable)
- Use Teal_Texture.
- Center the arch around x=0, z=0.
- Final arch center in y should be around 1.5.

GOLD BAR AND ARROW:

- Passage bar:
  - box passing through the arch horizontally.
- Arrow:
  - wedge from box/CSG or cone-like shape at the right end.
- Use Gold_Texture.
- Also at z = 0.

TEXT:

- Use POV-Ray text objects with the built-in font "timrom.ttf".
- Split into two text objects to color them separately:
  - "ZAGUÁN" (white)
  - "AI" (gold)
- Apply White_Text_Texture to "ZAGUÁN", Gold_Texture to "AI".
- Place the text so that:
  - it is horizontally centered under or in front of the arch,
  - final baseline y ≈ 0.4,
  - z ≈ -0.6 so it clearly sits in front of the arch.

Z-ORDER RELATION:

- Background plane and rails: z > 1.0
- Arch + bar + arrow: z = 0
- Text (“ZAGUÁN AI”): z = -0.6

------------------------------------------------------------
12. SYNCHRONIZED ANIMATION (ARCH DROP + TEXT RISE)
------------------------------------------------------------

You MUST use the shared Ease_Motion for both arch and text.

ARCH:

- Define:
  - Arch_Y_Start = a high value (e.g., 5.0) above the visible area.
  - Arch_Y_Final = 1.5 (final centered height).
- Compute:
  Arch_Y = Arch_Y_Start + (Arch_Y_Final - Arch_Y_Start) * Ease_Motion;
- Translate the entire arch (including bar/arrow) by <0, Arch_Y, 0>.
- For clock <= MotionStart, the arch must be at or above Arch_Y_Start.
- For clock >= MotionEnd, the arch must be exactly at Arch_Y_Final and must not move any more.

TEXT (“ZAGUÁN” and “AI”):

- Define:
  - Text_Y_Start = a low value below the floor (e.g., -3.0).
  - Text_Y_Final = 0.4 (final baseline).
- Compute:
  Text_Y = Text_Y_Start + (Text_Y_Final - Text_Y_Start) * Ease_Motion;
- Translate both “ZAGUÁN” and “AI” text objects by <offset_x, Text_Y, -0.6>.
- For clock <= MotionStart, text must be below the floor.
- For clock >= MotionEnd, text must be exactly at Text_Y_Final and must not move any more.

The arch and text must reach their final positions at exactly the same moment (when Ease_Motion = 1.0), and remain perfectly still from clock = MotionEnd (0.40) to clock = 1.0.

------------------------------------------------------------
13. OPTIONAL GLOW
------------------------------------------------------------

You MAY add a faint transparent glow shell (e.g., sphere) around the logo using:

- no diffuse,
- low emission,
- subtle filter.

------------------------------------------------------------
14. FINAL CHECKLIST
------------------------------------------------------------

Your final code MUST include:

- #include "colors.inc"
- #include "textures.inc"
- global_settings with assumed_gamma and radiosity
- timing and easing constants
- a camera that zooms OUT (farther from the logo) and is completely static from clock >= 0.80
- key, fill, and neon lights
- animated neural-tech background plane and rails
- floor plane with reflections
- Teal_Texture, Gold_Texture, White_Text_Texture, Neon_Texture, Floor_Texture
- teal arch symbol + golden bar/arrow centered at z=0
- “ZAGUÁN” in white and “AI” in gold, in front of the arch at z=-0.6
- synchronized arch drop and text rise using Ease_Motion, both static from clock >= 0.40
- no syntax errors and no undefined identifiers

Now generate the complete POV-Ray 3.7 SDL scene using these rules. Output ONLY the POV-Ray code.
