from p5 import *
import numpy as np
import math
import random
import colorsys


#DATA

img = None            
setup_started = False   #guard so setup() only runs once w/ skia renderer

#animation state variables
colors = []             #list of (rgb, hsv) tuples  dot travels between
current_index = 0       #color dot is leaving from
t = 0                   #progress between current and next color 0 to 1
speed = 0.01            #how much t grows per frame


#FUNCTIONS

def make_wheel_array(w, h):
    #grids of x,y pixel coords
    # yy[row, col] = row, xx[row, col] = col
    yy, xx = np.mgrid[0:h, 0:w]

    #shift the origin to the center of the image and flip y axis
    dx = xx - w / 2
    dy = yy - h / 2

    r = np.sqrt(dx**2 + dy**2)  #polar coordinates

    hue = (np.degrees(np.arctan2(dy, dx)) % 360) / 360 #atan2 gives -180->180 degrees so % 360 wraps it to 0->360, then /360 scales to 0->1

    sat = np.minimum(r / (w / 2), 1)   #0 at center--white, 1 at the edge.

    #HSV -> RGB conversion, done for every pixel at once
    h6 = hue * 6                       #hue circle into 6 sections
    i = np.floor(h6).astype(int) % 6   #which section each pixel is in 0-5
    f = h6 - np.floor(h6)              #how far through that section 0-1
    v = np.ones_like(sat)              #brightness v = 1
    p = 1 - sat                        #min chann value
    q = 1 - sat * f                    #falling chann value
    tt = 1 - sat * (1 - f)             #rising chann value

    R = np.choose(i, [v, q, p, p, tt, v])     #uses v, p, q, tt for R, G, B.
    G = np.choose(i, [tt, v, v, q, p, p])     #np.choose picks the right one per pixel based on its section number i.
    B = np.choose(i, [p, p, tt, v, v, q])

    arr = np.zeros((h, w, 4), dtype=np.uint8)       #pack into an RGBA byte array scale to 0-255.
    arr[..., 0] = (R * 255).astype(np.uint8)
    arr[..., 1] = (G * 255).astype(np.uint8)
    arr[..., 2] = (B * 255).astype(np.uint8)
    arr[..., 3] = 255                  #fully opaque

    outside = r > w / 2 #anything farther from the center than the radius becomes white
    arr[outside] = (255, 255, 255, 255) 
    
    return arr


def rgb_to_hsv(rgb):    #convert an rgb tuple 0-255 to hue 0-360, sat 0-1, val 0-1
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    return (h * 360, s, v)


def generate_colors():  #5 random colors storing both the RGB and HSV form of each
    result = []        
    for _ in range(5):
        rgb = (random.randint(0, 255),
               random.randint(0, 255),
               random.randint(0, 255))
        result.append((rgb, rgb_to_hsv(rgb)))

    return result


def get_position(h, s):     #convert a (hue, saturation) pair into an (x, y) on the wheel
                                                    
    angle = math.radians(h)
    cx = width / 2
    cy = height / 2
    r = s * (width / 2)

    return cx + r * math.cos(angle), cy + r * math.sin(angle)


#PROCESSING

def setup():
    global img, colors, setup_started

    if setup_started:   #in skia renderer size() triggers a window-resize callback that calls setup() again--let only first call through
        return
    setup_started = True

    size(400, 400)

    img = create_image(width, height)
    img.load_pixels()

    px = img.pixels

    #build wheel, then copy it into the img pixel buffer
    arr = make_wheel_array(width, height)

    if px.ndim == 3:        #handles different buffer layouts so it works for pixels (h, w, 4), (h*w, 4), or a flat byte array
        px[:] = arr[..., :px.shape[2]]
    elif px.ndim == 2 and px.shape[1] in (3, 4):
        px[:] = arr.reshape(-1, 4)[:, :px.shape[1]]
    else:
        px[:] = arr.reshape(-1)[:px.size]

  
    img.update_pixels()

    colors = generate_colors()


def draw():
    global t, current_index

    background(255)
    image(img, 0, 0)

    next_index = (current_index + 1) % len(colors)
    rgb2, hsv2 = colors[next_index]
    h1, s1, v1 = colors[current_index][1]
    h2, s2, v2 = hsv2

    hue_difference = (h2 - h1 + 180) % 360 - 180   #shortest way around the circle -180-180


    h = (h1 + hue_difference * t) % 360
    s = s1 + (s2 - s1) * t
    v = v1 + (v2 - v1) * t

    no_stroke()
    fill(0, 0, 0, (1 - v) * 255)          #darken the wheel to match the current brightness (v)
    circle((width / 2, height / 2), width)

   
    x, y = get_position(h, s)

    #point filled with the next color in the list (rgb)
    fill(rgb2[0], rgb2[1], rgb2[2])
    circle((x, y), 15)

    #move to the next pair
    t += speed
    if t >= 1:
        t = 0
        current_index = next_index


run(renderer="skia")   #skia renderer is needed for create_image(), my vipsy doesnt work