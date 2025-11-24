You are generating POV-Ray 3.7 code intended for ANIMATION.

Your ONLY task: output a single, complete, ready-to-render .pov scene that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Produces a “modern neural-tech AI background” in motion.
- Reveals the 3D Zaguán AI logo in front of this background.
- Animates everything using the built-in variable `clock` (range 0–1).
- Uses ONLY allowed primitives and safe constructs.
- Looks cinematic, high-tech, and professional for ANY frame from 0 to 1.

------------------------------------------------------------
1. GENERAL RULES
------------------------------------------------------------

- Output ONLY POV-Ray SDL code.
- No comments, no Markdown, no explanations.
- Allowed includes: "colors.inc" and "textures.inc" only.
- Forbidden:
  - macros
  - isosurfaces
  - user-defined functions
  - media, scattering, volumetrics
  - version > 3.7
  - mesh or mesh2
- All identifiers must be declared before use.
- All braces must be matched.
- The scene must render even if the user modifies camera settings.

------------------------------------------------------------
2. OVERALL SCENE CONCEPT
------------------------------------------------------------

You are creating a **high-tech AI-core background** defined entirely with:
- animated pigments
- planes
- thin boxes
- cylinders
- grids
- glowing lines

The style is:
- dark base (black / deep charcoal)
- neon greens and cyans
- animated scanning streaks
- data streams sliding horizontally or vertically
- thin, glowing digital “rails” or “pipelines”
- a subtle animated grid pattern

Think of:
- neural pathways
- LLM activation maps
- circuitry
- software visualization
- modern cyber aesthetics

In front of this background, the **Zaguán AI 3D logo** appears:
- Teal + Gold colors
- Clean geometry
- Rising from below the floor
- Cinematic lighting
- Smooth easing motion

Camera must do a slow, subtle forward drift.

------------------------------------------------------------
3. MANDATORY STRUCTURE (ORDER)
------------------------------------------------------------

a) #include directives  
b) global_settings  
c) #declare constants (PI, timings, colors, easing parameters)  
d) camera block  
e) light sources  
f) BACKGROUND LAYER: high-tech animated AI backdrop  
g) FLOOR PLANE  
h) TEXTURES (Teal, Gold, Neon Green, Floor)  
i) ZAGUÁN LOGO GEOMETRY  
j) LOGO ANIMATION (rising + settle)  
k) Optional subtle glow shells  

Do NOT deviate from this order.

------------------------------------------------------------
4. GLOBAL SETTINGS
------------------------------------------------------------

- assumed_gamma 1.0
- radiosity block similar to:

  radiosity {
    pretrace_start 0.08
    pretrace_end   0.01
    count 150
    nearest_count 5
    recursion_limit 1
    low_error_factor 0.5
  }

This creates soft indirect lighting without heavy render cost.

------------------------------------------------------------
5. CONSTANTS & TIMING
------------------------------------------------------------

You MUST declare:

#declare PI = 3.14159;

// Arch (logo symbol) drop timing: from top → center, then STOP.
#declare ArchDropStart = 0.00;
#declare ArchDropEnd   = 0.40;

// Text timing: starts ONLY after the arch is centered.
#declare TextRiseStart = 0.45;
#declare TextRiseEnd   = 0.90;

// Camera timing
#declare CamStart = 0.00;
#declare CamEnd   = 1.00;

// Normalized [0,1] helpers (clamped)
#declare T_Arch = min(max((clock - ArchDropStart)/(ArchDropEnd - ArchDropStart), 0), 1);
#declare T_Text = min(max((clock - TextRiseStart)/(TextRiseEnd - TextRiseStart), 0), 1);
#declare T_Cam  = min(max((clock - CamStart     )/(CamEnd       - CamStart     ), 0), 1);

// Smoothstep easing
#declare Ease_Arch = T_Arch*T_Arch*(3 - 2*T_Arch);
#declare Ease_Text = T_Text*T_Text*(3 - 2*T_Text);
#declare Ease_Cam  = T_Cam *T_Cam *(3 - 2*T_Cam);

// IMPORTANT:
// After ArchDropEnd, the arch MUST remain completely static.
// Do NOT add any overshoot or extra vertical motion after T_Arch reaches 1.0.

------------------------------------------------------------
6. CAMERA
------------------------------------------------------------

- camera { perspective }
- angle 38–45
- Start location example: <0, 2, -14>
- End   location example: <0, 3, -9>

Interpolate with Ease_Cam:
location = lerp(StartCam, EndCam, Ease_Cam);

look_at MUST stay fixed at the logo center, e.g. <0, 1.5, 0>.
No depth-of-field.

------------------------------------------------------------
7. LIGHT SOURCES
------------------------------------------------------------

You MUST define:

1. Key light — subtle warm tone.
2. Fill light — cooler, weaker.
3. Neon backlight — green or cyan, positioned behind the logo to interact with the neural-tech backdrop.
4. Optional flicker/pulse tied to `sin(clock * PI)` multiplied with a neon color.

No area lights.

------------------------------------------------------------
8. HIGH-TECH AI BACKGROUND LAYER (CRITICAL)
------------------------------------------------------------

This MUST be included and MUST animate.

Build it using only:
- planes
- thin box arrays
- animated pigments (bozo, wood, marble, agate)
- color_map gradients
- subtle turbulence

You MUST create:

1. **A large vertical backdrop plane** behind the logo (`z = 2` or similar).
   The pigment MUST animate using `clock`:
   - sliding noise
   - shifting green/cyan lines
   - pulse waves
   - gradient bands moving left/right or top/bottom.

   Example style (you must implement your own numbers):
```

pigment {
bozo
color_map {
[0.0  color rgb <0, 0.05, 0.02>]
[0.3  color rgb <0, 0.3, 0.1>]
[0.6  color rgb <0.2, 1, 0.3>]
[1.0  color rgb <0, 0.2, 0.1>]
}
scale <1, 1, 1>
turbulence 0.3
translate <clock*2, clock*0.5, 0>   // animated
}
finish { emission 0.2 }

```

2. **Digital rails**: horizontal or vertical glowing lines built from long thin boxes:
- colored neon green or cyan
- some move with `clock`
- some fade in/out with sin-based modulation.

3. **A dynamic grid overlay**:
- thin box or cylinder arrays forming a grid
- slightly emissive
- subtle flicker

All background must stay behind the logo.

------------------------------------------------------------
9. FLOOR PLANE
------------------------------------------------------------

- plane { y, 0 }
- Slight reflection (0.05–0.15)
- Very dark, neutral material so it doesn’t overpower the neon background.

------------------------------------------------------------
10. TEXTURES
------------------------------------------------------------

Define:

- Teal_Texture (rgb <0.06,0.34,0.43>)
- Gold_Texture (rgb <0.86,0.69,0.34>)
- Neon_Texture (rgb <0.2,1,0.4>) with emission for glowing rails
- Floor_Texture

------------------------------------------------------------
11. ZAGUÁN LOGO GEOMETRY (ARCH + BAR + ARROW)
------------------------------------------------------------

You MUST construct:

1. Teal arch symbol:
   - Vertical pillar (box).
   - Top lintel (box) or simple arch made from boxes/torus section.
   - Place the **arch symbol at z = 0** (the “logo plane”).

2. Golden passage bar + arrow head:
   - Bar = thin box that passes through the arch.
   - Arrow head = box/cone/CSG wedge.
   - Also at **z = 0**.

3. Text "ZAGUÁN AI":
   - Use POV-Ray text:
     text {
       ttf "timrom.ttf" "ZAGUÁN AI" 0.2, 0
       ...
     }
   - Apply teal to “ZAGUÁN” and gold to “AI” (you may split into two text objects).
   - **Text MUST be in front of the arch in z**, e.g. translate it to z = -0.6.
   - From the camera’s point of view, the text must clearly sit in front of the arch, never behind it.

Positional constraints:

- Arch symbol center roughly at <0, 1.5, 0>.
- Text baseline at y ≈ 0.4 and z ≈ -0.6.
- Background neural grid plane must be behind the arch (z > 1).

------------------------------------------------------------
12. ANIMATION OF ARCH & TEXT
------------------------------------------------------------

ARCH (logo symbol):

- At clock = 0:
  - The arch symbol starts **above** the visible area (e.g. center at y ≈ 6).
- During ArchDropStart → ArchDropEnd:
  - The arch moves straight down along the y-axis into its final centered position,
    using Ease_Arch for smooth motion.
- At clock ≥ ArchDropEnd:
  - The arch **stops completely** at its final y position (e.g. y ≈ 1.5).
  - No bounce, no overshoot, no further vertical motion.

Implement this by computing:

- A start Y (Arch_Y_Start, high value)
- A final Y (Arch_Y_Final, centered)
- An interpolated Y:
    Arch_Y = Arch_Y_Start + (Arch_Y_Final - Arch_Y_Start) * Ease_Arch;
- And applying this translation ONLY to the arch and arrow objects.

TEXT ("ZAGUÁN AI"):

- At clock < TextRiseStart:
  - Text should be invisible below the floor (e.g. y < -2) or exactly at y < 0.
- From TextRiseStart → TextRiseEnd:
  - Text rises smoothly with Ease_Text from below the floor up to its final baseline (y ≈ 0.4).
- At clock ≥ TextRiseEnd:
  - Text remains perfectly static.

Text animation must never move the arch; they are independent.

Z-ORDER RELATION:

- Background plane: z > 1 (furthest away).
- Arch symbol + bar + arrow: z = 0.
- Text ("ZAGUÁN AI"): z = -0.6 (closest to camera).

At the final frame (clock = 1.0):

- The arch is perfectly centered and static.
- The text is fully visible, directly in front of the arch.
- Camera is in its final eased position.
- No elements are still moving.

------------------------------------------------------------
13. OPTIONAL GLOW SHELL
------------------------------------------------------------

You MAY add a faint transparent sphere around the logo with:
- ambient 0
- diffuse 0
- low filter pigment
- tiny emission
- size ~20–30 units

------------------------------------------------------------
14. FINAL CHECKLIST (ALL REQUIRED)
------------------------------------------------------------

Your final scene MUST include:
- includes
- global_settings
- constants (#declare)
- camera
- lights
- animated neural-tech background plane
- glowing rails
- subtle grid
- floor plane
- neon + teal + gold textures
- Zaguán logo geometry
- correct animation from clock
- no syntax errors
- no undefined identifiers

Now generate the complete POV-Ray 3.7 SDL scene using these rules. 
Output ONLY the POV-Ray code.
