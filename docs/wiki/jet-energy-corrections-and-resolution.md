# Entry 4: Jet Energy Corrections and Jet Energy Resolution

## POG Recommendation

Jet energy corrections and jet energy resolution should follow the **JetMET / JERC POG**
recommendations, using the JME correctionlib payloads distributed through `jsonpog-integration`.

For Run 2 UL AK4 CHS jets, the payload family is the JERC JSON set, typically accessed through

- `POG/JME/<campaign>/jet_jerc.json.gz`

The JERC payloads provide:

- the usual JEC levels such as `L1FastJet`, `L2Relative`, `L3Absolute`, and `L2L3Residual`
- convenience compound corrections such as `L1L2L3Res`
- uncertainty sources
- JER scale factors and JER resolution parameterizations

## ColumnFlow Interface Available In The Repo

ColumnFlow already ships dedicated CMS calibrators for:

- `columnflow.calibration.cms.jets.jec`
- `columnflow.calibration.cms.jets.jer`

These calibrators are designed to:

- read the JERC JSON payloads from `cfg.x.external_files`
- apply nominal jet corrections
- propagate corrections and uncertainties to MET when configured
- create shifted jet and MET columns for JEC and JER variations

The JEC calibrator expects a config entry of the form:

- `cfg.x.jec["Jet"]`

with campaign, version, jet type, levels, and uncertainty-source settings. The JER calibrator
follows the analogous `cfg.x.jer[...]` pattern.

## Current Repo Status

In the present `ST_entanglement` repository, the default calibrator is still the local example
calibrator in:

- `st_entanglement/calibration/example.py`

That calibrator does not run the real CMS JEC/JER machinery. Instead, it:

- rescales jet `pt` and `mass` in a toy way
- writes placeholder `Jet.pt_jec_up`, `Jet.pt_jec_down`, `Jet.mass_jec_up`, and
  `Jet.mass_jec_down` columns

The analysis config does already define JEC-style shifts and aliases:

- `jec_up`
- `jec_down`

with aliases redirecting:

- `Jet.pt`
- `Jet.mass`
- `MET.pt`
- `MET.phi`

to shifted columns when the JEC shift is requested.

So the current state is:

- the analysis is already structured to consume JEC-like shifted columns
- the default implementation is still a placeholder example
- the real JEC/JER calibrators exist in the vendored ColumnFlow framework but are not yet selected
  as the default analysis calibrator

## Practical Consequence

For documentation purposes, the cleanest wording is that the repository already has the framework
shape needed for JEC systematics, but not yet the full physics-grade JERC hookup. Once the
analysis switches from the local `example` calibrator to the CMS `jec` / `jer` calibrators and
adds the corresponding `cfg.x.jec` / `cfg.x.jer` external-file configuration, the existing shift
machinery should map naturally onto the standard ColumnFlow interface.

## References

- JetMET POG correctionlib payload overview:
  https://dasanalysissystem.docs.cern.ch/md__builds_cms-analysis_general_DasAnalysisSystem_Core_Installer_tables_jsonpog-integration_POG_JME_README.html
- JetMET recommendation hub:
  https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetMET
- JEC data/MC campaign mapping:
  https://twiki.cern.ch/twiki/bin/viewauth/CMS/JECDataMC
- JER recommendations:
  https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
- JEC uncertainty sources:
  https://twiki.cern.ch/twiki/bin/view/CMS/JECUncertaintySources
