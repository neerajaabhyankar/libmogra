import os
from fractions import Fraction
import numpy as np
import plotly.graph_objects as go
import itertools
import pickle
from sympy.ntheory import factorint
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


class TonnetzColorScheme:
    def __init__(self, theme="daylight"):
        self.annotation = "#8D8DA4"
        self.light_grey = "#dcd8cf"
        self.bg_grey = "#f3f3f3"
        if theme == "twilight":
            self.chord_major = "#F08B65"
            self.chord_minor = "#F4C05B"
            self.node_blank = "#A5A9BB"
            # assuming x in (-0.5, 0.5)
            self.node_color = (
                lambda x: f"#{int(70+min(0,-x)*120)}20{int(70+min(0,x)*120)}"
            )
        elif theme == "daylight":
            self.chord_major = "#BA8FAD"
            self.chord_minor = "#9B8DC7"
            self.node_blank = "#A5A9BB"
            # assuming x in (-0.5, 0.5)
            concf = lambda x: np.sqrt(abs(x) / 2) * np.sign(x)
            self.node_color = (
                lambda x: f"#{int(45-420*min(concf(x),0)-90*max(concf(x),0)):02x}99{int(45+90*min(concf(x),0)+420*max(concf(x),0)):02x}"
            )
        else:
            raise ValueError(f"unknown theme: {theme}")


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
        """
        Initializes the genus from a non-decreasing list of prime numbers.
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
        self.node_coordinates: np.ndarray[Tuple] = np.array(
            list(itertools.product(*ranges))
        )

        self.assign_notes()
        self.color_scheme = TonnetzColorScheme()

    def set_color_scheme(self, theme):
        self.color_scheme = TonnetzColorScheme(theme)

    def coord_to_ratio(self, coords) -> Fraction:
        """
        Given a coordinate in the tonnetz net, find
        the octave-normalized relative frequency ratio that it represents.
        """
        ff = Fraction(1)
        for ii, cc in enumerate(coords):
            if cc >= 0:
                ff *= self.primes[ii] ** cc
            else:
                ff /= self.primes[ii] ** (-cc)
        return normalize_frequency(ff)

    def ratio_to_coord(self, ratio: Fraction) -> Tuple:
        """
        Given a frequency ratio, if comprised of the primes in the tonnetz,
        find the coordinate in the tonnetz net that it corresponds to.
        """
        ratio = Fraction(ratio)
        coord = [
            0,
        ] * len(self.primes)

        for kk, vv in factorint(ratio.numerator).items():
            if kk == 2:
                continue
            if kk not in self.primes:
                return ValueError(
                    "ratio includes prime factors not in the tonnetz genus"
                )
            coord[self.primes.index(kk)] += vv

        for kk, vv in factorint(ratio.denominator).items():
            if kk == 2:
                continue
            if kk not in self.primes:
                return ValueError(
                    "ratio includes prime factors not in the tonnetz genus"
                )
            coord[self.primes.index(kk)] -= vv

        return tuple(coord)

    def assign_notes(self):
        self.node_ratios: np.ndarray[Fraction] = np.array(
            [self.coord_to_ratio(nc) for nc in self.node_coordinates]
        )
        self.node_names: np.ndarray[str] = np.array(
            [ratio_to_swar(nf) for nf in self.node_ratios]
        )

    def get_swar_options(self, swar) -> List[Tuple]:
        """
        Given a Swar, return a list of coordinates
        where the Swar appears in this Tonnetz net
        """
        swar_node_indices = [nn == swar for nn in self.node_names]
        swar_node_coordinates = self.node_coordinates[swar_node_indices]
        return [tuple(nc) for nc in swar_node_coordinates.tolist()]

    def get_neighbors(self, node: List) -> (List, List[Tuple]):
        """
        Indices in the self.node_coordinates list
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
            swar_node_indices = np.array([nn == swar for nn in tn.node_names])
            for jj in np.where(swar_node_indices)[0]:
                mat[jj, ss] = 1
        return mat

    def get_node_color(self, coord):
        """
        Gives a warmer color for tones lower than the corresponding ET tone,
        and a cooler color for tones higher than the corresponding ET tone.
        The color is a shade of purple, with the hue determined by the distance
        """
        swarval = ratio_to_swarval(self.coord_to_ratio(coord))
        return self.color_scheme.node_color(swarval - round(swarval))

    def plot_raag(
        self, raag_name, show_ratios=True, show_chords=False, theme="daylight"
    ) -> Optional[go.Figure]:
        """
        Returns a figure based on the Ground Truth dataset
        """
        assert self.primes == list(
            set(GT_GENUS)
        ), "raags undefined for the current genus"
        assert self.powers == [
            GT_GENUS.count(p) for p in self.primes
        ], "raags undefined for the current genus"

        if raag_name not in GT_NODES:
            print("cannot find tonnetz diagram for", raag_name)
            return None

        raag_nodes = GT_NODES[raag_name]
        self.set_color_scheme(theme)

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
                            (
                                self.get_node_color(coord)
                                if tuple(coord) in raag_nodes
                                else self.color_scheme.node_blank
                            )
                            for coord in self.node_coordinates
                        ],
                    ),
                    text=self.node_names,
                    textposition="middle center",
                    textfont=dict(size=DOT_LABEL_SIZE, color="white"),
                    showlegend=False,
                    hovertemplate="(%{x}, %{y})<br>%{text}<extra></extra>",
                ),
            ]
        )

        if show_chords and show_ratios:
            print("cannot show both ratios and chords; only showing ratios")
            show_chords = False

        # ratios
        if show_ratios:
            fig.add_trace(
                go.Scatter(
                    x=[nc[0] + ANNOTATION_OFFSET_X for nc in self.node_coordinates],
                    y=[nc[1] + ANNOTATION_OFFSET_Y for nc in self.node_coordinates],
                    mode="text",
                    text=[str(nr) for nr in self.node_ratios],
                    textposition="middle center",
                    textfont=dict(
                        size=0.75 * DOT_LABEL_SIZE, color=self.color_scheme.annotation
                    ),
                    showlegend=False,
                )
            )

        # chords
        if show_chords:
            ao = 0.7 * ANNOTATION_OFFSET_Y
            aot = 1 - 1.4 * ANNOTATION_OFFSET_Y

            # major triads
            # draw triangles between (ii,jj), (ii+1,jj), (jj+1,ii)
            max_ii = max([ii for ii, _ in self.node_coordinates])
            max_jj = max([jj for _, jj in self.node_coordinates])
            for ii, jj in self.node_coordinates:
                if ii >= max_ii or jj >= max_jj:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=[ii + ao, ii + aot, ii + ao, ii + ao],
                        y=[jj + ao, jj + ao, jj + aot, jj + ao],
                        mode="lines",
                        line=dict(color=self.color_scheme.chord_major, width=2),
                        fill="toself",
                        fillcolor=self.color_scheme.chord_major,
                        showlegend=False,
                        hoverinfo="none",
                    )
                )

            # minor triads
            # draw triangles between (ii,jj), (ii-1,jj), (jj-1,ii)
            min_ii = min([ii for ii, _ in self.node_coordinates])
            min_jj = min([jj for _, jj in self.node_coordinates])
            for ii, jj in self.node_coordinates:
                if ii == min_ii or jj == min_jj:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=[ii - ao, ii - aot, ii - ao, ii - ao],
                        y=[jj - ao, jj - ao, jj - aot, jj - ao],
                        mode="lines",
                        line=dict(color=self.color_scheme.chord_minor, width=2),
                        fill="toself",
                        fillcolor=self.color_scheme.chord_minor,
                        showlegend=False,
                        hoverinfo="none",
                    )
                )

        # axes
        fig.update_layout(
            title=f"raag {raag_name}",
            xaxis_title=f"powers of {self.primes[0]}",
            yaxis_title=f"powers of {self.primes[1]}",
            plot_bgcolor=self.color_scheme.bg_grey,
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
