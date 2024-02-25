import cadquery as cq
import numpy as np
from cadquery import exporters
import os

# Modifiable parameters
height    = 3 # mm, minimum is 0.8
filletRadius = 0.8
thickness = 4.0 #mm
fullWidth = 150
numMeasPoints = 5


# The rest is all automated
sep = fullWidth/(numMeasPoints*2)
halfWidth = fullWidth/2

def thickLine(wp, x0, x1, y0, y1, height = height, thickness = thickness):
    dx = x1 - x0
    dy = y1 - y0
    
    xbar = (x0+x1)/2
    ybar = (y0+y1)/2
    
    theta = np.arctan2(dy, dx)
    print(theta)
    L = np.sqrt(dx**2 + dy**2)
    
    return (wp.center(0,0).
                rect(L, thickness).extrude(height)
                .edges("|Z").chamfer(filletRadius)
                .rotate((0,0,0),(0,0,1), theta*180/np.pi)
                .translate((xbar,ybar,0))
                )
    
# Center line
result = thickLine(cq.Workplane(), 
                   0, 0, 
                   -fullWidth/2 - thickness,
                   fullWidth/2+thickness)
# Draw all vertical pieces first
for ii in range(numMeasPoints):
    # Basic frame
    result = result + thickLine(cq.Workplane(), 
                       -(ii+1)*sep + thickness/2, 
                       -(ii+1)*sep + thickness/2, 
                       -fullWidth/2 - thickness,
                        sep/2)
    
    result = result + thickLine(cq.Workplane(), 
                                -(ii+1)*sep + thickness/2, 
                                -(ii+1)*sep + thickness/2, 
                                 sep-thickness,
                                 fullWidth/2 + thickness)
    # Exterior caliper stops
    result = result + thickLine(cq.Workplane(), 
                                -(ii+1)*sep -thickness/2, 
                                -(ii+1)*sep -thickness/2, 
                                -sep/2,sep)
    
    result = result + thickLine(cq.Workplane(),
                                (ii+1)*sep + thickness/2, 
                                (ii+1)*sep + thickness/2, 
                                -sep/2,
                                sep)
    # Interior caliper stops
    result = result + thickLine(cq.Workplane(), 
                                (ii+1)*sep - thickness/2, 
                                (ii+1)*sep -thickness/2, 
                                -fullWidth/2 - thickness,
                                0)
    
    result = result + thickLine(cq.Workplane(), 
                                (ii+1)*sep - thickness/2, 
                                (ii+1)*sep - thickness/2, 
                                sep/2,
                                fullWidth/2 + thickness)


# up til now everything has been vertical
# rotate and make the horizontal measure points
result = result + result.rotate((0,0,0),(0,0,1),-90)


# Trim off everything that is outside of a bounding octagon
outside = (
    cq.Workplane()
    .polygon(8, (fullWidth)/np.cos(np.pi/8))
    .extrude(height).rotate((0,0,0),(0,0,1),22.5)
)

osquare = (cq.Workplane()
.polygon(4, fullWidth/np.cos(np.pi/4))
.extrude(height))

# Create the diagonals
diag = (
    osquare.
    cut(
    cq.Workplane()
    .polygon(4, (fullWidth - 2*thickness)/np.cos(np.pi/4))
    .extrude(height).rotate((0,0,0),(0,0,1),0)
).intersect(outside))

diag = diag.cut(thickLine(cq.Workplane(), 0,0,-fullWidth/2,fullWidth/2, thickness = sep*2) + 
                thickLine(cq.Workplane(), -fullWidth/2,fullWidth/2, 0, 0, thickness = sep*2))


result = result + diag

frame = (outside
         + thickLine(cq.Workplane(), 
                     0, 0, 
                     -fullWidth/2 - thickness, 
                     fullWidth/2 + thickness, 
                     thickness = 2*(sep) - thickness)
           .translate((thickness/2, 0, 0))
         + thickLine(cq.Workplane(), 
                     -fullWidth/2 - thickness, 
                     fullWidth/2 + thickness, 
                     0,0,
                     thickness = 2*(sep) - thickness)
           .translate((0, thickness/2, 0))
         )
result = result.intersect(frame)

# diagonal caliper stops

nub1 = thickLine(cq.Workplane(),
          0, (fullWidth/2 + thickness)*np.sin(np.pi/8) + thickness,
          fullWidth/2 + thickness/2, fullWidth/2 + thickness/2).rotate((0,0,0), (0,0,1), 45)

nub1 = nub1.intersect(cq.Workplane().center(0, 0).
                      rect(fullWidth, fullWidth).
                      extrude(height))

nub2 = nub1.mirror((1,-1,0), (0,0,0))

nub3 = nub1.mirror(mirrorPlane="XZ")

nub4 = nub3.mirror((1,1,0), (0,0,0))
 
nub = nub1 + nub2 + nub3 + nub4

result = result + nub

result = result.faces("+Z").chamfer(0.4,0.4)

result = result.faces("-Z").chamfer(0.4,0.4)


# Last things, add some flair!
ar1 = (cq.Workplane().sketch()
        .segment((0, -0.5),
                 (8, -0.5))
        .segment((8,-1))
        .segment((12,0))
        .segment((8,1))
        .segment((8,0.5))
        .segment((0,0.5))
        .close().assemble().finalize().extrude(height).translate((5,0,height-1)))
ar1 = ar1 + ar1.rotate((0,0,0),(0,0,1), 90)


result = result.cut(ar1)
show_object(result)
wd = os.getcwd()
exporters.export(result, f'{wd}/fleur_de_cali_{fullWidth}x{numMeasPoints}.stl')
exporters.export(result, f'{wd}/fleur_de_cali_{fullWidth}x{numMeasPoints}.step')


