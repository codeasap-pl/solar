import matplotlib.pyplot as plt

Ex = 1
Ey = 1

Sx = 0
Sy = 0

xlim = [-5, 5]
ylim = [-5, 5]

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
plt.scatter([Ex], [Ey])
plt.scatter([Sx], [Sy], color="orange")
plt.savefig("points.png")
# plt.show()
