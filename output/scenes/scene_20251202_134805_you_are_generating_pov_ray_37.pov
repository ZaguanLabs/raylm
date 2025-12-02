```povray
#include "colors.inc"
#include "textures.inc"
#include "finish.inc"

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

#declare PI = 3.14159;

#declare MotionStart = 0.05;
#declare MotionEnd   = 0.40;
#declare CamStart    = 0.10;
#declare CamEnd      = 0.80;

#declare T_Motion_Raw = (clock - MotionStart) / (MotionEnd - MotionStart);
#declare T_Motion     = min(max(T_Motion_Raw, 0.0), 1.0);
#declare Ease_Motion  = T_Motion * T_Motion * (3.0 - 2.0 * T_Motion);

#declare T_Cam_Raw    = (clock - CamStart) / (CamEnd - CamStart);
#declare T_Cam        = min(max(T_Cam_Raw, 0.0), 1.0);
#declare Ease_Cam     = T_Cam * T_Cam * (3.0 - 2.0 * T_Cam);

camera {
  perspective
  angle 40
  location <0, 2.0 + 0.5 * Ease_Cam, -10.0 - 4.0 * Ease_Cam>
  look_at <0, 1.5, 0>
}

light_source {
  <10, 15, -10>
  color rgb <1.0, 0.97, 0.9>
}

light_source {
  <-15, 5, -10>
  color rgb <0.3, 0.4, 0.6>
  shadowless
}

light_source {
  <0, 5, 2>
  color rgb <0.0, 0.8, 0.6> * 0.8
}

#declare Teal_Texture = texture {
  pigment { color rgb <0.06, 0.34, 0.43> }
  finish {
    specular 0.2
    roughness 0.02
    reflection 0.05
  }
}

#declare Gold_Texture = texture {
  pigment { color rgb <0.86, 0.69, 0.34> }
  finish {
    specular 0.3
    roughness 0.02
    reflection 0.08
  }
}

#declare White_Text_Texture = texture {
  pigment { color rgb <1, 1, 1> }
  finish {
    specular 0.25
    roughness 0.02
    reflection 0.03
  }
}

#declare Neon_Texture = texture {
  pigment { color rgb <0.2, 1.0, 0.6> }
  finish {
    emission 0.25
    diffuse 0.1
    specular 0.1
  }
}

#declare Floor_Texture = texture {
  pigment { color rgb <0.02, 0.03, 0.04> }
  normal { bumps 0.02 scale 0.1 }
  finish {
    reflection 0.1
    specular 0.2
    roughness 0.05
  }
}

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
      translate y * -clock * 2
    }
    finish { emission 0.1 diffuse 0.5 }
  }
}

box { <-0.05, -1, -0.05>, <0.05, 10, 0.05> texture { Neon_Texture } translate <-5, 0, 2> }
box { <-0.05, -1, -0.05>, <0.05, 10, 0.05> texture { Neon_Texture } translate < 5, 0, 2> }
box { <-0.05, -1, -0.05>, <0.05, 10, 0.05> texture { Neon_Texture } translate <-3, 0, 3> }
box { <-0.05, -1, -0.05>, <0.05, 10, 0.05> texture { Neon_Texture } translate < 3, 0, 3> }

cylinder { <-10, 1, 3.5>, <10, 1, 3.5>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }
cylinder { <-10, 3, 3.5>, <10, 3, 3.5>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }
cylinder { <-10, 5, 3.5>, <10, 5, 3.5>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }
cylinder { <-2, -1, 3.5>, <-2, 10, 3.5>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }
cylinder { < 2, -1, 3.5>, < 2, 10, 3.5>, 0.02 texture { pigment { color rgb <0, 0.2, 0.2> } finish { emission 0.2 } } }

plane {
  y, 0
  texture { Floor_Texture }
}

#declare Arch_Y_Start = 5.0;
#declare Arch_Y_Final = 1.5;
#declare Arch_Y = Arch_Y_Start + (Arch_Y_Final - Arch_Y_Start) * Ease_Motion;

union {
  box { <-0.4, 0, -0.2>, <0.4, 3.0, 0.2> translate <-1.8, 0, 0> }
  box { <-0.4, 0, -0.2>, <0.4, 3.0, 0.2> translate < 1.8, 0, 0> }
  box { <-2.5, 2.5, -0.25>, <2.5, 3.2, 0.25> }
  box { <-2.2, 1.8, -0.1>, <1.5, 2.0, 0.1> }
  cone { <1.5, 1.9, 0>, 0.3, <2.0, 1.9, 0>, 0 }
  texture { Teal_Texture }
  translate <0, Arch_Y - Arch_Y_Final, 0>
}

#declare Text_Y_Start = -3.0;
#declare Text_Y_Final = 0.4;
#declare Text_Y = Text_Y_Start + (Text_Y_Final - Text_Y_Start) * Ease_Motion;

text {
  ttf "timrom.ttf" "ZAGUAN" 0.2, 0
  texture { White_Text_Texture }
  scale 0.5
  translate <-2.0, Text_Y, -0.6>
}

text {
  ttf "timrom.ttf" "AI" 0.2, 0
  texture { Gold_Texture }
  scale 0.5
  translate <1.2, Text_Y, -0.6>
}
```