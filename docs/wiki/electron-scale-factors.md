# Entry 3: Electron Scale Factors

## POG Recommendation

For electrons, the standard recommendation is to use the **EGamma POG** correctionlib payloads in
the `electron.json.gz` files and evaluate the appropriate correction set for the chosen electron
working point.

For Run 2 UL, the commonly used correction set is:

- `UL-Electron-ID-SF`

with working points such as reconstruction or ID/isolation working points selected through the
`WorkingPoint` argument.

## ColumnFlow Interface Available In The Repo

Unlike the muon case, electron scale factors are not yet configured in the analysis module, but
the ColumnFlow interface is already available in the vendored framework code.

The relevant upstream implementation is:

- `columnflow.production.cms.electron.electron_weights`

It expects:

- an external file such as `cfg.x.external_files["electron_sf"]`
- an `ElectronSFConfig` object, typically exposed as `cfg.x.electron_sf` or
  `cfg.x.electron_sf_names`

The producer then evaluates the configured correction and stores:

- `electron_weight`
- `electron_weight_up`
- `electron_weight_down`

## Current Repo Status

At the moment, this repository does not yet define:

- `cfg.x.external_files["electron_sf"]`
- `cfg.x.electron_sf` or `cfg.x.electron_sf_names`
- a producer call to `electron_weights` inside `st_entanglement/production/example.py`
- analysis shifts analogous to the existing muon `mu_up` / `mu_down` weight shifts

So the correct description for `ST_entanglement` is:

- the ColumnFlow interface for electron SFs already exists upstream
- this analysis has not wired it into its config and default producer yet

That distinction matters because the wiki should document both the recommended POG source and the
fact that, for electrons, the analysis-side hookup is still a pending integration step.

## References

- correctionlib usage example for Run 2 UL electron SFs:
  https://dasanalysissystem.docs.cern.ch/namespaceelectronExample.html
- EGamma Run 2 recommendations landing page:
  https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018
- EGamma Run 2 Recommendations (alt page):
  https://twiki.cern.ch/twiki/bin/view/CMS/EgammaRunIIRecommendations
