# coding: utf-8

"""
Producers related to event weights.
"""

from columnflow.production import Producer, producer
from columnflow.production.cms.btag import btag_weights
from columnflow.production.cms.electron import electron_weights
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.production.cms.muon import muon_weights
from columnflow.production.normalization import normalization_weights
from columnflow.production.cms.pileup import pu_weight
from columnflow.util import maybe_import

# from st_entanglement.production.gen_top import top_pt_weight
from st_entanglement.production.gen_v import vjets_weight
# from mtt.production.l1_prefiring import l1_prefiring_weights
# from mtt.production.toptag import toptag_weights

ak = maybe_import("awkward")

@producer
def weights(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Main event weight producer (e.g. MC generator, scale factors, normalization).
    """
    if self.dataset_inst.is_mc:
        # compute muon weights
        muon_mask = (events.Muon["pt"] >= 30) & (abs(events.Muon["eta"]) < 2.4)
        events = self[muon_weights](events, muon_mask=muon_mask, **kwargs)

        # FIXME: not all weights are available for run 3
        if self.config_inst.x.run == 2:
            # # compute L1 prefiring weights
            # FIXME: why is this broken?
            # events = self[l1_prefiring_weights](events, **kwargs)

            # compute V+jets K factor weights
            if self.dataset_inst.has_tag("is_v_jets"):
                events = self[vjets_weight](events, **kwargs)

        # # compute top pT weights (disabled for now)
        # if self.dataset_inst.has_tag("is_sm_ttbar"):
        #     events = self[top_pt_weight](events, **kwargs)

        # compute normalization weights
        events = self[normalization_weights](events, **kwargs)

        # compute MC weights
        events = self[mc_weight](events, **kwargs)

        events = self[pu_weight](events, **kwargs)

    return events


@weights.init
def weights_init(self: Producer) -> None:
    if getattr(self, "dataset_inst", None) and self.dataset_inst.is_mc:
        # dynamically add dependencies if running on MC
        self.uses |= {
            muon_weights,
            # btag_weights,
            normalization_weights,
            pu_weight,
            mc_weight,
            "Muon.{pt,eta,phi}",
        }
        self.produces |= {
            muon_weights,
            # btag_weights,
            normalization_weights,
            pu_weight,
            mc_weight,
        }
        if self.config_inst.x.run == 2:
            self.uses |= {
                # l1_prefiring_weights,
                vjets_weight,
            }
            self.produces |= {
                # l1_prefiring_weights,
                vjets_weight,
            }

