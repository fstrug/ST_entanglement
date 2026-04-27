# Entry 5: Luminosity Corrections

## What This Means In A Run 2 CMS Analysis

Luminosity-related corrections enter a Run 2 CMS analysis in two closely related ways:

- for **data**, they define which certified runs and luminosity sections are allowed to enter the
  analysis
- for **simulation**, they define the integrated luminosity used to normalize expected event yields
  and the associated uncertainty nuisance parameters

So luminosity is not a per-object correction like a muon or jet scale factor. Instead, it is part
of the global event-normalization and data-certification machinery.

## Data Side: Golden JSON And Normtag

For Run 2 CMS data, analyses typically process only certified luminosity sections listed in the
official **golden JSON** file. In practical terms, this removes runs or lumi sections that were
not certified as good for physics use.

The corresponding **normtag** file is used together with CMS luminosity tools to compute the
official integrated luminosity for the certified data-taking periods.

In this repository, the external lumi files are already configured in
`st_entanglement/config/analysis_st_entanglement.py` under:

- `cfg.x.external_files["lumi"]["golden"]`
- `cfg.x.external_files["lumi"]["normtag"]`

For the current example config, the golden JSON points to the 2017 UL certification file.

## MC Side: Integrated Luminosity Normalization

On the simulation side, the integrated luminosity enters the usual expected-yield relation:

```text
N_expected = sigma * L * epsilon
```

where:

- `sigma` is the process cross section
- `L` is the integrated luminosity
- `epsilon` stands for the effective acceptance, efficiency, and event weighting chain

This means the luminosity uncertainty is a **rate uncertainty** on simulated yields, not a shape
uncertainty on reconstructed observables.

Data are not reweighted by luminosity in the same sense as MC. Instead, data are selected with
the certified run/lumi mask, while MC predictions are normalized to the target integrated
luminosity.

## Run 2 Uncertainty Structure

For Run 2 CMS combinations, the luminosity uncertainty is usually split into components so that the
correlations across years are modeled correctly.

The current `ST_entanglement` example config already follows that pattern for 2017:

- integrated luminosity:
  `41480 pb^-1`
- year-specific 2017 component:
  `lumi_13TeV_2017 = 2.0%`
- 2017-2018 correlated component:
  `lumi_13TeV_1718 = 0.6%`
- fully correlated Run 2 component:
  `lumi_13TeV_correlated = 0.9%`

These are stored in the config as:

- `cfg.x.luminosity = Number(41480, {...})`

This decomposition is useful because it allows later statistical inference to share or decorrelate
the relevant luminosity nuisance parameters across years in a controlled way.

## How This Repo Already Interfaces With ColumnFlow

The luminosity configuration is already used in this analysis module.

In particular:

- `st_entanglement/config/analysis_st_entanglement.py` defines the integrated luminosity and its
  uncertainty components
- `st_entanglement/inference/example.py` loops over `self.config_inst.x.luminosity.uncertainties`
  and turns each component into a Gaussian rate nuisance parameter

So for luminosity, the current repo already has:

- a configured central value
- a decomposition into uncertainty components
- inference-side nuisance parameter creation

## Practical Notes For This Analysis

- The current example config is a **2017-focused** setup, so the luminosity value and uncertainty
  labels should be read as a concrete example rather than a full Run 2 combination.
- When the analysis expands to all of Run 2, the luminosity treatment should stay consistent across
  2016, 2017, and 2018, especially if a combined inference model is built.
- If separate yearly channels or configs are used, the correlated and uncorrelated luminosity
  components should be preserved explicitly rather than collapsed into a single number.

## References

- CMS good luminosity section JSON guide:
  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGoodLumiSectionsJSONFile
- CMS public luminosity results:
  https://twiki.cern.ch/twiki/bin/view/CMSPublic/PhysicsResultsLUM
- CMS public data quality information:
  https://twiki.cern.ch/twiki/bin/view/CMSPublic/DataQuality
- CMS Run 2 Luminosity Recommendations
  https://twiki.cern.ch/twiki/bin/viewauth/CMS/LumiRecommendationsRun2?rev=2#Combination_and_correlations
