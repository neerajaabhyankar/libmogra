import os
import numpy as np
import plotly.graph_objects as go
import itertools
import pickle
from typing import List, Dict, Tuple, Optional

from libmogra.datatypes import (
    normalize_frequency,
    ratio_to_swar,
    ratio_to_swarval,
    Swar,
)


""" style guide + color palette """

DOT_SIZE = 21
DOT_LABEL_SIZE = 13
ANNOTATION_OFFSET = 0.5
FIG_WIDTH = 800
FIG_HEIGHT = 550
FIG_MARGIN = dict(l=60, r=40, t=40, b=150)
FIG_SCALE = 1

NODE_ORANGE = "#f08b65"
NODE_YELLOW = "#f4c05b"
NODE_GREY = "#323539"
NODE_PURPLE = lambda x: f"#{int(70+min(0,-x)*120)}20{int(70+min(0,x)*120)}"

LIGHT_GREY = "#dcd8cf"
BG_GREY = "#f3f3f3"
WRONG_RED = "#a83232"
ANNOTATION_GREEN = "#3e7a32"


""" shruti data """

GT_GENUS = [3, 3, 3, 3, 5, 5]
GT_NODES = pickle.load(
    open(
        os.path.join(os.path.dirname(__file__), "shrutidata/hypothesized_gt_3_5.pkl"),
        "rb",
    )
)


class EFGenus:
    """
    An N-dimensional bounded tonnetz net can be initialized with
    N prime numbers and their maximum allowable powers,
    i.e. an Euler-Fokker Genus https://en.wikipedia.org/wiki/Euler%E2%80%93Fokker_genus
    """

    def __init__(self, primes=[3, 5, 7], powers=[0, 0, 0]) -> None:
        self.primes = primes
        self.powers = powers

    @classmethod
    def from_list(cls, genus_list: List):
        primes = []
        powers = []
        for new_prime in genus_list:
            if len(primes) > 0:
                assert new_prime >= primes[-1]
                if new_prime == primes[-1]:
                    powers[-1] += 1
                else:
                    primes.append(new_prime)
                    powers.append(1)
            else:
                primes.append(new_prime)
                powers.append(1)

        return cls(primes, powers)


class Tonnetz:
    def __init__(self, genus=EFGenus.from_list(GT_GENUS)) -> None:
        if len(genus.primes) > 3:
            print("cannot handle more than 3 dimensions")
            return

        self.primes = genus.primes
        self.powers = genus.powers

        ranges = []
        for prime, power in zip(genus.primes, genus.powers):
            ranges.append(range(-power, power + 1))
        self.node_coordinates = list(itertools.product(*ranges))

        self.assign_coords3d()
        self.assign_notes()

    def coord_to_frequency(self, coords):
        ff = 1
        for ii, cc in enumerate(coords):
            ff *= self.primes[ii] ** cc
        return ff

    def assign_coords3d(self):
        coords = list(zip(*self.node_coordinates))
        # Coordinates for Plotly Scatter3d
        self.coords3d = {i: [0] * len(self.node_coordinates) for i in range(3)}
        for i, coords in enumerate(coords):
            if i < len(coords):
                self.coords3d[i] = coords

    def assign_notes(self):
        self.node_frequencies = [
            normalize_frequency(self.coord_to_frequency(nc))
            for nc in self.node_coordinates
        ]
        self.node_names = [ratio_to_swar(nf) for nf in self.node_frequencies]

    def get_swar_options(self, swar):
        swar_node_indices = [nn == swar for nn in self.node_names]
        swar_node_coordinates = np.array(self.node_coordinates)[swar_node_indices]
        return [tuple(nc) for nc in swar_node_coordinates.tolist()], self.primes

    def get_neighbors(self, node: List):
        neighbor_indices = []
        for ii, nc in enumerate(self.node_coordinates):
            if sum(abs(np.array(nc) - np.array(node))) == 1:
                neighbor_indices.append(ii)
        return neighbor_indices, [self.node_coordinates[ii] for ii in neighbor_indices]

    def adjacency_matrix(self):
        """
        len(nodes) x len(nodes) matrix; represents geometric lattice
        """
        mat = np.zeros(
            (len(self.node_coordinates), len(self.node_coordinates)), dtype=int
        )
        for ii, nc in enumerate(self.node_coordinates):
            nb_indices, _ = self.get_neighbors(nc)
            for jj in nb_indices:
                mat[ii, jj] = 1
        return mat

    def equivalence_matrix(tn):
        """
        len(nodes) x 12 matrix; for each swar column, nodes (swar options) for that swar are 1
        """
        mat = np.zeros((len(tn.node_coordinates), 12), dtype=int)
        for ss in range(12):
            swar = Swar(ss).name
            swar_node_indices = [nn == swar for nn in tn.node_names]
            for jj in np.where(swar_node_indices)[0]:
                mat[jj, ss] = 1
        return mat

    def plot_raag(self, raag_name) -> Optional[go.Figure]:
        if raag_name not in GT_NODES:
            print("cannot find tonnetz diagram for", raag_name)
            return None

        raag_nodes = GT_NODES[raag_name]

        def node_purple(coord):
            swarval = ratio_to_swarval(
                normalize_frequency(self.coord_to_frequency(coord))
            )
            return NODE_PURPLE(swarval - round(swarval))

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=self.coords3d[0],
                    y=self.coords3d[1],
                    mode="text+markers",
                    marker=dict(
                        size=DOT_SIZE,
                        symbol="circle",
                        color=[
                            node_purple(coord) if coord in raag_nodes else NODE_ORANGE
                            for coord in self.node_coordinates
                        ],
                    ),
                    text=self.node_names,
                    textposition="middle center",
                    textfont=dict(
                        family="Overpass", size=DOT_LABEL_SIZE, color="white"
                    ),
                )
            ]
        )

        # axes
        fig.update_layout(
            title=f"raag {raag_name}",
            xaxis_title=f"powers of {self.primes[0]}",
            yaxis_title=f"powers of {self.primes[1]}",
            plot_bgcolor=BG_GREY,
            width=FIG_WIDTH,
            height=FIG_HEIGHT,
        )
        fig.update_xaxes(tickvals=np.arange(-self.powers[0], self.powers[0] + 1))
        fig.update_yaxes(tickvals=np.arange(-self.powers[1], self.powers[1] + 1))
        fig.update_layout(margin=FIG_MARGIN)

        fig.add_annotation(
            text="Note: m = shuddha, M = teevra",
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="top",
            x=0.05,
            y=-0.2,
            showarrow=False,
            font=dict(size=DOT_LABEL_SIZE - 2),
        )
        fig.add_annotation(
            text="Disclaimer: The selection of these shrutis is merely a hypothesis based on my limited knowledge and reading.",
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="top",
            x=0.05,
            y=-0.28,
            showarrow=False,
            font=dict(size=DOT_LABEL_SIZE - 2),
        )
        fig.add_annotation(
            text="Please use this as a mere guidance for visualization.",
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="top",
            x=0.05,
            y=-0.33,
            showarrow=False,
            font=dict(size=DOT_LABEL_SIZE - 2),
        )

        # fig.write_image(f"images/raag_{raag.lower()}.png", scale=FIG_SCALE)
        # fig.show(scale=FIG_SCALE)
        return fig
