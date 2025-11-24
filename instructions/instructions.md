# **THE PROMPT**

Use the following *exact* instruction set when generating POV-Ray code:

---

## **GOAL**

Create a single, cohesive, fully-renderable POV-Ray `.pov` scene that is visually stunning, technically advanced, and demonstrates the upper limits of procedural geometry, physically convincing lighting, and atmospheric realism.
The output must be **complete**, **self-contained**, and **not rely on include files beyond the built-in ones**.

The scene should look like a piece of concept art for a high-budget sci-fi world.

---

## **SCENE REQUIREMENTS**

### **1. Theme**

A monumental, ancient megastructure standing in a vast alien desert at sunrise.
Tone: quiet, enormous, timeless, eerie.
Architecture: a mix of brutalist mass and intricate geometric ornamentation.

### **2. Geometry Requirements**

The scene **must contain**:

* A towering central structure (≥200 meters scale in scene units)
* Intricate procedural details using `function`, `isosurface`, or layered CSG
* A foreground element (rock, broken pillar, sand ripple) to anchor composition
* A sense of enormous scale using:

  * aerial perspective
  * layering
  * size contrast

### **3. Lighting Requirements**

Lighting must be dramatic and physically motivated:

* A low-angle sunrise light source with soft warm tones
* Global illumination with **radiosity**
* Long shadows stretching across dunes
* Subtle atmospheric media for volumetric light scattering

### **4. Atmosphere Requirements**

Use **media** or **fog** to create:

* Depth haze
* Light rays (if feasible)
* Slight color gradient in the sky

### **5. Materials & Textures**

All materials must be custom.
No plain colors or single pigment blocks.

Use:

* layered textures
* procedural patterns
* subtle bumps
* realistic diffuse/specular balance
* metallic + matte contrasts on the structure

### **6. Camera Requirements**

The camera must:

* Use a wide but not extreme FOV (30–55 degrees)
* Be positioned near the ground to emphasize scale
* Include depth-of-field OR keep everything crisp (model decides based on artistic choice)

### **7. Code Structure Requirements**

The code must:

* Start with global settings (radiosity, photons optional)
* Define reusable textures and materials
* Use comments to explain key artistic decisions
* Be deterministic and renderable without debugging
* End with the `camera` declaration

---

## **ABSOLUTE RULES**

**Do NOT:**

* Output explanation outside code blocks
* Use placeholder geometry
* Use undefined textures
* Output partial scenes
* Produce toy examples (e.g., spheres floating in space)

**Do:**

* Deliver a full POV-Ray scene that I can render as-is
* Favor mathematical elegance over random shapes
* Use comments sparingly but meaningfully
* Ensure the final render is striking, cinematic, and memorable

---

# **FINAL INSTRUCTION TO THE MODEL**

Generate **only** a complete, ready-to-render POV-Ray scene file following all constraints above.
No commentary.
No Markdown.
Just pure `.pov` code.
