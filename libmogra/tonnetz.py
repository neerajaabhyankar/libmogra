import os
from fractions import Fraction
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
ANNOTATION_OFFSET_X = 0.25
ANNOTATION_OFFSET_Y = 0.2
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
        assert len(primes) == len(
            powers
        ), "the number of primes should match the number of corresponding specified powers"
        self.primes = primes
        self.powers = powers

    @classmethod
    def from_list(cls, genus_list: List):
        """Initializes the genus from a non-decreasing list of prime numbers.
        The number of occurences of a prime number in this list = the max allowable power of that prime.
        """
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

        self.primes: List = genus.primes
        self.powers: List = genus.powers

        ranges = []
        for prime, power in zip(genus.primes, genus.powers):
            ranges.append(range(-power, power + 1))
        self.node_coordinates: List[Tuple] = list(itertools.product(*ranges))

        # self.assign_coords3d()  # deprecated
        self.assign_notes()

    def coord_to_ratio(self, coords) -> Fraction:
        """Given a coordinate in the tonnetz net, find
        the octave-normalized relative frequency ratio that it represents.
        """
        ff = Fraction(1)
        for ii, cc in enumerate(coords):
            if cc >= 0:
                ff *= self.primes[ii] ** cc
            else:
                ff /= self.primes[ii] ** (-cc)
        return normalize_frequency(ff)

    # def assign_coords3d(self):
    #     """ TODO(neeraja): remove redundant variable"""
    #     coords = list(zip(*self.node_coordinates))
    #     # Coordinates for Plotly Scatter3d
    #     self.coords3d = {i: [0] * len(self.node_coordinates) for i in range(3)}
    #     for i, coords in enumerate(coords):
    #         if i < len(coords):
    #             self.coords3d[i] = coords

    def assign_notes(self):
        self.node_ratios: List[Fraction] = [
            self.coord_to_ratio(nc) for nc in self.node_coordinates
        ]
        self.node_names: List[str] = [ratio_to_swar(nf) for nf in self.node_ratios]

    def get_swar_options(self, swar) -> List[Tuple]:
        """Given a Swar, return a list of coordinates
        where the Swar appears in this Tonnetz net
        """
        swar_node_indices = [nn == swar for nn in self.node_names]
        swar_node_coordinates = np.array(self.node_coordinates)[swar_node_indices]
        return [tuple(nc) for nc in swar_node_coordinates.tolist()], self.primes

    def get_neighbors(self, node: List) -> (List, List[Tuple]):
        """Indices in the self.node_coordinates list
        and coordinates in the net
        of neighbors of a given node
        """
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
            swarval = ratio_to_swarval(self.coord_to_ratio(coord))
            return NODE_PURPLE(swarval - round(swarval))

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=[nc[0] for nc in self.node_coordinates],
                    y=[nc[1] for nc in self.node_coordinates],
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
                    textfont=dict(size=DOT_LABEL_SIZE, color="white"),
                    showlegend=False,
                ),
                # ratios
                go.Scatter(
                    x=[nc[0] + ANNOTATION_OFFSET_X for nc in self.node_coordinates],
                    y=[nc[1] + ANNOTATION_OFFSET_Y for nc in self.node_coordinates],
                    mode="text",
                    text=[str(nr) for nr in self.node_ratios],
                    textposition="middle center",
                    textfont=dict(size=0.75 * DOT_LABEL_SIZE, color=ANNOTATION_GREEN),
                    showlegend=False,
                ),
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
