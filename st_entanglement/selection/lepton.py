# coding: utf-8

"""
Lepton selection methods.
"""

from __future__ import annotations

from columnflow.selection import Selector, selector
from columnflow.util import maybe_import

ak = maybe_import("awkward")


@selector(
    uses={"nElectron", "Electron.{pt,eta,mvaFall17V2Iso_WP80}"},
    exposed=False,
)
def electron_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, ak.Array, ak.Array]:
    """
    Electron selection returning analysis, control and veto masks.

    The current analysis-level electron definition is:
    - exactly one reconstructed electron in the event
    - electron pt < 27 GeV
    - abs(eta) < 2.1
    - passes mvaFall17V2Iso_WP80

    See https://twiki.cern.ch/twiki/bin/view/CMS/EgammaNanoAOD?rev=42 for more details on the electron ID working point.
    """

    selected_electron_mask = (
        (events.Electron.pt < 27.0) &
        (abs(events.Electron.eta) < 2.1) &
        (events.Electron.mvaFall17V2Iso_WP80 == 1)
    )
    exactly_one_electron = events.nElectron == 1

    analysis_mask = selected_electron_mask & exactly_one_electron
    control_mask = analysis_mask
    veto_mask = analysis_mask

    return analysis_mask, control_mask, veto_mask


@selector(
    uses={"nMuon", "Muon.{pt,eta,tightId,pfRelIso04_all}"},
    exposed=False,
)
def muon_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, ak.Array, ak.Array]:
    """
    Muon selection returning analysis, control and veto masks.

    The analysis-level muon definition is:
    - exactly one reconstructed muon in the event
    - muon pt > 24 GeV
    - abs(eta) < 2.1
    - passes tight ID

    References:

    - Isolation working point: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2?rev=59
    - ID und ISO : https://twiki.cern.ch/twiki/bin/view/CMS/MuonUL2017?rev=15
    """

    selected_muon_mask = (
        (events.Muon.pt > 24.0) &
        (abs(events.Muon.eta) < 2.1) &
        (events.Muon.tightId == 1) &
        (events.Muon.pfRelIso04_all < 0.15)
    )
    exactly_one_muon = events.nMuon == 1

    analysis_mask = selected_muon_mask & exactly_one_muon
    control_mask = analysis_mask
    veto_mask = analysis_mask

    return analysis_mask, control_mask, veto_mask
