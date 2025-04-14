class Sphere:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.classname = "Sphere"

class Torus:
    def __init__(self, x, y, z, inRadius, outRadius):
        self.x = x
        self.y = y
        self.z = z
        self.inRadius = inRadius
        self.outRadius = outRadius
        self.classname = "Torus"

def local(bodies, argv):
    # print(bodies)
    print(
        f"Rock thrown at the point ({float(argv[3])}, {float(argv[4])}, {float(argv[5])}) "
        f"and parallel to the vector ({float(argv[6])}, {float(argv[7])}, {float(argv[8])})"
    )
