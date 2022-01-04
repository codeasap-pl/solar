import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation


π = math.pi

xlim = [-3, 3]
ylim = [-3, 3]

ax = plt.gca()
ax.set_aspect("equal")

ax.set_xlim(*xlim)
ax.set_ylim(*ylim)

spines = ax.spines
spines["left"].set_position("zero")
spines["bottom"].set_position("zero")

spines["top"].set_color("none")
spines["right"].set_color("none")


xticks = list(range(xlim[0], xlim[1] + 1, 1))
yticks = list(range(xlim[0], xlim[1] + 1, 1))

ax.set_xticks(xticks)
ax.set_yticks(yticks)

plt.grid(True, alpha=0.5)
plt.tight_layout()


def update(frame_no, timeline, objects):
    Earth = objects["E"]
    Sun = objects["S"]

    ex, ey = Earth["coords"]
    r = Earth["orbit_radius"]
    Earth["coords"] = [
        r * math.sin(timeline[frame_no]),  # * math.cos(ex),
        r * math.cos(timeline[frame_no])
    ]

    # Panta Rhei.
    sx, sy = Sun["coords"]
    r = Sun["orbit_radius"]
    Sun["coords"] = [
        r * math.sin(timeline[frame_no]),  # * math.cos(sx),
        r * math.cos(timeline[frame_no])
    ]

    Sun["handle"].set_data(*Sun["coords"])
    Earth["handle"].set_data(*Earth["coords"])

    handles = [o["handle"] for o in objects.values()]
    return handles


objects = {
    "E": {
        "coords": [1, 1],
        "orbit_radius": 1,
        "color": "blue",  # Pale Blue Dot.
        "handle": None,
    },
    "S": {
        "coords": [0, 0],
        "orbit_radius": 0.03,
        "handle": None,
        "color": "orange",
    }
}


E = objects["E"]
S = objects["S"]

E["handle"], = ax.plot(*E["coords"], color=E["color"], marker="o")
S["handle"], = ax.plot(*S["coords"], color=S["color"], marker="o")

n_frames = 32
timeline_step = (2 * π) / n_frames
timeline = [-π + (timeline_step * i) for i in range(n_frames)]

ani = animation.FuncAnimation(
    plt.gcf(),
    update,
    n_frames,
    fargs=(timeline, objects),
    interval=(1000 / 25),
    blit=True,
)

plt.show()
