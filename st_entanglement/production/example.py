# coding: utf-8

"""
Column production methods related to higher-level features.
"""

from functools import partial

from columnflow.production import Producer, producer
from columnflow.production.categories import category_ids
from columnflow.production.normalization import normalization_weights
from columnflow.production.cms.seeds import deterministic_seeds
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.production.cms.muon import muon_weights
from columnflow.reduction.util import create_collections_from_masks
from columnflow.util import maybe_import
from columnflow.columnar_util import EMPTY_FLOAT, Route, attach_coffea_behavior, set_ak_column
from st_entanglement.production.weights import weights

np = maybe_import("numpy")
ak = maybe_import("awkward")


# helper
set_ak_f32 = partial(set_ak_column, value_type=np.float32)


@producer(
    uses=set(),
    produces=set(),
    exposed=True,
)
def identity(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    return events


@producer(
    uses={"Jet.{pt,eta,phi,mass}"},
    produces={"ht", "n_jet", "dijet.{pt,mass,dr}"},
)
def jet_features(self: Producer, events: ak.Array, **kwargs) -> ak.Array:

    # event observables
    events = set_ak_column(events, "ht", ak.sum(events.Jet.pt, axis=1))
    events = set_ak_column(events, "n_jet", ak.num(events.Jet.pt, axis=1), value_type=np.int32)

    # attach coffea behaviour
    events = attach_coffea_behavior(events, collections={})
    # object padding (Note that after padding, ak.num(events.Jet.pt, axis=1) would always be >= 2)
    events = set_ak_column(events, "Jet", ak.pad_none(events.Jet, 2))

    # dijet features
    dijet = ak.with_name(events.Jet[:, 0] + events.Jet[:, 1], "Jet")
    dijet = set_ak_f32(dijet, "dr", events.Jet[:, 0].delta_r(events.Jet[:, 1]))
    dijet_columns = ("pt", "mass", "dr")
    for col in dijet_columns:
        events = set_ak_f32(events, f"dijet.{col}", ak.fill_none(getattr(dijet, col), EMPTY_FLOAT))

    return events


@producer(
    uses={"Electron.{pt,eta,phi,mass}", "Muon.{pt,eta,phi,mass}"},
    produces={"Lepton.{pt,eta,phi,mass}"},
)
def lepton_kinematics(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # At this stage, the event is assumed to contain exactly one selected electron or muon.
    electron = ak.pad_none(events.Electron, 1)[:, 0]
    muon = ak.pad_none(events.Muon, 1)[:, 0]
    has_electron = ak.num(events.Electron, axis=1) == 1

    events = set_ak_f32(events, "Lepton.pt", ak.where(has_electron, electron.pt, muon.pt))
    events = set_ak_f32(events, "Lepton.eta", ak.where(has_electron, electron.eta, muon.eta))
    events = set_ak_f32(events, "Lepton.phi", ak.where(has_electron, electron.phi, muon.phi))
    events = set_ak_f32(events, "Lepton.mass", ak.where(has_electron, electron.mass, muon.mass))

    return events


@producer(
    uses={"Jet.{pt,eta,phi,mass,btagDeepFlavB}"},
    produces={"Bjet.{pt,eta,phi,mass,btagDeepFlavB}"},
)
def bjet_kinematics(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # At this stage, the event is assumed to contain exactly one selected b-tagged jet.
    cuts = self.config_inst.x.btag_selection
    btag_wp = self.config_inst.x.btag_working_point
    btag_mask = (
        (events.Jet.pt >= cuts.pt_min) &
        (abs(events.Jet.eta) < cuts.abs_eta_max) &
        (events.Jet.btagDeepFlavB >= btag_wp)
    )
    bjet = ak.pad_none(events.Jet[btag_mask], 1)[:, 0]

    events = set_ak_f32(events, "Bjet.pt", bjet.pt)
    events = set_ak_f32(events, "Bjet.eta", bjet.eta)
    events = set_ak_f32(events, "Bjet.phi", bjet.phi)
    events = set_ak_f32(events, "Bjet.mass", bjet.mass)
    events = set_ak_f32(events, "Bjet.btagDeepFlavB", bjet.btagDeepFlavB)

    return events


@producer(
    uses={mc_weight, category_ids, "Jet.{pt,phi}", "Muon.{pt,eta,phi}"},
    produces={mc_weight, category_ids, "cutflow.jet1_pt", "cutflow.muon_pt"},
)
def cutflow_features(
    self: Producer,
    events: ak.Array,
    object_masks: dict[str, dict[str, ak.Array]],
    **kwargs,
) -> ak.Array:
    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)

    # apply object masks and create new collections
    reduced_events = create_collections_from_masks(events, object_masks)

    # create category ids per event and add categories back to the
    events = self[category_ids](reduced_events, target_events=events, **kwargs)

    # add cutflow columns
    events = set_ak_column(
        events,
        "cutflow.jet1_pt",
        Route("Jet.pt[:,0]").apply(reduced_events, EMPTY_FLOAT),
    )
    events = set_ak_column(
        events,
        "cutflow.muon_pt",
        Route("Muon.pt[:,0]").apply(reduced_events, EMPTY_FLOAT),
    )

    return events


@producer(
    uses={
        jet_features, lepton_kinematics, bjet_kinematics, category_ids,
        normalization_weights, muon_weights, deterministic_seeds, weights,
    },
    produces={
        jet_features, lepton_kinematics, bjet_kinematics, category_ids,
        normalization_weights, muon_weights, deterministic_seeds, weights,
    },
)
def example(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # jet_features
    events = self[jet_features](events, **kwargs)

    # selected lepton kinematics
    events = self[lepton_kinematics](events, **kwargs)

    # selected b-jet kinematics and discriminator
    events = self[bjet_kinematics](events, **kwargs)

    # category ids
    events = self[category_ids](events, **kwargs)

    # deterministic seeds
    events = self[deterministic_seeds](events, **kwargs)

    # weights
    events = self[weights](events, **kwargs)

    return events
