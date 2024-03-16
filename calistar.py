import cadquery as cq
import numpy as np
from cadquery import exporters
import os

# Modifiable parameters
height    = 4 # mm, minimum is 0.8
chamferSize = 0.8
thickness = 4.0 #mm
fullWidth = 100
numMeasPoints = 2
diagWidth = 10


# adjustment at the corners to account for potentially
# uncalibrated pressure advance
pa = 0.6
# make chamfers?
fightElephantFoot = True

# The rest is all automated
sep = fullWidth/(numMeasPoints*2)
centerWidth = max(sep - 2*thickness,20)

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

def polygonRing(radius, 
            height = height, 
            thickness = thickness,
            wp = cq.Workplane(),
            chamfer = True,
            sides = 8):
    
    octOuter = wp.polygon(sides,radius*2/np.cos(np.pi/sides)).extrude(height)
    octInner = wp.polygon(sides,(radius - thickness)*2/np.cos(np.pi/sides)).extrude(height)
    return octOuter.cut(octInner).rotate((0,0,0),(0,0,1),180/sides).edges("|Z").chamfer(chamferSize)


def ring(radius, 
            height = height, 
            thickness = thickness,
            wp = cq.Workplane(),
            angleStart = 0,
            angleEnd = 360):
    
    if angleStart != (angleEnd % 360):
        theta2 = (angleStart + angleEnd)/2
        angleEnd = angleStart + ((angleEnd - angleStart) % 360)
        print(angleStart, angleEnd)
        circOuter = (wp.lineTo(radius*np.cos(angleStart*np.pi/180),
                               radius*np.sin(angleStart*np.pi/180))
                 .threePointArc((radius*np.cos(theta2*np.pi/180),
                                 radius*np.sin(theta2*np.pi/180)),
                                (radius*np.cos(angleEnd*np.pi/180),
                                 radius*np.sin(angleEnd*np.pi/180)))
                 .close().extrude(height))
    else:
        circOuter = wp.circle(radius).extrude(height)
    circInner = wp.circle(radius - thickness).extrude(height)
    return circOuter.cut(circInner)
    

# Center line
result = cq.Workplane()

"""result = result + thickLine(-centerWidth/2 + thickness/2, 
                            -centerWidth/2 + thickness/2, 
                   -fullWidth/2 - thickness,
                   fullWidth/2+thickness)

result = result + thickLine(centerWidth/2 - thickness/2, 
                            centerWidth/2 - thickness/2, 
                   -fullWidth/2 - thickness,
                   fullWidth/2+thickness)
"""

centerHull = thickLine(0,0,
                        -fullWidth/2-thickness,
                       fullWidth/2+thickness,thickness=centerWidth)
centerHull = centerHull + centerHull.rotate((0,0,0),(0,0,1),90)


result = result + thickLine(-centerWidth/2 + thickness/2, 
                            -centerWidth/2 + thickness/2, 
                   centerWidth/2 - thickness,
                   fullWidth/2+thickness)

result = result + thickLine(-centerWidth/2 + thickness/2, 
                            -centerWidth/2 + thickness/2, 
                   -fullWidth/2 - thickness,
                   -centerWidth/2 + thickness)

result = result + thickLine(centerWidth/2 - thickness/2, 
                            centerWidth/2 - thickness/2, 
                            -fullWidth/2 - thickness,
                             -centerWidth/2 + thickness)

result = result + thickLine(centerWidth/2 - thickness/2, 
                            centerWidth/2 - thickness/2, 
                            centerWidth/2 - thickness,
                             fullWidth/2 + thickness)


result = result + thickLine(centerWidth/2 - thickness/2, 
                            -centerWidth/2 + thickness/2, 
                            centerWidth/2 - thickness/2,
                            -centerWidth/2 + thickness/2)

result = result + thickLine(centerWidth/2 - thickness/2, 
                            -centerWidth/2 + thickness/2, 
                            -centerWidth/2 + thickness/2,
                            centerWidth/2 - thickness/2)



caliperStops = cq.Workplane()

# Draw all vertical pieces first
for ii in range(0,numMeasPoints):
    # Basic frame
    """result = result + thickLine(-(ii+1)*sep + thickness/2, 
                                -(ii+1)*sep + thickness/2, 
                                -thickness - centerWidth/2,
                                 thickness - centerWidth/2)#sep/2)
    """
    # Exterior caliper stops
    result = result + thickLine(-(ii+1)*sep -thickness/2, 
                                -(ii+1)*sep -thickness/2, 
#                                -sep/2,sep)
                                -centerWidth/2,centerWidth/2)
    
    
    result = result + thickLine((ii+1)*sep + thickness/2, 
                                (ii+1)*sep + thickness/2, 
                                #-sep/2, sep)
                                -centerWidth/2,centerWidth/2)
    
    """result = result + thickLine((ii+1)*sep - thickness/2, 
                                (ii+1)*sep - thickness/2, 
                                -thickness - centerWidth/2,
                                 thickness - centerWidth/2)
    """
    # Interior caliper stops
    # (thickness/2 + sep - thickness)/2
    # = sep/2 - thickness/4
    if ii > -1:
        
        
        result = result + thickLine((ii+1)*sep - thickness/2, 
                                (ii+1)*sep - thickness/2, 
                                #-sep/2, sep)
                                -centerWidth/2 - 3,
                                -centerWidth/2 + thickness/2)
        result = result + thickLine(-(ii+1)*sep + thickness/2, 
                                -(ii+1)*sep + thickness/2, 
                                #-sep/2, sep)
                                -centerWidth/2 - 3,
                                -centerWidth/2+thickness/2)
    
        """caliperStops = caliperStops + thickLine((ii+1)*sep - thickness*2/3 - pa*2, # formerly - thickness
                                (ii+1)*sep + thickness/2,
                                 thickness/2,
                                 thickness/2)

        caliperStops = caliperStops + thickLine(-(ii+1)*sep + thickness*2/3 + 2*pa,
                                -(ii+1)*sep - thickness/2,
                                -thickness/2,
                                -thickness/2)"""

        caliperStops = caliperStops + thickLine((ii+1)*sep-thickness/2, # formerly - thickness
                        (ii+1)*sep-thickness/2,
                         centerWidth/2,
                         0)
        caliperStops = caliperStops + thickLine(-(ii+1)*sep+thickness/2, # formerly - thickness
                -(ii+1)*sep+thickness/2,
                 0,
                 -centerWidth/2)

    
    """
    caliperStops = caliperStops + thickLine((ii+1)*sep - thickness/2, # formerly - thickness
                                            (ii+1)*sep - thickness/2,
                                            sep/2 - thickness,
                                            sep/2,
                                            chamferStart = False)

    caliperStops = caliperStops + thickLine(-(ii+1)*sep + thickness/2, # formerly - thickness
                                            -(ii+1)*sep + thickness/2,
                                            sep/2,
                                            sep/2 + thickness,
                                            chamferEnd = False)
    """
    

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
for ii in range(0,numMeasPoints):
    #paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate((-(ii+1)*sep - pa,-thickness/2,0)))
    #paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate(((ii+1)*sep + pa,-thickness/2,0)))
    
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate(((ii+1)*sep + pa, -centerWidth/2,0)))
    paCuts = paCuts + (cq.Workplane().circle(pa).extrude(2*height).translate((-(ii+1)*sep - pa, -centerWidth/2,0)))

paCuts = (paCuts + 
          paCuts.rotate((0,0,0),(0,0,1),-90)
          .mirror((0,1,0),(0,0,0)))
result = result.cut(paCuts)



# diagonal caliper stops
diag = thickLine(0,0,
                 0, fullWidth/2+thickness)

"""diag = diag + thickLine(-diagWidth, 
                        -diagWidth, 
                        0,
                        fullWidth/2)"""
# Top left
for ii in range(numMeasPoints - 1):
    diag = diag + thickLine(-diagWidth, 
                            0,
                            (ii+2)*sep - thickness/2,
                            (ii+2)*sep - thickness/2)
    diag = diag + ring((ii+2)*sep, angleStart = 90, angleEnd = 135)
    diag = diag.cut(cq.Workplane().circle(pa).extrude(height).translate((-thickness/2,sep*(ii+2) + pa,0)))

# Other four corners
diag = diag + diag.mirror((0,1,0), (0,0,0))
diag = diag.rotate((0,0,0),(0,0,1),45)
diag = diag.cut(centerHull)
diag = diag + diag.rotate((0,0,0), (0,0,1), 90)





result = result + diag

# Center circle that indicates orientation
center = (cq.Workplane()
                   .lineTo(0,centerWidth/3)
                   .threePointArc((-centerWidth/3,0),(centerWidth/3,0))
                   .close().extrude(height))




if fightElephantFoot:
    result = result.faces("Z").chamfer(0.6,0.6)
    center = center.faces("Z").chamfer(0.6,0.6)

result = result + center
result = result.cut((cq.Workplane()
                   .lineTo(0,thickness/2)
                   .threePointArc((-thickness/2,0),(thickness/2,0))
                   .close().extrude(height).translate((0,0,height-1))))
#
#for ii in range(numMeasPoints-1):
#    result = result + ring((ii+2)*sep).cut(centerHull)
show_object(result)

wd = os.getcwd()
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.stl')
exporters.export(result, f'{wd}/calistar_{fullWidth}x{numMeasPoints}.step')


