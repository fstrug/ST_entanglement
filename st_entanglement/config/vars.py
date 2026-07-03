import itertools
import numpy as np
import order as od

from columnflow.columnar_util import EMPTY_FLOAT
from columnflow.util import maybe_import

ak = maybe_import("awkward")

def add_vars(config: od.Config) -> None:
    cfg = config
    # (the "event", "run" and "lumi" variables are required for some cutflow plotting task,
    # and also correspond to the minimal set of columns that coffea's nano scheme requires)
    cfg.add_variable(
        name="event",
        expression="event",
        binning=(1, 0.0, 1.0e9),
        x_title="Event number",
    )
    cfg.add_variable(
        name="run",
        expression="run",
        binning=(1, 100000.0, 500000.0),
        x_title="Run number",
    )
    cfg.add_variable(
        name="lumi",
        expression="luminosityBlock",
        binning=(1, 0.0, 5000.0),
        x_title="Luminosity block",
    )


    # pt of all jets in every event
    cfg.add_variable(
        name="jets_pt",
        expression="Jet.pt",
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"$p_{T} of all jets$",
    )
    # pt of the first jet in every event
    cfg.add_variable(
        name="jet1_pt",  # variable name, to be given to the "--variables" argument for the plotting task
        expression="Jet.pt[:,0]",  # content of the variable
        null_value=EMPTY_FLOAT,  # value to be given if content not available for event
        binning=(40, 0.0, 400.0),  # (bins, lower edge, upper edge)
        unit="GeV",  # unit of the variable, if any
        x_title=r"Jet 1 $p_{T}$",  # x title of histogram when plotted
    )
    # eta of the first jet in every event
    cfg.add_variable(
        name="jet1_eta",
        expression="Jet.eta[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(41, -4.1, 4.1),
        x_title=r"Jet 1 $\eta$",
    )
    cfg.add_variable(
        name="jet1_phi",
        expression="Jet.phi[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Jet 1 $\phi$",
    )
    cfg.add_variable(
        name="jet2_pt",
        expression="Jet.pt[:,1]",
        null_value=EMPTY_FLOAT,
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Jet 2 $p_{T}$",
    )
    cfg.add_variable(
        name="jet2_eta",
        expression="Jet.eta[:,1]",
        null_value=EMPTY_FLOAT,
        binning=(41, -4.1, 4.1),
        x_title=r"Jet 2 $\eta$",
    )
    cfg.add_variable(
        name="jet2_phi",
        expression="Jet.phi[:,1]",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Jet 2 $\phi$",
    )
    cfg.add_variable(
        name="ht",
        expression=lambda events: ak.sum(events.Jet.pt, axis=1),
        binning=(40, 0.0, 800.0),
        unit="GeV",
        x_title="HT",
        aux={"inputs": ["Jet.{pt,eta,phi}"]},
    )
    # weights
    cfg.add_variable(
        name="mc_weight",
        expression="mc_weight",
        binning=(200, -10, 10),
        x_title="MC weight",
    )
    # cutflow variables
    cfg.add_variable(
        name="cf_jet1_pt",
        expression="cutflow.jet1_pt",
        binning=(40, 0.0, 400.0),
        unit="GeV",
        x_title=r"Jet 1 $p_{T}$",
    )

    cfg.add_variable(
        name="cf_muon_pt",
        expression="cutflow.muon_pt",
        binning=(50,0.0,250.0),
        unit="GeV",
        x_title=r"Muon $p_{T}$",
    )

    ##### Variables for ST entanglement analysis
    cfg.add_variable(
        name="nMuon",
        expression=lambda events: ak.num(events.Muon, axis=1),
        binning=(8, -0.5, 7.5),
        x_title="Number of muons",
        aux={"inputs": ["Muon.pt"]},
    )
    cfg.add_variable(
        name="nElectron",
        expression=lambda events: ak.num(events.Electron, axis=1),
        binning=(8, -0.5, 7.5),
        x_title="Number of electrons",
        aux={"inputs": ["Electron.pt"]},
    )
    cfg.add_variable(
        name="electron_pt",
        expression="Electron.pt[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 250.0),
        unit="GeV",
        x_title=r"Electron $p_{T}$",
        aux={"inputs": ["Electron.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="electron_eta",
        expression="Electron.eta[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(30, -3.0, 3.0),
        x_title=r"Electron $\eta$",
        aux={"inputs": ["Electron.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="electron_phi",
        expression="Electron.phi[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Electron $\phi$",
        aux={"inputs": ["Electron.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="muon_pt",
        expression="Muon.pt[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 250.0),
        unit="GeV",
        x_title=r"Muon $p_{T}$",
        aux={"inputs": ["Muon.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="muon_eta",
        expression="Muon.eta[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(30, -3.0, 3.0),
        x_title=r"Muon $\eta$",
        aux={"inputs": ["Muon.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="muon_phi",
        expression="Muon.phi[:,0]",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Muon $\phi$",
        aux={"inputs": ["Muon.{pt,eta,phi}"]},
    )
    cfg.add_variable(
        name="Lepton_pt",
        expression="Lepton.pt",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 250.0),
        unit="GeV",
        x_title=r"Selected lepton $p_{T}$",
        aux={"inputs": ["Lepton.{pt,eta,phi,mass}"]},
    )
    cfg.add_variable(
        name="Lepton_eta",
        expression="Lepton.eta",
        null_value=EMPTY_FLOAT,
        binning=(30, -3.0, 3.0),
        x_title=r"Selected lepton $\eta$",
        aux={"inputs": ["Lepton.{pt,eta,phi,mass}"]},
    )
    cfg.add_variable(
        name="Lepton_phi",
        expression="Lepton.phi",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Selected lepton $\phi$",
        aux={"inputs": ["Lepton.{pt,eta,phi,mass}"]},
    )
    cfg.add_variable(
        name="Lepton_mass",
        expression="Lepton.mass",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 200.0),
        unit="GeV",
        x_title=r"Selected lepton mass",
        aux={"inputs": ["Lepton.{pt,eta,phi,mass}"]},
    )
    cfg.add_variable(
        name="Bjet_pt",
        expression="Bjet.pt",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 250.0),
        unit="GeV",
        x_title=r"Selected b jet $p_{T}$",
        aux={"inputs": ["Bjet.{pt,eta,phi,mass,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="Bjet_eta",
        expression="Bjet.eta",
        null_value=EMPTY_FLOAT,
        binning=(41, -4.1, 4.1),
        x_title=r"Selected b jet $\eta$",
        aux={"inputs": ["Bjet.{pt,eta,phi,mass,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="Bjet_phi",
        expression="Bjet.phi",
        null_value=EMPTY_FLOAT,
        binning=(32, -np.pi, np.pi),
        x_title=r"Selected b jet $\phi$",
        aux={"inputs": ["Bjet.{pt,eta,phi,mass,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="Bjet_mass",
        expression="Bjet.mass",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 200.0),
        unit="GeV",
        x_title=r"Selected b jet mass",
        aux={"inputs": ["Bjet.{pt,eta,phi,mass,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="Bjet_btagDeepFlavB",
        expression="Bjet.btagDeepFlavB",
        null_value=EMPTY_FLOAT,
        binning=(50, 0.0, 1.0),
        x_title=r"Selected b jet DeepFlavB",
        aux={"inputs": ["Bjet.{pt,eta,phi,mass,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="n_jet",
        expression=lambda events: ak.num(events.Jet, axis = 1),
        binning=(11, -0.5, 10.5),
        x_title="Number of jets",
        aux={"inputs": ["Jet.pt"]},
    )
    cfg.add_variable(
        name="n_bjet",
        expression=lambda events: ak.sum(
            (events.Jet.pt >= 25.0) &
            (abs(events.Jet.eta) < 4.1) &
            (events.Jet.btagDeepFlavB >= cfg.x.btag_working_point),
            axis=1,
        ),
        binning=(8, -0.5, 7.5),
        x_title="Number of b-tagged jets",
        aux={"inputs": ["Jet.{pt,phi,eta,btagDeepFlavB}"]},
    )
    cfg.add_variable(
        name="MET_pt",
        expression="MET.pt",
        binning = (100,0,100),
        unit = "GeV",
        x_title=r"MET $p_{T}$"
    )
