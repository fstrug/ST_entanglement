# coding: utf-8

"""
Exemplary selection methods.
"""

from columnflow.categorization import Categorizer, categorizer
from columnflow.util import maybe_import

ak = maybe_import("awkward")


#
# categorizer functions used by categories definitions
#

@categorizer(uses={"event"})
def cat_incl(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    # fully inclusive selection
    return events, ak.ones_like(events.event) == 1


@categorizer(uses={"Electron.pt", "Muon.pt"})
def cat_1e(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    # exactly one selected electron and no selected muons
    return events, (ak.num(events["Electron", "pt"], axis=1) == 1) & (ak.num(events["Muon", "pt"], axis=1) == 0)


@categorizer(uses={"Electron.pt", "Muon.pt"})
def cat_1mu(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    # exactly one selected muon and no selected electrons
    return events, (ak.num(events["Muon", "pt"], axis=1) == 1) & (ak.num(events["Electron", "pt"], axis=1) == 0)


@categorizer(uses={"Jet.pt"})
def cat_2j(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    # two or more jets
    return events, ak.num(events.Jet.pt, axis=1) >= 2
