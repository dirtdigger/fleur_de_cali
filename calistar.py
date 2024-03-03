import cadquery as cq
import numpy as np
from cadquery import exporters
import os

# Modifiable parameters
height    = 4 # mm, minimum is 0.8
chamferSize = 0.8
thickness = 4.0 #mm
fullWidth = 150
numMeasPoints = 3
diagWidth = 15
# adjustment at the corners to account for potentially
# uncalibrated pressure advance
pa = 0.8
# make chamfers?
fightElephantFoot = True

# The rest is all automated
sep = fullWidth/(numMeasPoints*2)

halfWidth = fullWidth/2

def thickLine(x0, x1, y0, y1, 
              height = height, thickness = thickness,
              wp = cq.Workplane()):
    dx = x1 - x0
    dy = y1 - y0
    
    xbar = (x0+x1)/2
    ybar = (y0+y1)/2
    
    theta = np.arctan2(dy, dx)
    print(theta)
    L = np.sqrt(dx**2 + dy**2)
    
    return (wp.center(0,0)
                .rect(L, thickness).extrude(height)
                .edges("|Z").chamfer(chamferSize)
                .rotate((0,0,0),(0,0,1), theta*180/np.pi)
                .translate((xbar,ybar,0))
                )

# Center line
result = thickLine(0, 0, 
                   -fullWidth/2 - thickness,
                   fullWidth/2+thickness)

# left and right lines, top and bottom
result = result + thickLine(-sep + thickness/2, 
                            -sep + thickness/2, 
                            sep - thickness,
                            fullWidth/2)

result = result + thickLine(-sep + thickness/2, 
                            -sep + thickness/2, 
                            -sep + thickness,
                            -fullWidth/2)

result = result + thickLine(sep - thickness/2, 
                            sep - thickness/2, 
                            sep - thickness,
                            fullWidth/2+thickness)

result = result + thickLine(sep - thickness/2, 
                            sep - thickness/2, 
                            0,
                            -fullWidth/2-thickness)
caliperStops = cq.Workplane()

# Draw all vertical pieces first
for ii in range(numMeasPoints):
    # Basic frame
    result = result + thickLine(-(ii+1)*sep + thickness/2, 
                                -(ii+1)*sep + thickness/2, 
                                -sep,
                                0)#sep/2)
    
    # Exterior caliper stops
    result = result + thickLine(-(ii+1)*sep -thickness/2, 
                                -(ii+1)*sep -thickness/2, 
#                                -sep/2,sep)
                                0,sep)
    
    
    
    result = result + thickLine((ii+1)*sep + thickness/2, 
                                (ii+1)*sep + thickness/2, 
                                #-sep/2, sep)
                                0,sep)
    
    result = result + thickLine((ii+1)*sep - thickness/2, 
                                (ii+1)*sep -thickness/2, 
                                -sep,
                                0)
    
    # Interior caliper stops
    # (thickness/2 + sep - thickness)/2
    # = sep/2 - thickness/4
    caliperStops = caliperStops + thickLine((ii+1)*sep - thickness*2/3 - pa*2, # formerly - thickness
                                (ii+1)*sep + thickness/2,
                                sep/2 + thickness/4,
                                sep/2 + thickness/4)

    caliperStops = caliperStops + thickLine(-(ii+1)*sep + thickness*2/3 + 2*pa,
                                -(ii+1)*sep - thickness/2,
                                sep/2-3*thickness/4,
                                sep/2-3*thickness/4)

    #result = result + thickLine(cq.Workplane(), 
    #                            (ii+1)*sep - thickness/2, 
    #                            (ii+1)*sep - thickness/2, 
    #                            sep/2,
    #                            sep)


# up til now everything has been vertical
# rotate and mirror to make the horizontal measure points
result = (result + 
          result.rotate((0,0,0),(0,0,1),-90)
          .mirror((0,1,0),(0,0,0)))
# Caliper stops shouldn't be mirrored
caliperStops = caliperStops + caliperStops.rotate((0,0,0),(0,0,1),-90)
result = result + caliperStops

# Cutouts to account for potentially poorly or non calibrated PA
paCuts = cq.Workplane()
for ii in range(numMeasPoints):
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate((-(ii+1)*sep - pa,-thickness/2,0)))
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate(((ii+1)*sep + pa,-thickness/2,0)))
    
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate(((ii+1)*sep - pa, sep/2 - thickness/4,0)))
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate((-(ii+1)*sep + pa, sep/2 - thickness/4,0)))

paCuts = (paCuts + 
          paCuts.rotate((0,0,0),(0,0,1),-90)
          .mirror((0,1,0),(0,0,0)))
result = result.cut(paCuts)

# diagonal caliper stops
diag = thickLine(0,0,
                 0, fullWidth/2+thickness)

diag = diag + thickLine(-diagWidth, 
                        -diagWidth, 
                        0,
                        fullWidth/2)
# Top left
for ii in range(numMeasPoints - 1):
    diag = diag + thickLine(-diagWidth, 
                            0,
                            (ii+2)*sep - thickness/2,
                            (ii+2)*sep - thickness/2)
    diag = diag.cut(cq.Workplane().circle(pa).extrude(height).translate((-thickness/2,sep*(ii+2) + pa,0)))

# Other four corners
diag = diag + diag.mirror((0,1,0), (0,0,0))
diag = diag + diag.rotate((0,0,0), (0,0,1), 90)
diag = diag.rotate((0,0,0),(0,0,1),45)

diag = diag.cut(thickLine(0,0,-fullWidth/2 - thickness,fullWidth/2 + thickness, thickness = sep*2) + 
                thickLine(-fullWidth/2,fullWidth/2, 0, 0, thickness = sep*2))

result = result + diag

# Center circle that indicates orientation
center = (cq.Workplane()
                   .lineTo(0,sep/3)
                   .threePointArc((-sep/3,0),(sep/3,0))
                   .close().extrude(height))


if fightElephantFoot:
    result = result.faces("Z").chamfer(0.4,0.4)
    center = center.faces("Z").chamfer(0.4,0.4)

result = result + center

# Last things, add axis orientation markers
ar1 = (cq.Workplane().sketch()
        .segment((0, -0.5),
                 (8, -0.5))
        .segment((8,-1))
        .segment((12,0))
        .segment((8,1))
        .segment((8,0.5))
        .segment((0,0.5))
        .close().assemble().finalize().extrude(height).translate((7,0,height-2)))
ar1 = ar1 + ar1.rotate((0,0,0),(0,0,1), 90)

#x = cq.Workplane().text("X", 5, 1, fontPath = '/usr/share/fonts/TTF/RobotoCondensed-Bold.ttf').faces("<Z").wires().toPending().extrude(height).translate((thickness,0,height-1))
#y = cq.Workplane().text("Y", 5, 1, fontPath = '/usr/share/fonts/TTF/Roboto-Bold.ttf').faces("<Z").wires().toPending().extrude(height).translate((0,thickness,height-1))

#show_object(result)


#result = result.cut(ar1)

show_object(result)
wd = os.getcwd()
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.stl')
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.step')


