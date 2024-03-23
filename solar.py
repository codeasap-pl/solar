# Animation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# std lib
import abc


RND = np.random.random


def xrot(theta: int | float) -> np.matrix:
    """Returns rotation matrix for x-axis.

    Arguments:
    theta       - angle
    """
    return np.matrix([[1, 0            , 0             ],    # noqa: E202, E203
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta),  np.cos(theta)]])


def yrot(theta: int | float) -> np.matrix:
    """Returns rotation matrix for y-axis.

    Arguments:
    theta       - angle
    """
    return np.matrix([[np.cos(theta),  0, np.sin(theta)],
                      [0            ,  1, 0            ],    # noqa: E202, E203
                      [-np.sin(theta), 0, np.cos(theta)]])


def zrot(theta: int | float) -> np.matrix:
    """Returns rotation matrix for z-axis.

    Arguments:
    theta       - angle
    """
    return np.matrix([[np.cos(theta), -np.sin(theta), 0 ],   # noqa: E202, E203
                      [np.sin(theta),  np.cos(theta), 0 ],   # noqa: E202, E203
                      [0            ,  0            , 1 ]])  # noqa: E202, E203


class _Shape:
    ...


class Ellipse(_Shape):
    """TODO: elipse (currently a circle)"""

    def __init__(self,
                 *,
                 radius: int | float = 1,
                 precision: int = 64,
                 rotation: tuple | list = (0, 0, 0),
                 center: tuple | list = (0, 0, 0)):
        """Orbit (circle) initializer:

        TODO: elipse.
        """
        r = radius
        a, b, c = center
        h_space = np.zeros(precision)
        v_space = np.linspace(-np.pi, np.pi, precision)

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

        self._xyz = np.array(data)

    @property
    def xyz(self) -> np.ndarray:
        return self._xyz


class Orbit(Ellipse):
    ...


class Planet:
    def __init__(self,
                 *,
                 orbit: Orbit | dict,
                 name: str = "",
                 symbol: str = ""):
        self.name = name
        self.symbol = symbol
        self.orbit = orbit if isinstance(orbit, Orbit) else Orbit(**orbit)
        self.mpl_handle = None

    def get_xyz(self, t: int = 0) -> tuple:
        """Position on the orbit in 't' instance/frame of time"""
        x, y, z = self.orbit.xyz
        return (x[t], y[t], z[t])


class _Object(abc.ABC):
    @abc.abstractmethod
    def render(self, ax, *args, **kwargs) -> None:
        ...


class _Scene(_Object):
    """Scene"""


class MainScene(_Scene):
    """MainScene"""

    def __init__(self,
                 *,
                 center: tuple | list = (0, 0, 0),
                 radius: int | float = 1):
        self.center = center
        self.radius = radius

    def render(self, ax, *args, **kwargs) -> None:
        self._plot_axes(ax)

    def _plot_axes(self, ax):
        """Axis Mundi"""
        a, b, c, r = [*self.center, self.radius]
        n = 100
        zeros = np.zeros(n)
        (x, y, z) = (zeros + a, zeros + b, zeros + c)
        line = np.linspace(-r, r, n)

        ax.plot(line + a, y, z, color="r", alpha=0.2)
        ax.plot(x, line + b, z, color="g", alpha=0.2)
        ax.plot(x, y, line + c, color="b", alpha=0.2)

        ax.set_xlabel("X", color="r", fontweight="bold")
        ax.set_ylabel("Y", color="g", fontweight="bold")
        ax.set_zlabel("Z", color="b", fontweight="bold")


class Sphere(_Object):
    ...


class Universe(Sphere):
    """As conjectured and proven"""

    def __init__(self, planets, center, radius=1, prec=64, **po):
        """
        """
        self.planets = planets
        self.center = center
        self.radius = radius
        self.prec = prec
        self.po = po

    def mpl_play(self, frame_no, scene, controls, n_frames, **kwargs):
        """Invoked by matplotlib (animation function, frame by frame)"""
        controls["title"].set_text("Solar, t=%d" % frame_no)
        for name, p in self.planets.items():
            x, y, z = p.get_xyz(frame_no)
            p.mpl_handle.set_data([x], [y])
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

    def render(self, ax, *args, **kwargs) -> None:
        a, b, c = self.center
        r = self.radius
        prec = self.prec

        self._plot_surface(ax, a, b, c, r, prec)
        self._plot_meridians(ax, 8, a, b, c, r, prec)
        self._plot_sun(ax, a, b, c)
        self._plot_planets(ax)

    def _plot_surface(self, ax, a, b, c, r, prec) -> None:
        v = np.linspace(0, 2 * np.pi, prec)
        u = np.linspace(0, np.pi, prec)
        x = np.outer(np.cos(u), np.sin(v)) * r + a
        y = np.outer(np.sin(u), np.sin(v)) * r + b
        z = np.outer(np.ones(np.size(u)), np.cos(v)) * r + c

        ax.plot_surface(x, y, z, color="white", alpha=0.05)

    def _plot_sun(self, ax, a=0, b=0, c=0):
        # The SUN.
        ax.scatter([a], [b], [c], color="orange", alpha=0.4, linewidth=10)

    def _plot_planets(self, ax):
        for name, planet in self.planets.items():
            # Orbits
            ax.plot(*planet.orbit.xyz, alpha=0.2)
            # Planets
            handle = ax.plot(*planet.get_xyz(), marker="o", label=name)[0]
            self.planets[name].mpl_handle = handle

    def _plot_meridians(self, ax, total, a, b, c, r, prec):
        angle = (np.pi / total)
        meridians = [
            Orbit(
                center=[a, b, c],
                radius=r,
                rotation=[0, 0, angle * i],
                precision=prec,
            )
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
        "Ἑρμῆς": {
            "symbol": "☿",
            "orbit": {
                "radius": 0.387098,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Ἀφροδίτη": {
            "orbit": {
                "radius": 0.723332,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Γαῖα": {
            "orbit": {
                "radius": 1,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Ἄρης": {
            "orbit": {
                "radius": 1.3814,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Ζεύς": {
            "orbit": {
                "radius": 5.2038,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Κρόνος": {
            "orbit": {
                "radius": 9.5826,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Οὐρανός": {
            "orbit": {
                "radius": 19.19126,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Ποσειδῶν": {
            "orbit": {
                "radius": 30.07,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
        "Ἅιδης": {
            "orbit": {
                "radius": 39.482,
                "center": [0, 0, 0],
                "precision": precision,
            },
        },
    }

    planets = {
        name: Planet(
            # orbit_theta=np.random.uniform(-np.pi / 8, np.pi / 2, 3),
            **p,
        )
        for name, p in planets.items()
    }

    plt.figure(figsize=(16, 9))
    ax = plt.axes(projection="3d")
    ax.set_box_aspect(aspect=(1, 1, 1))
    ax.axis("on" if po.show_axis else "off")

    fig_main = plt.gcf()

    # Main SCENE
    ax_main = fig_main.gca()

    scene_main = MainScene(radius=1, center=[0, 0, 0])
    scene_main.render(ax_main)

    # Universe
    universe = Universe(
        planets=planets,
        center=[0, 0, 0],
        radius=42,
        **po.__dict__,
    )

    universe.render(ax_main)

    controls = dict(
        title=ax.set_title("Solar")
    )

    n_frames = precision

    ani = animation.FuncAnimation(
        plt.gcf(),
        universe.mpl_play,
        precision,
        fargs=(universe, controls, n_frames),
        interval=(1000 / fps),
        blit=True,
    )

    plt.legend(loc="upper right")

    if po.save_mp4:
        writer = animation.FFMpegWriter()
        ani.save("solar.mp4", writer=writer)
    else:
        plt.show()
