import cadquery as cq

from cadquery import exporters

import os

height    = 4 # mm
filletRadius = 1.2

# Object is created mostly as a list of rectangles
# with centers and side lengths
vertices = ((-52.5,6.875),
            (-27.5,6.875),
            ( 27.5,6.875),
            ( 52.5,6.875),
            (-22.5,35),
            (22.5, 33.125),
            (-47.5, -6.875),
            (-22.5,-19.375),
            (22.5, -26.15),
            (47.5, -13.75),
            (52.5, 6.875),
            (0,0),
            (47.5,18.125),
            (6.875, 52.5), 
            (-9.375, 47.5), 
            (6.25, 27.5), 
            (-21.875, 22.5), 
            (37.5, 22.5), 
            (0, 0), 
            (-23.75, -22.5), 
            (30.625, -22.5), 
            (6.25, -27.5), 
            (-11.25, -47.5), 
            (18.125, -47.5), 
            (6.875, -52.5))

sideLength = ((5,36.25),
              (5,36.25),
              (5,36.25),
              (5,36.25),
              (5,30),
              (5, 43.75),
              (5,36.25),
              (5,61.25),
              (5,57.5),
              (5,32.5),
              (5,36.25),
              (5,110),
              (5,13.75),
              (36.25, 5), 
              (41.25, 5), 
              (37.5, 5), 
              (66.25, 5), 
              (35, 5), 
              (110, 5), 
              (52.5, 5), 
              (38.75, 5), 
              (37.5, 5), 
              (27.5, 5), 
              (13.75, 5), 
              (36.25, 5))

N = len(vertices)

# create the main frame
result = (cq.Workplane().
          center(vertices[0][0], vertices[0][1]).
          rect(sideLength[0][0],sideLength[0][1]).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )

for ii in range(1,N):
    result = result + (cq.Workplane().center( vertices[ii][0], vertices[ii][1]).rect(sideLength[ii][0],sideLength[ii][1]).extrude(height).
    edges("|Z").chamfer(filletRadius))



# diagonals
result2 = (cq.Workplane().
          center(0, 47.5).
          rect(33,5).
          extrude(height).
          edges("|Z").chamfer(filletRadius).
          rotate((0,0,0),(0,0,1),-45)
          )

for ii in range(3):
    result2 = result2.rotate((0,0,0),(0,0,1),90) + (cq.Workplane().
              center(0, 47.5).
              rect(33,5).
              extrude(height).
              edges("|Z").chamfer(filletRadius).
              rotate((0,0,0),(0,0,1),-45)
              )


# results 3 and 4 are the outer diagonal pieces
result3 = (cq.Workplane().
          center(11.1405, 52.5).
          rect(22.281,5).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )


result3 = result3 + (cq.Workplane().
          center(11.1405, -52.5).
          rect(22.281,5).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )



result3 = result3.rotate((0,0,0),(0,0,1),-45)


result4 = (cq.Workplane().
          center(-52.5,7.875).
          rect(5,15.75).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )


result4 = result4 + (cq.Workplane().
          center(52.5, 7.875).
          rect(5,15.75).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )

result4 = result4.rotate((0,0,0),(0,0,1),-45)

result = result + result2 + result3 + result4


# Some cleanup to get rid of unsightly edges
clean = (cq.Workplane().
          center(57.5,0).
          rect(5,110).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )


clean = clean + (cq.Workplane().
          center(-57.5,0).
          rect(5,110).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )

clean = clean + (cq.Workplane().
          center(0,57.5).
          rect(110,5).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )
clean = clean.rotate((0,0,0),(0,0,1),-45)

clean = clean + (cq.Workplane().
          center(-36, -52.5).
          rect(35,5).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )
result = result.cut(clean)


# Add a square center post and rotate it
center = (cq.Workplane().
          center(0,0).
          rect(10,10).
          extrude(height).
          edges("|Z").chamfer(filletRadius)
          )
center = center.rotate((0,0,0),(0,0,1),-45)

result = result + center


# Chamfer the top and bottom edges to avoid
# elephant's foot
result = result.faces("+Z").chamfer(0.4,0.4)

result = result.faces("-Z").chamfer(0.4,0.4)

# Finally, the top markings so you know how
# to orient it
bore = (cq.Workplane().
          center(0,0).
          circle(2).
          extrude(3).translate((0,0,height-1))
          )
# Right arrow
ar1 = (cq.Workplane().sketch()
        .segment((0, -0.5),
                 (8, -0.5))
        .segment((8,-1))
        .segment((12,0))
        .segment((8,1))
        .segment((8,0.5))
        .segment((0,0.5))
        .close().assemble().finalize().extrude(3).translate((5,0,height-1)))
# Left arrow
ar2 = ar1.rotate((0,0,0),(0,0,1), 90)

result = result.cut(bore + ar1 + ar2)


show_object(result)

wd = os.getcwd()
exporters.export(result, f'{wd}/fleur_de_cali.stl')
exporters.export(result, f'{wd}/fleur_de_cali.step')
