#version 3.7;

#include "colors.inc"
#include "textures.inc"
#include "finish.inc"
#include "metals.inc"
#include "stones.inc"
#include "woods.inc"

// ---------------------------------------------------------
// GLOBAL SETTINGS
// ---------------------------------------------------------
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

// ---------------------------------------------------------
// CONSTANTS & TIMING
// ---------------------------------------------------------
#declare PI = 3.14159;

// Timing configuration
#declare MotionStart = 0.05;
#declare MotionEnd   = 0.40;
#declare CamStart    = 0.10;
#declare CamEnd      = 0.80;

// Motion Easing (Arch & Text)
#declare T_Motion_Raw = (clock - MotionStart) / (MotionEnd - MotionStart);
#declare T_Motion     = min(max(T_Motion_Raw, 0.0), 1.0);
#declare Ease_Motion  = T_Motion * T_Motion * (3.0 - 2.0 * T_Motion);

// Camera Easing
#declare T_Cam_Raw    = (clock - CamStart) / (CamEnd - CamStart);
#declare T_Cam        = min(max(T_Cam_Raw, 0.0), 1.0);
#declare Ease_Cam     = T_Cam * T_Cam * (3.0 - 2.0 * T_Cam);

// ---------------------------------------------------------
// CAMERA
// ---------------------------------------------------------
// Zooms out (moves away) from z = -10 to z = -14
// Drifts slightly up from y = 2 to y = 2.5
camera {
  perspective
  angle 40
  location <0, 2.0 + 0.5 * Ease_Cam, -10.0 - 4.0 * Ease_Cam>
  look_at <0, 1.5, 0>
}

// ---------------------------------------------------------
// LIGHT SOURCES
// ---------------------------------------------------------

// Key Light (Warm)
light_source {
  <10, 15, -10>
  color rgb <1.0, 0.97, 0.9>
  fade_distance 20
  fade_power 2
}

// Fill Light (Cool)
light_source {
  <-15, 5, -10>
  color rgb <0.3, 0.4, 0.6>
  shadowless
}

// Neon Backlight (Cyan/Green)
light_source {
  <0, 5, 2>
  color rgb <0.0, 0.8, 0.6> * 0.8
  fade_distance 10
  fade_power 2
}

// ---------------------------------------------------------
// TEXTURES
// ---------------------------------------------------------

#declare Teal_Texture = texture {
  pigment { color rgb <0.06, 0.34, 0.43> }
  finish {
    specular 0.4
    roughness 0.02
    reflection { 0.05, 0.1 fresnel on }
    conserve_energy
  }
}

#declare Gold_Texture = texture {
  pigment { color rgb <0.86, 0.69, 0.34> }
  finish {
    specular 0.8
    roughness 0.01
    reflection { 0.1, 0.4 metallic }
    metallic
  }
}

#declare White_Text_Texture = texture {
  pigment { color rgb <1, 1, 1> }
  finish {
    specular 0.3
    roughness 0.02
    reflection 0.03
    ambient 0.1
  }
}

#declare Neon_Texture = texture {
  pigment { color rgb <0.2, 1.0, 0.6> }
  finish {
    emission 0.6
    diffuse 0.1
    ambient 0
  }
}

#declare Floor_Texture = texture {
  pigment { color rgb <0.02, 0.03, 0.04> }
  normal { bumps 0.02 scale 0.1 }
  finish {
    reflection { 0.05, 0.15 fresnel on }
    specular 0.2
    roughness 0.05
    conserve_energy
  }
}

// ---------------------------------------------------------
// BACKGROUND (Neural Tech)
// ---------------------------------------------------------

// Background Plane (z = 4)
plane {
  -z, -4
  texture {
    pigment {
      marble
      turbulence 0.6
      color_map {
        [0.0 color rgb <0, 0, 0>]
        [0.4 color rgb <0.01, 0.05, 0.05>]
        [0.8 color rgb <0.0, 0.2, 0.2>]
        [0.95 color rgb <0.0, 0.8, 0.5>]
      }
      scale <3, 6, 1>
      // Animate texture downwards to simulate data flow
      translate y * -clock * 2
    }
    finish { emission 0.1 diffuse 0.5 }
  }
}

// Vertical Neon Rails
#declare Rail = box { <-0.05, -1, -0.05>, <0.05, 10, 0.05> texture { Neon_Texture } }

object { Rail translate <-5, 0, 2> }
object { Rail translate < 5, 0, 2> }
object { Rail translate <-3, 0, 3> }
object { Rail translate < 3, 0, 3> }

// Subtle Grid
#declare GridLineH = cylinder { <-10, 0, 0>, <10, 0, 0>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }
#declare GridLineV = cylinder { <0, -1, 0>, <0, 10, 0>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }

union {
  object { GridLineH translate <0, 1, 3.5> }
  object { GridLineH translate <0, 3, 3.5> }
  object { GridLineH translate <0, 5, 3.5> }
  object { GridLineV translate <-2, 0, 3.5> }
  object { GridLineV translate < 2, 0, 3.5> }
}

// ---------------------------------------------------------
// FLOOR
// ---------------------------------------------------------
plane {
  y, 0
  texture { Floor_Texture }
}

// ---------------------------------------------------------
// LOGO GEOMETRY & ANIMATION
// ---------------------------------------------------------

// 1. THE ARCH (Drops from above)
#declare Arch_Pillar = box { <-0.4, 0, -0.2>, <0.4, 3.0, 0.2> }
#declare Arch_Top    = box { <-2.5, 2.5, -0.25>, <2.5, 3.2, 0.25> }

#declare Arch_Structure = union {
  object { Arch_Pillar translate <-1.8, 0, 0> }
  object { Arch_Pillar translate < 1.8, 0, 0> }
  object { Arch_Top }
  texture { Teal_Texture }
}

// Gold Bar & Arrow
#declare Bar = box { <-2.2, 1.8, -0.1>, <1.5, 2.0, 0.1> texture { Gold_Texture } }
#declare ArrowHead = prism {
  linear_sweep
  linear_spline
  -0.1, 0.1, 4,
  <0, 0>, <0, 1>, <1, 0.5>, <0, 0>
  rotate x*90
  scale <0.5, 0.5, 1>
  translate <1.5, 1.65, 0>
  texture { Gold_Texture }
}

#declare Full_Arch_Obj = union {
  object { Arch_Structure }
  object { Bar }
  object { ArrowHead }
  // Centering adjustment for the object itself before animation
  translate <0, 0, 0> 
}

// Arch Animation Logic