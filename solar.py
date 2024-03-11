import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


RND = np.random.random


def xrot(theta):
    return np.matrix([[1, 0            , 0             ],    # noqa: E202, E203
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta),  np.cos(theta)]])


def yrot(theta):
    return np.matrix([[np.cos(theta),  0, np.sin(theta)],
                      [0            ,  1, 0            ],    # noqa: E202, E203
                      [-np.sin(theta), 0, np.cos(theta)]])


def zrot(theta):
    return np.matrix([[np.cos(theta), -np.sin(theta), 0 ],   # noqa: E202, E203
                      [np.sin(theta),  np.cos(theta), 0 ],   # noqa: E202, E203
                      [0            ,  0            , 1 ]])  # noqa: E202, E203


class Orbit:
    def __init__(self, a, b, c, r, rotation, prec):
        h_space = np.zeros(prec)
        v_space = np.linspace(-np.pi, np.pi, prec)

        x = r * (np.sin(v_space) * np.cos(h_space)) + a
        y = r * (np.sin(v_space) * np.sin(h_space)) + b
        z = r * (np.cos(v_space)) + c

        data = [x, y, z]
        rx, ry, rz = (rotation if np.any(rotation) else [0, 0, 0])
        if rx:
            data = xrot(rx) * data
        if ry:
            data = yrot(ry) * data
        if rz:
            data = zrot(rz) * data

        self.xyz = np.array(data)


class Planet:
    def __init__(self,
                 r,
                 rotation,
                 precision=64,
                 name=None):
        self.name = name
        self.r = r
        self.orbit = Orbit(0, 0, 0, r, rotation, precision)
        self.mpl_handle = None

    def get_xyz(self, t=0):
        x, y, z = self.orbit.xyz
        return (x[t], y[t], z[t])


class Scene:
    def __init__(self, a, b, c, r):
        self.a = a
        self.b = b
        self.c = c
        self.radius = r

        self.fig = plt.gcf()
        self.ax = self.fig.gca()

    def plot_axes(self):
        """Axis Mundi"""
        a, b, c, r = [self.a, self.b, self.c, self.radius]
        n = 100
        zeros = np.zeros(n)
        (x, y, z) = (zeros + a, zeros + b, zeros + c)
        line = np.linspace(-r, r, n)

        self.ax.plot(line + a, y, z, color="r", alpha=0.2)
        self.ax.plot(x, line + b, z, color="g", alpha=0.2)
        self.ax.plot(x, y, line + c, color="b", alpha=0.2)

        self.ax.set_xlabel("X", color="r", fontweight="bold")
        self.ax.set_ylabel("Y", color="g", fontweight="bold")
        self.ax.set_zlabel("Z", color="b", fontweight="bold")


class Sphere:
    def __init__(self, ax, planets, center, radius=1, prec=64, **po):
        self.ax = ax
        self.planets = planets
        self.center = center
        self.radius = radius
        self.prec = prec
        self.po = po

    def play(self, frame_no, scene, controls, n_frames, **kwargs):
        controls["title"].set_text("Solar, t=%d" % frame_no)
        for name, p in self.planets.items():
            x, y, z = p.get_xyz(frame_no)
            p.mpl_handle.set_data([x, y])
            p.mpl_handle.set_3d_properties(z)
            if self.po.get("verbose"):
                print(
                    "t=%03d %12s: %.8f %.8f %.8f" % (
                        frame_no, p.name, x, y, z
                    )
                )

        return tuple([
            *controls.values(),
            *[p.mpl_handle for p in self.planets.values()]
        ])

    def plot(self):
        a, b, c = self.center
        r = self.radius
        prec = self.prec

        v = np.linspace(0, 2 * np.pi, prec)
        u = np.linspace(0, np.pi, prec)
        x = np.outer(np.cos(u), np.sin(v)) * r + a
        y = np.outer(np.sin(u), np.sin(v)) * r + b
        z = np.outer(np.ones(np.size(u)), np.cos(v)) * r + c

        self.ax.plot_surface(x, y, z, color="white", alpha=0.05)
        self.plot_meridians(self.ax, 8, a, b, c, 1, prec)

        # The SUN.
        self.ax.scatter([0], [0], [0], color="orange", alpha=0.4, linewidth=10)

        for name, planet in self.planets.items():
            # Orbits
            self.ax.plot(*planet.orbit.xyz, alpha=0.2)
            # Planets
            handle = self.ax.plot(*planet.get_xyz(), marker="o", label=name)[0]
            self.planets[name].mpl_handle = handle

    def plot_meridians(self, ax, total, a, b, c, r, prec):
        angle = (np.pi / total)
        meridians = [
            Orbit(a, b, c, r, [0, 0, angle * i], prec)
            for i in range(0, total)
        ]

        for m in meridians:
            ax.plot(*m.xyz, color="gray", alpha=0.1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-A", "--show-axis", action="store_true")
    parser.add_argument("-S", "--save-mp4", action="store_true")
    parser.add_argument("-V", "--verbose", action="store_true")
    parser.add_argument("-p", "--precision", type=int, default=64)
    parser.add_argument("-f", "--fps", type=int, default=24)

    po = parser.parse_args()

    precision = po.precision
    fps = po.fps

    # Planet caravan.

    planets = {
        "Ἑρμῆς": dict(),
        "Ἀφροδίτη": dict(),
        "Γαῖα": dict(),
        "Ἄρης": dict(),
        "Ζεύς": dict(),
        "Κρόνος": dict(),
        "Οὐρανός": dict(),
        "Ποσειδῶν": dict(),
        "Ἅιδης": dict(),
    }

    # fixed radius: to be removed
    for idx, _P in enumerate(planets.items(), 1):
        name, p = _P
        p["r"] = idx / len(planets)

    planets = {
        name: Planet(
            r=p["r"],
            rotation=np.random.uniform(-np.pi / 8, np.pi / 2, 3),
            precision=precision,
            name=name,
        )
        for name, p in planets.items()
    }

    plt.figure(figsize=(16, 9))
    ax = plt.axes(projection="3d")
    ax.set_box_aspect(aspect=(1, 1, 1))
    ax.axis("on" if po.show_axis else "off")

    # SCENE
    scene = Scene(0, 0, 0, 1)
    scene.plot_axes()

    # SPHERE
    sphere = Sphere(scene.ax, planets, [0, 0, 0], 1, precision, **po.__dict__)
    sphere.plot()

    controls = dict(
        title=ax.set_title("Solar")
    )

    n_frames = precision

    ani = animation.FuncAnimation(
        plt.gcf(),
        sphere.play,
        precision,
        fargs=(scene, controls, n_frames),
        interval=(1000 / fps),
        blit=True,
    )

    plt.legend(loc="upper right")

    if po.save_mp4:
        writer = animation.FFMpegWriter()
        ani.save("solar.mp4", writer=writer)
    else:
        plt.show()
