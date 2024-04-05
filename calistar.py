import cadquery as cq
import numpy as np
from cadquery import exporters
import os

# Modifiable parameters
height    = 4 # mm, minimum is 0.8
chamferSize = 0.8 # mm
thickness = 4.0 # mm
# Recommend fullWidth/numMeasPoints does not fall below 40
fullWidth = 120 # mm
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
              wp = cq.Workplane(),
              chamferStart = True,
              chamferEnd = True):
    dx = x1 - x0
    dy = y1 - y0
    
    xbar = (x0+x1)/2
    ybar = (y0+y1)/2
    
    theta = np.arctan2(dy, dx)
    print(theta)
    L = np.sqrt(dx**2 + dy**2)
    
    line = (wp.center(0,0)
                .rect(L, thickness).extrude(height)
                )
    
    if chamferStart:
        line = line.faces("-X").edges("|Z").chamfer(chamferSize)
    
    if chamferEnd:
        line = line.faces("+X").edges("|Z").chamfer(chamferSize)
    
    
    return (line.rotate((0,0,0),(0,0,1), theta*180/np.pi)
                .translate((xbar,ybar,0))
                )

def paWedge(sideLength = chamferSize, 
            mirrorX = False, 
            mirrorY = False, 
            wp = cq.Workplane(),
            height = height*2):
    
    wedge = (wp.moveTo(0,0)
               .lineTo(0,sideLength)
               .lineTo(sideLength,0)
               .close().extrude(height)
             )
    if mirrorX:
        # negate x coords
        wedge = wedge.mirror((1,0,0),(0,0,0))
    if mirrorY:
        # negate y coords
        wedge = wedge.mirror((0,1,0),(0,0,0))
    return wedge
    

# Center line
result = thickLine(0, 0, 
                   -fullWidth/2 - thickness,
                   fullWidth/2+thickness)

# left and right lines, top and bottom
result += thickLine(-sep + thickness/2, 
                    -sep + thickness/2, 
                    sep - thickness,
                    fullWidth/2)

result += thickLine(-sep + thickness/2, 
                    -sep + thickness/2, 
                    -sep + thickness,
                    -fullWidth/2)

result += thickLine(sep - thickness/2, 
                    sep - thickness/2, 
                    sep - thickness,
                    fullWidth/2+thickness)

result += thickLine(sep - thickness/2, 
                    sep - thickness/2, 
                    0,
                    -fullWidth/2-thickness)
caliperStops = cq.Workplane()

# Draw all vertical pieces first
for ii in range(numMeasPoints):
    # Basic frame
    result += thickLine(-(ii+1)*sep + thickness/2, 
                        -(ii+1)*sep + thickness/2, 
                        -sep,
                        0)
    
    # Exterior caliper stops
    result += thickLine(-(ii+1)*sep -thickness/2, 
                        -(ii+1)*sep -thickness/2, 
                        -thickness,sep)
    
    
    
    result += thickLine((ii+1)*sep + thickness/2, 
                        (ii+1)*sep + thickness/2, 
                        -thickness,sep)
    
    result += thickLine((ii+1)*sep - thickness/2, 
                        (ii+1)*sep -thickness/2, 
                        -sep,
                        0)
    
    # Interior caliper stops
    caliperStops += thickLine((ii+1)*sep - thickness*2/3 - pa*2,
                              (ii+1)*sep + thickness/2,
                              sep/2 + thickness/4,
                              sep/2 + thickness/4)

    caliperStops += thickLine(-(ii+1)*sep + thickness*2/3 + 2*pa,
                              -(ii+1)*sep - thickness/2,
                              sep/2-3*thickness/4,
                              sep/2-3*thickness/4)
    


# up til now everything has been vertical
# rotate and mirror to make the horizontal measure points
result += (result.rotate((0,0,0),(0,0,1),-90)
          .mirror((0,1,0),(0,0,0)))
# Caliper stops shouldn't be mirrored
caliperStops += (caliperStops.
                 rotate((0,0,0),(0,0,1),-90))
result += caliperStops

# Cutouts to account for potentially poorly or non calibrated PA
paCuts = cq.Workplane()
for ii in range(numMeasPoints):
    paCuts += (paWedge(mirrorY = True)
               .translate((-(ii+1)*sep, 
                           sep/2 - thickness/4,
                           0)))
    paCuts += (paWedge(mirrorX = True)
               .translate(((ii+1)*sep, 
                           sep/2 - thickness/4,
                           0)))
    
    paCuts += (paWedge()
               .translate((sep/2 - thickness/4,
                           -(ii+1)*sep, 
                           0)))
    paCuts += (paWedge(mirrorX = True,mirrorY=True)
               .translate((sep/2 - thickness/4,
                           (ii+1)*sep, 
                           0)))

result = result.cut(paCuts)


# diagonal caliper stops
diag = thickLine(0,0,
                 0, fullWidth/2+thickness)

diag += thickLine(-diagWidth, 
                        -diagWidth, 
                        0,
                        fullWidth/2)
# Top left
for ii in range(numMeasPoints - 1):
    diag += thickLine(-diagWidth, 
                            0,
                            (ii+2)*sep - thickness/2,
                            (ii+2)*sep - thickness/2)
    diag -= (paWedge()
             .translate((-thickness/2,
                         (ii+2)*sep, 
                         0)))

    #diag = diag.cut(cq.Workplane().circle(pa).extrude(height).translate((-thickness/2,sep*(ii+2) + pa,0)))

# Other four corners
diag += diag.mirror((0,1,0), (0,0,0))
diag +=  diag.rotate((0,0,0), (0,0,1), 90)

# rotate the whole thing and cut out the central frame
diag = diag.rotate((0,0,0),(0,0,1),45)
diag -= (thickLine(0,0,-fullWidth/2 - thickness,fullWidth/2 + thickness, thickness = sep*2) + 
         thickLine(-fullWidth/2,fullWidth/2, 0, 0, thickness = sep*2))

result += diag

# Center circle that indicates orientation
center = (cq.Workplane()
                   .lineTo(0,sep/3)
                   .threePointArc((-sep/3,0),(sep/3,0))
                   .close().extrude(height))


if fightElephantFoot:
    result = result.faces("+Z").chamfer(0.4,0.4)
    result = result.faces("-Z").chamfer(0.4,0.4)
    center = center.faces("+Z").chamfer(0.4,0.4)
    center = center.faces("-Z").chamfer(0.4,0.4)

result += center
result -= ((cq.Workplane()
            .lineTo(0,thickness/2)
            .threePointArc((-thickness/2,0),
                           (thickness/2,0))
            .close().extrude(height).translate((0,0,height-1))))


# If this line is causing issues, you can comment it out
# (it's only valid if you're using CQ-editor
try:
    show_object(result)
except:
    # must be running from an environment other than cq-editor
    pass
        
wd = os.getcwd()
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.stl')
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.step')


