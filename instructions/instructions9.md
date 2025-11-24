You are generating POV-Ray 3.7 code intended for ANIMATION.

Your ONLY task: output a single, complete, ready-to-render .pov scene that:
- Compiles in POV-Ray 3.7 without manual fixes.
- Produces a high-tech “neural AI processing background”.
- Animates an arch (teal) dropping from above.
- Animates the text “ZAGUÁN AI” rising from below.
- Both arch and text arrive at their final positions at the SAME time.
- Uses the built-in variable `clock` (range 0–1).
- Looks cinematic for ANY frame 0–1.
- Uses only safe primitives and allowed constructs.

------------------------------------------------------------
1. GENERAL RULES
------------------------------------------------------------

- Output ONLY raw POV-Ray SDL code (no comments, no Markdown, no explanations).
- Allowed includes: "colors.inc", "textures.inc".
- Forbidden:
  macros, isosurfaces, user functions, media/volumetrics,
  mesh/mesh2, version > 3.7, photons.
- All identifiers must be declared before use.
- All braces must match.
- All geometry must be positioned explicitly.
- No negative scaling (to avoid mirrored elements).

------------------------------------------------------------
2. OVERALL SCENE CONCEPT
------------------------------------------------------------

You will create a **modern neural-tech AI background**:

- deep black/teal base colors
- glowing green/cyan data streaks
- animated scanning noise
- vertical neon rails
- a faint animated grid
- everything in constant subtle motion using animated pigments

In front of this:

- The **teal Zaguán arch** drops from above.
- The **text “ZAGUÁN” (white)** rises from below.
- The **text “AI” (gold)** rises with it.
- They meet at the same moment and stop dead.
- Text sits IN FRONT of the arch (z = -0.6, arch at z = 0).
- Camera eases forward slightly.

------------------------------------------------------------
3. MANDATORY STRUCTURE (ORDER)
------------------------------------------------------------

a) #include directives  
b) global_settings  
c) #declare constants (PI, timings, easing)  
d) camera block  
e) light sources  
f) BACKGROUND (neural-tech plane + neon rails + animated pigment)  
g) FLOOR  
h) TEXTURES (Teal, Gold, White, Neon, Floor)  
i) LOGO GEOMETRY (arch + bar + arrow + text)  
j) ANIMATION TRANSFORMS (arch drop + text rise)  
k) Optional glow shell

Do NOT deviate.

------------------------------------------------------------
4. GLOBAL SETTINGS
------------------------------------------------------------

global_settings must include:

assumed_gamma 1.0
radiosity {
    pretrace_start 0.08
    pretrace_end   0.01
    count 150
    nearest_count 5
    recursion_limit 1
    low_error_factor 0.5
}

------------------------------------------------------------
5. CONSTANTS & TIMING
------------------------------------------------------------

You MUST declare:

#declare PI = 3.14159;

// Shared movement timing for BOTH arch and text
#declare MotionStart = 0.05;
#declare MotionEnd   = 0.55;

// Camera timing (end to 1.0)
#declare CamStart = 0.10;
#declare CamEnd   = 1.00;

// Normalized clamped motion parameter
#declare T_Motion = min(max((clock - MotionStart)/(MotionEnd - MotionStart), 0), 1);
#declare Ease_Motion = T_Motion*T_Motion*(3 - 2*T_Motion);

// Camera easing
#declare T_Cam = min(max((clock - CamStart)/(CamEnd - CamStart),0),1);
#declare Ease_Cam = T_Cam*T_Cam*(3 - 2*T_Cam);

------------------------------------------------------------
6. CAMERA (ZOOM-OUT)
------------------------------------------------------------

The camera must NOT move closer to the logo.  
Instead, it must perform a subtle, smooth **zoom-out** or backward drift, ensuring the entire arch stays fully visible for the entire animation.

camera {
    perspective
    angle 40

    // Start closer, end slightly farther back
    // to guarantee full visibility of the arch.
    location <
        0,
        2 + 0.5*Ease_Cam,     // small upward drift
        -10 - 4*Ease_Cam      // pulls BACK from -10 to -14
    >

    look_at <0, 1.5, 0>
}

------------------------------------------------------------
7. LIGHT SOURCES
------------------------------------------------------------

You MUST create:

1. Key light (slightly warm)
2. Fill light (cooler)
3. Neon backlight (cyan/green) behind the arch
4. Optional flicker using sin(clock*PI*2)

No area lights.

------------------------------------------------------------
8. HIGH-TECH AI BACKGROUND
------------------------------------------------------------

You MUST include:

- A vertical plane behind the logo (e.g. z = 4)
- Animated bozo/marble pigment in green/cyan
- translate with clock for scanning motion
- turbulence or phase-based warping
- Several thin neon rails using boxes or cylinders:
  - color = neon cyan/green
  - slight emission
  - spaced across x-axis
- A subtle grid of thin boxes
- Background MUST stay behind the arch and text.

------------------------------------------------------------
9. FLOOR
------------------------------------------------------------

plane { y, 0 }
with a dark glossy floor texture:
- reflection 0.05–0.15
- subtle bump
- not too bright

------------------------------------------------------------
10. TEXTURES (MANDATORY)
------------------------------------------------------------

You MUST declare:

1. Teal_Texture (rgb <0.06,0.34,0.43>)
2. Gold_Texture (rgb <0.86,0.69,0.34>)
3. White_Text_Texture (rgb <1,1,1>)   // for “ZAGUÁN”
4. Neon_Texture (cyan/green, emission)
5. Floor_Texture

------------------------------------------------------------
11. LOGO GEOMETRY (ARCH + TEXT)
------------------------------------------------------------

ARCH:

- Built from simple primitives:
  - vertical pillar: box
  - horizontal top: box
  - optional torus section for curve (allowed)
- Entire arch geometry MUST lie around <0,1.5,0>
- Arch sits at z = 0.

TEXT:

- Use text { ttf "timrom.ttf" } ONLY.
- “ZAGUÁN” must be White_Text_Texture.
- “AI” must be Gold_Texture.

Z-ORDER (MANDATORY):

- Background plane: z > 1.5
- Arch + bar + arrow: z = 0
- Text:            z = -0.6

------------------------------------------------------------
12. SYNCHRONIZED ANIMATION
------------------------------------------------------------

ARCH DROP:

- Start Y high above (e.g. y = 5)
- End   Y = 1.5
- Position computed as:
  Arch_Y = Arch_Y_Start + (Arch_Y_Final - Arch_Y_Start) * Ease_Motion;
- NO overshoot. Arch must STOP completely at its final Y.

TEXT RISE:

- “ZAGUÁN” and “AI” rise TOGETHER with the SAME Ease_Motion.
- Start Y = -3 (below floor)
- End   Y = 0.4
- Position:
  Text_Y = Text_Y_Start + (Text_Y_Final - Text_Y_Start) * Ease_Motion;

BOTH movements must complete at EXACTLY the same moment: when Ease_Motion reaches 1.

------------------------------------------------------------
13. OPTIONAL GLOW
------------------------------------------------------------

You MAY include a transparent glow shell around the logo.

------------------------------------------------------------
14. FINAL CHECKLIST
------------------------------------------------------------

Your final code MUST include:

- includes
- global_settings
- constants/easing
- camera
- lights
- neural-tech animated background
- neon rails
- floor
- textures (Teal, Gold, White, Neon)
- arch + bar + arrow at z=0
- text “ZAGUÁN AI” with correct materials at z=-0.6
- synchronized arch drop & text rise
- no syntax errors
- no undefined identifiers

Now generate the complete POV-Ray scene using these rules.  
Output ONLY the POV-Ray SDL code.
