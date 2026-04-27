# coding: utf-8

"""
Preselection methods for the ST entanglement analysis.
"""

from collections import defaultdict

from columnflow.selection import Selector, SelectionResult, selector
from columnflow.selection.stats import increment_stats
from columnflow.columnar_util import sorted_indices_from_mask
from columnflow.production.processes import process_ids
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.util import maybe_import

from st_entanglement.production.example import cutflow_features

ak = maybe_import("awkward")


@selector(
    uses={"Muon.{pt,eta,phi,mass}"},
)
def muon_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    muon_mask = (events.Muon.pt >= 20.0) & (abs(events.Muon.eta) < 2.1)
    muon_sel = ak.sum(muon_mask, axis=1) == 1

    return events, SelectionResult(
        steps={
            "muon": muon_sel,
        },
        objects={
            "Muon": {
                "Muon": muon_mask,
            },
        },
    )


@selector(
    uses={"Jet.{pt,eta,phi,mass}"},
)
def jet_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    jet_mask = (events.Jet.pt >= 25.0) & (abs(events.Jet.eta) < 2.4)
    jet_sel = ak.sum(jet_mask, axis=1) >= 1

    return events, SelectionResult(
        steps={
            "jet": jet_sel,
        },
        objects={
            "Jet": {
                "Jet": sorted_indices_from_mask(jet_mask, events.Jet.pt, ascending=False),
            },
        },
        aux={
            "n_jets": ak.sum(jet_mask, axis=1),
        },
    )


@jet_selection.init
def jet_selection_init(self: Selector) -> None:
    self.shifts |= {
        shift_inst.name
        for shift_inst in self.config_inst.shifts
        if shift_inst.has_tag(("jec", "jer"))
    }


@selector(
    uses={"MET.{pt,phi}"},
)
def MET_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    met_sel = events.MET.pt >= 20.0

    return events, SelectionResult(
        steps={
            "MET": met_sel,
        },
    )


@selector(
    uses={"Jet.{pt,eta,phi,btagDeepFlavB}"},
)
def check_for_1btag(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    btag_wp = self.config_inst.x.btag_working_point
    btag_mask = (
        (events.Jet.pt >= 25.0) &
        (abs(events.Jet.eta) < 2.4) &
        (events.Jet.btagDeepFlavB >= btag_wp)
    )
    has_btag_jet = ak.sum(btag_mask, axis=1) >= 1

    return events, SelectionResult(
        steps={
            "btag": has_btag_jet,
        },
    )


@check_for_1btag.init
def check_for_1btag_init(self: Selector) -> None:
    self.shifts |= {
        shift_inst.name
        for shift_inst in self.config_inst.shifts
        if shift_inst.has_tag(("jec", "jer"))
    }


@selector(
    uses={
        mc_weight, cutflow_features, process_ids, muon_selection, jet_selection,
        MET_selection, check_for_1btag, increment_stats,
    },
    produces={
        mc_weight, cutflow_features, process_ids,
    },
    exposed=True,
)
def preselection(
    self: Selector,
    events: ak.Array,
    stats: defaultdict,
    **kwargs,
) -> tuple[ak.Array, SelectionResult]:
    results = SelectionResult()

    events, muon_results = self[muon_selection](events, **kwargs)
    results += muon_results

    events, jet_results = self[jet_selection](events, **kwargs)
    results += jet_results

    events, met_results = self[MET_selection](events, **kwargs)
    results += met_results

    events, btag_results = self[check_for_1btag](events, **kwargs)
    results += btag_results

    results.event = (
        results.steps.muon &
        results.steps.jet &
        results.steps.MET &
        results.steps.btag
    )

    events = self[process_ids](events, **kwargs)

    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)

    events = self[cutflow_features](events, results.objects, **kwargs)

    weight_map = {
        "num_events": Ellipsis,
        "num_events_selected": results.event,
    }
    group_map = {}
    if self.dataset_inst.is_mc:
        weight_map = {
            **weight_map,
            "sum_mc_weight": (events.mc_weight, Ellipsis),
            "sum_mc_weight_selected": (events.mc_weight, results.event),
        }
        group_map = {
            "process": {
                "values": events.process_id,
                "mask_fn": (lambda v: events.process_id == v),
            },
            "njet": {
                "values": results.x.n_jets,
                "mask_fn": (lambda v: results.x.n_jets == v),
            },
        }
    events, results = self[increment_stats](
        events,
        results,
        stats,
        weight_map=weight_map,
        group_map=group_map,
        **kwargs,
    )

    return events, results
