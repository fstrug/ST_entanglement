# coding: utf-8

"""
Configuration of the ST_entanglement analysis.
"""

import law
import order as od
from scinum import Number

from columnflow.config_util import (
    get_root_processes_from_campaign, add_shift_aliases, get_shifts_from_sources, add_category, verify_config_processes,
)
from columnflow.columnar_util import EMPTY_FLOAT, ColumnCollection, skip_column
from columnflow.util import DotDict, maybe_import
import os, yaml
thisdir = os.path.dirname(os.path.abspath(__file__))

ak = maybe_import("awkward")
np = maybe_import("numpy")


#
# the main analysis object
#

analysis_st_entanglement = ana = od.Analysis(
    name="analysis_st_entanglement",
    id=1,
)

# analysis-global versions
# (see cfg.x.versions below for more info)
ana.x.versions = {}

# files of bash sandboxes that might be required by remote tasks
# (used in cf.HTCondorWorkflow)
ana.x.bash_sandboxes = ["$CF_BASE/sandboxes/cf.sh"]
default_sandbox = law.Sandbox.new(law.config.get("analysis", "default_columnar_sandbox"))
if default_sandbox.sandbox_type == "bash" and default_sandbox.name not in ana.x.bash_sandboxes:
    ana.x.bash_sandboxes.append(default_sandbox.name)

# files of cmssw sandboxes that might be required by remote tasks
# (used in cf.HTCondorWorkflow)
ana.x.cmssw_sandboxes = [
    "$CF_BASE/sandboxes/cmssw_default.sh",
]

# config groups for conveniently looping over certain configs
# (used in wrapper_factory)
ana.x.config_groups = {}

# named function hooks that can modify store_parts of task outputs if needed
ana.x.store_parts_modifiers = {}

# histogramming hooks, invoked before creating plots when --hist-hook parameter set
ana.x.hist_hooks = {}


#
# setup configs
#

# an example config is setup below, based on cms NanoAOD v9 for Run2 2017, focussing on
# ttbar and single top MCs, plus single muon data
# update this config or add additional ones to accomodate the needs of your analysis

from cmsdb.campaigns.run2_2017_nano_v9 import campaign_run2_2017_nano_v9

# copy the campaign
# (creates copies of all linked datasets, processes, etc. to allow for encapsulated customization)
campaign = campaign_run2_2017_nano_v9.copy()

# get all root processes
procs = get_root_processes_from_campaign(campaign)

# create a config by passing the campaign, so id and name will be identical
cfg = ana.add_config(campaign)

# gather campaign data
year = campaign.x.year

# add run tag to config
cfg.x.run = 2

# add processes we are interested in
process_names = [
    # Data
    "data",
    # Signal
    "st_tchannel",
    # Major Backgrounds
    "w_lnu",
    "qcd",
    "tt",
    # Minor Backgrounds
    "dy",
    "st_twchannel"
]
for process_name in process_names:
    # add the process
    proc = cfg.add_process(procs.get(process_name))

    # configuration of colors, labels, etc. can happen here
    if proc.name == "data":
        proc.color1 = (0, 0, 0)
    elif proc.name == "tt":
        proc.color1 = (244, 182, 66)
    elif proc.name == "st":
        proc.color1 = (244, 93, 66)
    elif proc.name == "st_tchannel_t":
        proc.color1 = (244, 93, 66)
    elif proc.name == "st_tchannel_tbar":
        proc.color1 = (66, 135, 244)
    elif proc.name == "w_lnu":
        proc.color1 = (86, 180, 233)
    elif proc.name == "qcd":
        proc.color1 = (148, 103, 189)
    elif proc.name == "dy":
        proc.color1 = (44, 160, 44)
    elif proc.name == "st_twchannel":
        proc.color1 = (214, 39, 40)

# add datasets we need to study
dataset_names = [
    # data
    "data_mu_b",
    "data_mu_c",
    "data_mu_d",
    "data_mu_e",
    "data_mu_f",
    # signals
    "st_tchannel_t_5f_powheg",
    "st_tchannel_tbar_5f_powheg",
    ### Major backgrounds
    # ttbar
    "tt_sl_powheg",
    # QCD
    "qcd_ht50to100_madgraph",
    "qcd_ht100to200_madgraph",
    "qcd_ht200to300_madgraph",
    "qcd_ht300to500_madgraph",
    "qcd_ht500to700_madgraph",
    "qcd_ht700to1000_madgraph",
    "qcd_ht1000to1500_madgraph",
    "qcd_ht1500to2000_madgraph",
    "qcd_ht2000toinf_madgraph",
    # WJets
    "w_lnu_ht70to100_madgraph",
    "w_lnu_ht100to200_madgraph",
    "w_lnu_ht200to400_madgraph",
    "w_lnu_ht400to600_madgraph",
    "w_lnu_ht600to800_madgraph",
    "w_lnu_ht800to1200_madgraph",
    "w_lnu_ht1200to2500_madgraph",
    "w_lnu_ht2500toinf_madgraph",

    ### Minor backgrounds
    # DY
    "dy_m50toinf_ht70to100_madgraph",
    "dy_m50toinf_ht100to200_madgraph",
    "dy_m50toinf_ht200to400_madgraph",
    "dy_m50toinf_ht400to600_madgraph",
    "dy_m50toinf_ht600to800_madgraph",
    "dy_m50toinf_ht800to1200_madgraph",
    "dy_m50toinf_ht1200to2500_madgraph",
    "dy_m50toinf_ht2500toinf_madgraph",
    # tW
    "st_twchannel_t_powheg",
    "st_twchannel_tbar_powheg",
]
for dataset_name in dataset_names:
    # add the dataset
    dataset = cfg.add_dataset(campaign.get_dataset(dataset_name))

    # for testing purposes, limit the number of files to 2
    for info in dataset.info.values():
        info.n_files = min(info.n_files, 2)

# W/Z+jets datasets
if dataset.name.startswith("dy"):
    dataset.add_tag({"is_v_jets", "is_z_jets"})
if dataset.name.startswith("w_lnu"):
    dataset.add_tag({"is_v_jets", "is_w_jets"})

# verify that the root process of all datasets is part of any of the registered processes
verify_config_processes(cfg, warn=True)

# default objects, such as calibrator, selector, reducer, producer, ml model, inference model, etc
cfg.x.default_calibrator = "example"
cfg.x.default_selector = "preselection"
cfg.x.default_selector_steps = []
cfg.x.default_reducer = "cf_default"
cfg.x.default_producer = "example"
cfg.x.default_hist_producer = "all_weights"
cfg.x.default_ml_model = None
cfg.x.default_inference_model = "example"
cfg.x.default_categories = ("incl",)
cfg.x.default_variables = ("n_jet", "jet1_pt")

# process groups for conveniently looping over certain processs
# (used in wrapper_factory and during plotting)
cfg.x.process_groups = {
    "st_grouped": ["tt", "st"],
    "st_split": ["st_tchannel_t", "st_tchannel_tbar"],
    "signals": [],  # list of signal parent processes e.g. h, hh etc. (needed for some features)
    "other_groups": [],
}

# dataset groups for conveniently looping over certain datasets
# (used in wrapper_factory and during plotting)
cfg.x.dataset_groups = {}

# category groups for conveniently looping over certain categories
# (used during plotting)
cfg.x.category_groups = {
    "channels": ["1e", "1mu"],
}

# variable groups for conveniently looping over certain variables
# (used during plotting)
cfg.x.variable_groups = {
    "n_particles": ("n_jet", "n_bjet", "nMuon", "nElectron"),
    "jet1_kin": ("jet1_pt", "jet1_eta", "jet1_phi"),
    "jet2_kin": ("jet2_pt", "jet2_eta", "jet2_phi"),
    "lepton_kin": ("Lepton_pt", "Lepton_eta", "Lepton_phi", "Lepton_mass"),
    "bjet_kin": ("Bjet_pt", "Bjet_eta", "Bjet_phi", "Bjet_mass", "Bjet_btagDeepFlavB"),
    "muon_kin": ("muon_pt", "muon_eta", "muon_phi"),
    "electron_kin": ("electron_pt", "electron_eta", "electron_phi"),
    "MET_kin": ("MET_pt","MET_phi"),
}

# shift groups for conveniently looping over certain shifts
# (used during plotting)
cfg.x.shift_groups = {}

# general_settings groups for conveniently looping over different values for the general-settings parameter
# (used during plotting)
cfg.x.general_settings_groups = {}

# process_settings groups for conveniently looping over different values for the process-settings parameter
# (used during plotting)
cfg.x.process_settings_groups = {}

# variable_settings groups for conveniently looping over different values for the variable-settings parameter
# (used during plotting)
cfg.x.variable_settings_groups = {}

# custom_style_config groups for conveniently looping over certain style configs
# (used during plotting)
cfg.x.custom_style_config_groups = {}

# selector step groups for conveniently looping over certain steps
# (used in cutflow tasks)
cfg.x.selector_step_groups = {
    "default": ["electron", "muon", "trigger", "jet", "MET", "btag"],
    "electron_channel_steps": ["electron", "jet", "MET", "btag"],
    "muon_channel_steps": ["muon", "trigger", "jet", "MET", "btag"],
}

# calibrator groups for conveniently looping over certain calibrators
# (used during calibration)
ana.x.calibrator_groups = {}

# producer groups for conveniently looping over certain producers
# (used during the ProduceColumns task)
ana.x.producer_groups = {}

# ml_model groups for conveniently looping over certain ml_models
# (used during the machine learning tasks)
ana.x.ml_model_groups = {}

# custom method and sandbox for determining dataset lfns
cfg.x.get_dataset_lfns = None
cfg.x.get_dataset_lfns_sandbox = None

# whether to validate the number of obtained LFNs in GetDatasetLFNs
# (currently set to false because the number of files per dataset is truncated to 2)
cfg.x.validate_dataset_lfns = False

# lumi values in inverse pb
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2?rev=2#Combination_and_correlations
cfg.x.luminosity = Number(41480, {
    "lumi_13TeV_2017": 0.02j,
    "lumi_13TeV_1718": 0.006j,
    "lumi_13TeV_correlated": 0.009j,
})



# 2017 UL DeepJet medium working point
cfg.x.btag_working_point = 0.3040

# lepton selection cuts used by preselection selectors
cfg.x.electron_selection = DotDict.wrap({
    "pt_min": 27.0,
    "abs_eta_max": 2.1,
})
cfg.x.muon_selection = DotDict.wrap({
    "pt_min": 24.0,
    "abs_eta_max": 2.1,
})
cfg.x.trigger_names = (
    "IsoMu24",
    "IsoMu24_eta2p1",
)
cfg.x.btag_selection = DotDict.wrap({
    "pt_min": 25.0,
    "abs_eta_max": 4.1,
    "n_btag": 1,
})
cfg.x.met_selection = DotDict.wrap({
    "pt_min": 30.0,
})

 #
# JEC & JER  # FIXME: Taken from HBW
# https://github.com/uhh-cms/hh2bbww/blob/master/hbw/config/config_run2.py#L138C5-L269C1
#

# jec configuration
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC?rev=2017#Jet_Energy_Corrections_in_Run2

jerc_campaign = "Summer19UL17"
jet_type = "AK4PFchs"

cfg.x.jec = DotDict.wrap({
    "Jet": {
        "campaign": jerc_campaign,
        "version": "V5",
        "jet_type": jet_type,
        "levels": ["L1L2L3Res"],
        "levels_for_type1_met": ["L1FastJet"],
        # "data_eras": sorted(filter(None, {d.x("jec_era", None) for d in cfg.datasets if d.is_data})),
        "uncertainty_sources": [
            # comment out most for now to prevent large file sizes
            # "AbsoluteStat",
            # "AbsoluteScale",
            # "AbsoluteSample",
            # "AbsoluteFlavMap",
            # "AbsoluteMPFBias",
            # "Fragmentation",
            # "SinglePionECAL",
            # "SinglePionHCAL",
            # "FlavorQCD",
            # "TimePtEta",
            # "RelativeJEREC1",
            # "RelativeJEREC2",
            # "RelativeJERHF",
            # "RelativePtBB",
            # "RelativePtEC1",
            # "RelativePtEC2",
            # "RelativePtHF",
            # "RelativeBal",
            # "RelativeSample",
            # "RelativeFSR",
            # "RelativeStatFSR",
            # "RelativeStatEC",
            # "RelativeStatHF",
            # "PileUpDataMC",
            # "PileUpPtRef",
            # "PileUpPtBB",
            # "PileUpPtEC1",
            # "PileUpPtEC2",
            # "PileUpPtHF",
            # "PileUpMuZero",
            # "PileUpEnvelope",
            # "SubTotalPileUp",
            # "SubTotalRelative",
            # "SubTotalPt",
            # "SubTotalScale",
            # "SubTotalAbsolute",
            # "SubTotalMC",
            "Total",
            # "TotalNoFlavor",
            # "TotalNoTime",
            # "TotalNoFlavorNoTime",
            # "FlavorZJet",
            # "FlavorPhotonJet",
            # "FlavorPureGluon",
            # "FlavorPureQuark",
            # "FlavorPureCharm",
            # "FlavorPureBottom",
            # "TimeRunA",
            # "TimeRunB",
            # "TimeRunC",
            # "TimeRunD",
            # "CorrelationGroupMPFInSitu",
            # "CorrelationGroupIntercalibration",
            # "CorrelationGroupbJES",
            # "CorrelationGroupFlavor",
            # "CorrelationGroupUncorrelated",
        ],
    },
})

# JER
# https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution?rev=107
cfg.x.jer = DotDict.wrap({
    "Jet": {
        "campaign": jerc_campaign,
        "version": "JRV2",
        "jet_type": jet_type,
    },
})
# lepton sf taken from
# https://github.com/uhh-cms/hh2bbww/blob/master/hbw/config/config_run2.py#L338C1-L352C85
# names of electron correction sets and working points
# (used in the electron_sf producer)
# TODO: check that these are appropriate
from columnflow.production.cms.electron import ElectronSFConfig
cfg.x.electron_sf_names = ElectronSFConfig(
    correction="UL-Electron-ID-SF",
    campaign=f"{year}_UL",
    working_point = "wp80iso"
)

# names of muon correction sets and working points
# (used in the muon producer)
from columnflow.production.cms.muon import MuonSFConfig
cfg.x.muon_sf_names = MuonSFConfig(
    correction="NUM_TightRelIso_DEN_TightIDandIPCut",
    campaign=f"{year}_UL",
)

# read in JEC sources from file
with open(os.path.join(thisdir, "jec_sources.yaml"), "r") as f:
    all_jec_sources = yaml.load(f, yaml.Loader)["names"]

# declare the shifts
def add_shifts(cfg):
    # register shifts
    cfg.add_shift(name="nominal", id=0)

    # tune shifts are covered by dedicated, varied datasets, so tag the shift as "disjoint_from_nominal"
    # (this is currently used to decide whether ML evaluations are done on the full shifted dataset)
    cfg.add_shift(name="tune_up", id=1, type="shape", tags={"disjoint_from_nominal"})
    cfg.add_shift(name="tune_down", id=2, type="shape", tags={"disjoint_from_nominal"})

    cfg.add_shift(name="hdamp_up", id=3, type="shape", tags={"disjoint_from_nominal"})
    cfg.add_shift(name="hdamp_down", id=4, type="shape", tags={"disjoint_from_nominal"})

    # pileup / minimum bias cross section variations
    cfg.add_shift(name="minbias_xs_up", id=7, type="shape")
    cfg.add_shift(name="minbias_xs_down", id=8, type="shape")
    add_shift_aliases(cfg, "minbias_xs", {"pu_weight": "pu_weight_{name}"})

    # top pt reweighting
    cfg.add_shift(name="top_pt_up", id=9, type="shape")
    cfg.add_shift(name="top_pt_down", id=10, type="shape")
    add_shift_aliases(cfg, "top_pt", {"top_pt_weight": "top_pt_weight_{direction}"})

    # prefiring weights
    cfg.add_shift(name="l1_ecal_prefiring_up", id=301, type="shape")
    cfg.add_shift(name="l1_ecal_prefiring_down", id=302, type="shape")
    add_shift_aliases(
        cfg,
        "l1_ecal_prefiring",
        {"l1_ecal_prefiring_weight": "l1_ecal_prefiring_weight_{direction}"},
    )
    
    # jet energy scale (JEC) uncertainty variations
    for jec_source in cfg.x.jec.Jet.uncertainty_sources:
        idx = all_jec_sources.index(jec_source)
        cfg.add_shift(name=f"jec_{jec_source}_up", id=5000 + 2 * idx, type="shape", tags={"jec"})
        cfg.add_shift(name=f"jec_{jec_source}_down", id=5001 + 2 * idx, type="shape", tags={"jec"})
        add_shift_aliases(
            cfg,
            f"jec_{jec_source}",
            {
                "Jet.pt": "Jet.pt_{name}",
                "Jet.mass": "Jet.mass_{name}",
                "MET.pt": "MET.pt_{name}",
            },
        )

    # jet energy resolution (JER) scale factor variations
    cfg.add_shift(name="jer_up", id=6000, type="shape")
    cfg.add_shift(name="jer_down", id=6001, type="shape")
    add_shift_aliases(
        cfg,
        "jer",
        {
            "Jet.pt": "Jet.pt_{name}",
            "Jet.mass": "Jet.mass_{name}",
            "MET.pt": "MET.pt_{name}",
        },
    )

    # event weights due to muon scale factors
    cfg.add_shift(name="mu_up", id=111, type="shape")
    cfg.add_shift(name="mu_down", id=112, type="shape")
    add_shift_aliases(cfg, "mu", {"muon_weight": "muon_weight_{direction}"})

    # event weights due to electron scale factors
    cfg.add_shift(name="electron_up", id=113, type="shape")
    cfg.add_shift(name="electron_down", id=114, type="shape")
    add_shift_aliases(cfg, "electron", {"electron_weight": "electron_weight_{direction}"})

    # V+jets reweighting
    cfg.add_shift(name="vjets_up", id=201, type="shape")
    cfg.add_shift(name="vjets_down", id=202, type="shape")
    add_shift_aliases(cfg, "vjets", {"vjets_weight": "vjets_weight_{direction}"})

# add the shifts
add_shifts(cfg)

# external files
sources = {
        "cert": "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV",
        "local_repo": os.getenv("ST_ENTANGLEMENT_BASE"),
        "json_mirror": "/afs/cern.ch/user/f/fstrug/public/mirrors/jsonpog-integration-a81953b1",
        "jet": "/afs/cern.ch/user/f/fstrug/public/mirrors/cms-jet-JSON_Format-54860a23",
    }

corr_tag = "2017_UL"
cfg.x.external_files = DotDict.wrap({
    # # pileup weight corrections
    "pu_sf": (f"{sources['json_mirror']}/POG/LUM/{corr_tag}/puWeights.json.gz", "v1"),  # noqa

    # jet energy corrections
    "jet_jerc": (f"{sources['json_mirror']}/POG/JME/{corr_tag}/jet_jerc.json.gz", "v1"),  # noqa

    # top-tagging scale factors
    "toptag_sf": (f"{sources['jet']}/JMAR/DeepAK8/2017_DeepAK8_Top.json", "v1"),  # noqa

    # btag scale factors
    "btag_sf_corr": (f"{sources['json_mirror']}/POG/BTV/{corr_tag}/btagging.json.gz", "v1"),  # noqa

    # electron scale factors
    "electron_sf": (f"{sources['json_mirror']}/POG/EGM/{corr_tag}/electron.json.gz", "v1"),  # noqa

    # muon scale factors
    "muon_sf": (f"{sources['json_mirror']}/POG/MUO/{corr_tag}/muon_Z.json.gz", "v1"),  # noqa

    # met phi corrector (TODO)
    # "met_phi_corr": (f"{sources['json_mirror']}/POG/JME/{corr_tag}/met.json.gz", "v1"),

    # L1 prefiring corrections
    "l1_prefiring": f"{sources['local_repo']}/data/json/l1_prefiring.json",

    # V+jets reweighting
    "vjets_reweighting": f"{sources['local_repo']}/data/json/vjets_reweighting.json",
})
if year == 2017:
    cfg.x.external_files.update(DotDict.wrap({
        # lumi files
        "lumi": {
            "golden": (f"{sources['cert']}/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt", "v1"),  # noqa
            "normtag": ("/afs/cern.ch/user/l/lumipro/public/Normtags/normtag_PHYSICS.json", "v1"),
        },

        # pileup files (for PU reweighting)
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData?rev=44#Pileup_JSON_Files_For_Run_II
        "pu": {
            "json": (f"{sources['cert']}/PileUp/UltraLegacy/pileup_latest.txt", "v1"),  # noqa
            "mc_profile": ("https://raw.githubusercontent.com/cms-sw/cmssw/435f0b04c0e318c1036a6b95eb169181bbbe8344/SimGeneral/MixingModule/python/mix_2017_25ns_UltraLegacy_PoissonOOTPU_cfi.py", "v1"),  # noqa
            "data_profile": {
                "nominal": (f"{sources['cert']}/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2017-69200ub-99bins.root", "v1"),  # noqa
                "minbias_xs_up": (f"{sources['cert']}/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2017-72400ub-99bins.root", "v1"),  # noqa
                "minbias_xs_down": (f"{sources['cert']}/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2017-66000ub-99bins.root", "v1"),  # noqa
            },
        },
    }))
else:
    raise NotImplementedError(f"No lumi and pu files provided for year {year}")

#### Weights
cfg.x.event_weights = {
            "normalization_weight": [],
            "pu_weight": get_shifts_from_sources(cfg, "minbias_xs"),
            "muon_weight": get_shifts_from_sources(cfg, "mu"), 
            }


# event weights only present in certain datasets
for dataset in cfg.datasets:
    dataset.x.event_weights = DotDict()

    # TTbar: top pt reweighting (disable for now)
    # if dataset.has_tag("is_sm_ttbar"):
    #     dataset.x.event_weights["top_pt_weight"] = get_shifts("top_pt")

    # V+jets: QCD NLO reweighting
    if dataset.has_tag("is_v_jets"):
        dataset.x.event_weights["vjets_weight"] = get_shifts_from_sources(cfg,"vjets")

    # all MC: L1 prefiring
    # if not dataset.is_data:
    #     # prefiring weights (all datasets except real data)
    #    dataset.x.event_weights["l1_ecal_prefiring_weight"] = get_shifts_from_sources(cfg,"l1_ecal_prefiring")


# target file size after MergeReducedEvents in MB
cfg.x.reduced_file_size = 512.0

# columns to keep after certain steps
cfg.x.keep_columns = DotDict.wrap({
     "cf.MergeSelectionMasks": {
        "mc_weight", "normalization_weight", "process_id", "category_ids", "cutflow.*",
        },
    "cf.ReduceEvents": {
        # general event info, mandatory for reading files with coffea
        # additional columns can be added as strings, similar to object info
        ColumnCollection.MANDATORY_COFFEA,
        # weights
        "genWeight",
        "LHEWeight.*",
        "LHEPdfWeight", "LHEScaleWeight",
        "PSWeight",
        # object info
        "Jet.{pt,eta,phi,mass,btagDeepFlavB,hadronFlavour}",
        "Electron.{pt,eta,phi,mass}",
        "Muon.{pt,eta,phi,mass,pfRelIso04_all}",
        "MET.{pt,phi,significance,covXX,covXY,covYY}",
        "PV.npvs",

        # photons (for L1 prefiring)
        "Photon.pt", "Photon.eta", "Photon.phi", "Photon.mass",
        "Photon.jetIdx",

        # average number of pileup interactions
        "Pileup.nTrueInt",

        # all columns added during selection using a ColumnCollection flag, but skip cutflow ones
        ColumnCollection.ALL_FROM_SELECTOR,
        skip_column("cutflow.*"),
        # other columns, required by carious tasks
        "mc_weight",
        "pu_weight*",
    },
    "cf.MergeSelectionMasks": {
        "cutflow.*",
    },
    "cf.UniteColumns": {
        "*",
    },
})

# pinned versions
# (see [versions] in law.cfg for more info)
cfg.x.versions = {}

# channels
cfg.add_channel(name="muon", id=1)
cfg.add_channel(name="electron", id=2)

# histogramming hooks, invoked before creating plots when --hist-hook parameter set
cfg.x.hist_hooks = {}

# add categories using the "add_category" tool which adds auto-generated ids
# the "selection" entries refer to names of categorizers, e.g. in categorization/example.py
# note: it is recommended to always add an inclusive category with id=1 or name="incl" which is used
#       in various places, e.g. for the inclusive cutflow plots and the "empty" selector
add_category(
    cfg,
    id=1,
    name="incl",
    selection="cat_incl",
    label="inclusive",
)
add_category(
    cfg,
    name="1e",
    selection="cat_1e",
    label="1 electron",
)
add_category(
    cfg,
    name="1mu",
    selection="cat_1mu",
    label="1 muon",
)
add_category(
    cfg,
    name="2j",
    selection="cat_2j",
    label="2 jets",
)

# add vars for plotting
from .vars import add_vars
add_vars(cfg)