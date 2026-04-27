# Entry 2: Muons

## NanoAOD Collection Preselection

In NanoAOD, the `Muon` collection is not a fully unfiltered list of all reconstructed muon
candidates. It is already preselected at production time with a basic requirement of the form:

```text
pt > 15 || 
(pt > 3 && (
  passed('CutBasedIdLoose') ||
  passed('SoftCutBasedId') ||
  passed('SoftMvaId') ||
  passed('CutBasedIdGlobalHighPt') ||    
  passed('CutBasedIdTrkHighPt')
  )
)
```

The practical consequence is:

- muons with `pT < 3 GeV` are discarded before they ever appear in NanoAOD
- muons with `3 < pT < 15 GeV` are kept only if they pass one of the listed cut-based or soft-ID
  style requirements
- muons with `pT > 15 GeV` are kept without needing this additional preselection step

This is important when defining analysis object selections, because the NanoAOD `Muon` collection
is already a filtered subset of the full upstream reconstruction output.

## Corrections

### POG Recommendation

For Run 2 muons, the recommended scale factors come from the **Muon POG** correctionlib JSON
payloads documented on the maintained **Muon Wiki** correction guidelines page rather than the old
Twiki pages. In the Run 2 UL regime, the recommendation is to use the Muon POG correction sets
from the `jsonpog-integration` payloads, with the file choice matched to the muon `pT` regime:

- `muon_JPsi.json` for low-`pT` scale factors, with `pT < 30 GeV`
- `muon_Z.json` for the standard Z-peak regime, roughly `15 < pT < 200 GeV`
- `muon_HighPt.json` for the very high-`pT` regime, with `pT > 200 GeV`

For the current analysis setup, the most relevant payload is `muon_Z.json.gz`, since the example
selection is centered on ordinary single-muon analysis phase space rather than the low-`pT` or
very-high-`pT` extremes.

The maintained Muon Wiki guidance also notes that for **Run 2 UL** the scale factors are derived
as functions of `abs(eta)`, but can still be read using `eta` as input for consistency with newer
campaigns.

### How This Repo Already Interfaces with ColumnFlow

Muon scale factors are already the most concretely integrated of the current correction topics.

The current analysis config defines the muon SF setup through:

- `cfg.x.muon_sf_names` in `st_entanglement/config/analysis_st_entanglement.py`
- `cfg.x.external_files["muon_sf"]`, which currently points to
  `.../POG/MUO/{year}_UL/muon_Z.json.gz`

That configuration is consumed by ColumnFlow's CMS muon producer:

- `columnflow.production.cms.muon.muon_weights`

and the example analysis producer already runs it:

- `st_entanglement/production/example.py`

In practice, this means the workflow already follows the standard ColumnFlow pattern:

- the correction file is loaded from `cfg.x.external_files`
- the correction name and campaign are configured via `MuonSFConfig`
- per-event products `muon_weight`, `muon_weight_up`, and `muon_weight_down` are written
- the config exposes `mu_up` and `mu_down` shifts via aliases on `muon_weight`

So for muons, the framework interface is already present in this repo rather than only available
upstream.

### Practical Note For This Analysis

The current `MuonSFConfig` in the repo is:

- correction:
  `NUM_TightRelIso_DEN_TightIDandIPCut`
- campaign:
  `{year}_UL`

That is a reasonable baseline for the present single-muon example workflow, but the final analysis
should still confirm that this working point exactly matches the muon ID and isolation working
point used in the eventual physics selection.

## References

- Muon Wiki correction guidelines:
  https://muon-wiki.docs.cern.ch/guidelines/corrections/
- Muon POG correctionlib usage summary:
  https://dasanalysissystem.docs.cern.ch/md__builds_cms-analysis_general_DasAnalysisSystem_Core_Installer_tables_jsonpog-integration_POG_MUO_README.html
