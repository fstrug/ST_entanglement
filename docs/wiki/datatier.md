# Entry 1: Datatier

## Working Datatier

The analysis is built around the **CMS NanoAOD** datatier for **Run 2**.

In the context of this repository, that means:

- centrally produced CMS NanoAOD samples are the primary event input
- the relevant event content is accessed as ROOT `TTree` data
- the analysis is performed with columnar tools such as `uproot`, `awkward`, and `columnflow`
- campaign and dataset metadata are managed through `cmsdb` and `order`

The current development setup in the repository is based on a Run 2 2017 NanoAOD v9 example
configuration, but the intended analysis scope is full Run 2 NanoAOD.

For this analysis, **NanoAOD v9** should be treated as the recommended Run 2 NanoAOD baseline
across the full Run 2 data-taking period, i.e. **2016, 2017, and 2018**.

## What NanoAOD Is

NanoAOD is a compact CMS analysis format designed to store the event content needed for many
physics analyses in a lightweight, analysis-friendly form.

Compared with AOD and MiniAOD:

- NanoAOD is smaller and more analysis-oriented
- it stores data in standard types inside ROOT TTrees rather than CMS EDM C++ objects
- it keeps a reduced set of high-level quantities per object
- much of the lower-level detector and reconstruction detail present in AOD and MiniAOD is removed

This is one of the main reasons it works naturally with modern columnar analysis frameworks.

## Structural View

A NanoAOD file is typically organized around several ROOT trees, in particular:

- `Events`: the main per-event analysis content
- `Runs`: run-level metadata and aggregated information
- `LuminosityBlocks`: lumi-section-level metadata
- additional metadata trees such as `MetaData` or `ParameterSets`

Within the `Events` tree:

- scalar branches store one value per event
- jagged branches store per-object values, such as one entry per muon or jet in the event
- physics objects are represented through coordinated branch groups like `Muon_*`, `Jet_*`,
  `Electron_*`, and so on

For analysis work, this means NanoAOD behaves much more like a structured ntuple than like a full
CMSSW EDM event.

## What Is Preserved and What Is Dropped

NanoAOD keeps the information that is broadly useful for analysis, but does so in a compressed,
high-level form.

Typical features of NanoAOD are:

- high-level reconstructed objects such as leptons, jets, MET, and event-level quantities
- precomputed identification or selection-related quantities for many objects
- generator-level information for simulation samples
- reduced precision and reduced content compared with MiniAOD

Typical things that are reduced or removed relative to upstream formats are:

- much of the lower-level detector detail
- many reconstruction intermediates
- particle-flow candidate collections in standard NanoAOD

This tradeoff is deliberate: NanoAOD is designed to be sufficient for a large fraction of CMS
analyses while remaining lightweight enough for large-scale processing.

## Relation to AOD and MiniAOD

For analysis planning, it is useful to think of the CMS Run 2 formats roughly as:

- `AOD` / `AODSIM`: large, reconstruction-rich formats with broad event content
- `MiniAOD` / `MiniAODSIM`: reduced CMS EDM formats intended for most physics analyses
- `NanoAOD` / `NANOAODSIM`: compact ntuple-like formats optimized for fast analysis

For this analysis:

- NanoAOD is the working datatier
- MiniAOD is conceptually the upstream source format from which NanoAOD is derived
- if a quantity is absent from NanoAOD, recovering it generally requires either a dedicated
  extension, a private derivation, or returning to MiniAOD-level inputs

## Important Analysis Consequences

Using NanoAOD has a few practical consequences for `ST_entanglement`:

- object definitions must be based on the branches and IDs that NanoAOD exposes
- some analysis choices are constrained by what was centrally stored
- per-event processing is naturally suited to awkward-array based workflows
- central CMS object corrections and scale factors are especially valuable because the format is
  already high level
- any missing information has to be handled deliberately rather than assumed to be recoverable

For a `columnflow` analysis, NanoAOD is a particularly good fit because the branch structure maps
well to columnar processing and object-wise transformations.

## Definitions Used in This Analysis

For the purpose of this repository, the following terminology will be used consistently:

- **datatier**:
  the CMS event-data format used as the starting point of the analysis
- **NanoAOD**:
  the CMS Run 2 ntuple-like datatier used as the main analysis input
- **branch**:
  a stored quantity in a ROOT TTree, either scalar or per-object
- **collection**:
  a set of related branches representing one physics-object family, such as `Jet` or `Muon`
- **event content**:
  the total set of branches available to the analysis at a given stage
- **reduced event content**:
  the subset of branches kept after selection/reduction for downstream steps

## Scope Note

This entry describes the analysis datatier at the level relevant for framework and workflow
choices. It does not yet document:

- the exact NanoAOD version policy across all Run 2 eras
- branch-by-branch object content used by the analysis
- the mapping from NanoAOD branches to analysis-specific reduced columns

Those should be added in later entries.

## References

- CMS Open Data, "Getting Started with CMS NanoAOD Open Data":
  https://opendata.cern.ch/docs/cms-getting-started-nanoaod
- CERN Open Data Portal, "About CMS", data-format overview:
  https://opendata.cern.ch/docs/about-cms
- CMS NanoAOD Workbook:
  https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
- CMS NanoAOD documentation repository:
  https://gitlab.cern.ch/cms-crossPOG/nanoaod-doc
