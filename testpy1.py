import math
import numpy as np
import matplotlib.pyplot as plt

from itertools import combinations

class Circle:

    def __init__(self, radius, center):
        self.radius = float(radius)
        self.center = center
        self.area = math.pi * self.radius ** 2

    def get_area(self):
        return self.area

class Line:
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2

    def length(self):
        x1, x2 = self.p1[0], self.p2[0]
        y1, y2 = self.p1[1], self.p2[1]
        d = (x1 - x2) ** 2 + (y1 - y2) ** 2
        d = math.sqrt(d)
        return d

if __name__ == "__main__":
    def give_intersect_full(seg1_start, seg1_end, seg2_start, seg2_end):
        m1 = (seg1_end[1] - seg1_start[1]) / (seg1_end[0] - seg1_start[0])
        b1 = seg1_end[1] - m1 * seg1_end[0]
        m2 = (seg2_end[1] - seg2_start[1]) / (seg2_end[0] - seg2_start[0])
        b2 = seg2_start[1] - m2 * seg2_start[0]

        if seg1_end[0] - seg1_start[0] == 0:
            point = [seg1_end[0], m2 * seg1_end[0] + b2]
        elif seg2_start[0] - seg2_end[0] == 0:
            point = [seg2_start[0], m1 * seg2_start[0] + b1]
        else:
            point_x = (b2 - b1) / (m1 - m2)
            point_y = m1 * point_x + b1
            point = [point_x, point_y]

        if (
            min(seg1_start[0], seg1_end[0]) <= point[0] <= max(seg1_start[0], seg1_end[0])
            and min(seg1_start[1], seg1_end[1]) <= point[1] <= max(seg1_start[1], seg1_end[1])
            and min(seg2_start[0], seg2_end[0]) <= point[0] <= max(seg2_start[0], seg2_end[0])
            and min(seg2_start[1], seg2_end[1]) <= point[1] <= max(seg2_start[1], seg2_end[1])
        ):
            return point
        else:
            return []


    center1 = tuple(map(float, input("Enter the center coordinates of circle 1 (x, y): ").split()))
    radius1 = float(input("Enter the radius of circle 1: "))
    circle1 = Circle(radius1, center1)

    center2 = tuple(map(float, input("Enter the center coordinates of circle 2 (x, y): ").split()))
    radius2 = float(input("Enter the radius of circle 2: "))
    circle2 = Circle(radius2, center2)

    distance = Line(circle1.center, circle2.center)
    if distance.length() == circle1.radius + circle2.radius:
        print("One collision point at", ((circle1.center[0] + circle2.center[0]) / 2, (circle1.center[1] + circle2.center[1]) / 2))
    elif (distance.length() > circle1.radius + circle2.radius) or (circle1.center==circle2.center and circle1.radius != circle2.radius):
        print("No collision occurs")
    elif circle1.center==circle2.center and circle1.radius==circle2.radius:
        print("infinity collisions")
    else:
        tet = [0]
        circle1_points = []
        circle2_points = []

        for i in range(1, 1002):
            tet.append(tet[i - 1] + math.pi / 1000)
            x, y = circle1.radius * np.cos(tet[i]), circle1.radius * np.sin(tet[i])
            x += circle1.center[0]
            y += circle1.center[1]
            circle1_points.append([x, y])

        for i in range(1, 1002):
            tet.append(tet[i - 1] + math.pi / 1000)
            x, y = circle2.radius * np.cos(tet[i]), circle2.radius * np.sin(tet[i])
            x += circle2.center[0]
            y += circle2.center[1]
            circle2_points.append([x, y])

        circle1_lines = []
        circle2_lines = []

        for i in range(len(circle1_points) - 1):
            p1 = tuple(circle1_points[i])
            p2 = tuple(circle1_points[i + 1])
            circle1_lines.append(Line(p1, p2))

        for i in range(len(circle2_points) - 1):
            p1 = tuple(circle2_points[i])
            p2 = tuple(circle2_points[i + 1])
            circle2_lines.append(Line(p1, p2))


        colliding_lines = []
        intersect_points=[]

        for line1, line2 in combinations(circle1_lines + circle2_lines, 2):
            point = give_intersect_full(line1.p1, line1.p2, line2.p1, line2.p2)
            if point:
                intersect_points.append(point)
                if len(intersect_points) == 2:
                    break
        
        kcount = 0 
        print("Two collisions occur at" )
        for point in intersect_points:
            print(point)
            if kcount==0:
                kia = point
            else:
                par = point
            
            kcount = kcount+1 


pi = np.pi
tet = np.arange(0,2*pi,0.05)
print(kia)
print(par)
x_values = circle1.center[0] + circle1.radius*np.sin(tet)
y_values = circle1.center[1] + circle1.radius*np.cos(tet)
plt.scatter(x_values, y_values, color='blue')
plt.axis('equal')
x_values = circle2.center[0] + circle2.radius*np.sin(tet)
y_values = circle2.center[1] + circle2.radius*np.cos(tet)
plt.scatter(x_values, y_values, color='red')
plt.scatter(kia[0],kia[1], color='green')
plt.scatter(par[0],par[1], color='green')

# plt.scatter(intersect_points[0,0],intersect_points[0,1], color='green')
# plt.scatter(intersect_points[1,0],intersect_points[1,1], color='green')
# # Optional: You can add labels and customize the plot
# plt.title('Plotting Multiple Points')
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')

# Display the plot
plt.grid(True) # Optional: Add a grid
plt.axhline(0, color='black',linewidth=0.5) # Optional: Add x and y axis lines
plt.axvline(0, color='black',linewidth=0.5)
plt.show()
