# HSV_RGB_Conversion_Color_Wheel
Drawn and Animated color wheel made using Python

- Generates a 400 × 400 HSV color wheel using pixel coordinates and converts the HSV values into RGB.
- Uses hue to determine color around the wheel and saturation to determine distance from the center.
- Generates five random RGB colors and stores both their RGB and HSV values.
- Converts each color's hue and saturation into an (x, y) position on the wheel.
- Animates a dot between the five colors by gradually interpolating hue, saturation, and brightness.
- Calculates the shortest path around the hue circle to create smoother color transitions.
- Adjusts the wheel's brightness using a transparent black overlay.
- Loops continuously through all five randomly generated colors.
  
Libraries: p5, NumPy, math, random, colorsys.
