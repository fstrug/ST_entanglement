# ST_entanglement Specification

## Purpose

`ST_entanglement` is a CMS analysis repository built on top of `columnflow` and `law`.
It provides the analysis-specific configuration, physics objects, selections, derived columns,
categorization, histogramming, plotting, and inference logic needed to study spin-entanglement-
related observables in single top production.

The repository is intentionally thin: common workflow, IO, remote execution, dataset handling,
columnar processing, and many CMS-specific utilities are inherited from upstream dependencies,
while this repo contains only the analysis layer that defines what is processed and how it is
interpreted.

## Framework Basis

### `law`

`law` provides the workflow engine and orchestration layer. In this repository it is responsible
for:

- task definitions and dependency resolution
- local and remote workflow execution
- reproducible outputs and target handling
- integration with batch systems such as HTCondor and Slurm
- configuration via `law.cfg`

### `columnflow`

`columnflow` provides the columnar analysis framework on top of `law`. In this repository it is
used for:

- campaign, process, dataset, and shift configuration
- event calibration, selection, reduction, and column production
- histogram production and plotting
- ML and inference task integration
- CMS-specific helpers for NanoAOD-based analyses

### `cmsdb`

`cmsdb` provides campaign and dataset metadata used to construct the analysis configuration. The
analysis is intended to run on CMS Run 2 NanoAOD campaigns, with concrete campaign definitions
imported from `cmsdb`.

### `order`

`order` provides the object model used to manage analysis configuration in a structured way. In
this repository it underpins the bookkeeping of:

- analyses
- campaigns
- datasets
- physics processes and cross sections
- channels
- categories
- variables
- systematic shifts

Within a `columnflow`-based analysis, `order` is the configuration layer that makes these entities
explicit Python objects rather than scattered dictionaries or ad hoc config fragments. That is why
the central analysis definition in `st_entanglement.config.analysis_st_entanglement` is built
around an `order.Analysis` instance and derived config objects.

## Repository Scope

The repository should contain:

- the analysis bootstrap and environment setup in `setup.sh`
- global workflow configuration in `law.cfg`
- analysis configuration in `st_entanglement/config/`
- analysis modules for:
  - calibration
  - selection
  - reduction
  - production
  - categorization
  - histogramming
  - plotting
  - ML
  - inference
- lightweight task wrappers in `st_entanglement/tasks/`
- tests and example sandboxes

The repository should not duplicate generic framework logic already provided by `columnflow`,
`law`, or `cmsdb` unless a clear analysis-specific patch or extension is needed.

## Physics Context

### Signal Process

The signal process is **single top production in the t-channel**.

The main signal datasets and categories should therefore be centered on the t-channel production
mode, with event selection and observables chosen to retain sensitivity to the kinematics and spin
information of this process.

### Background Processes

The analysis must distinguish the t-channel signal from several important backgrounds:

- **other single top production modes**, treated as background relative to the t-channel signal
- **ttbar**, one of the dominant backgrounds
- **W+jets**, a major background especially in lepton-plus-jets event topologies
- **QCD multijet**, an important background due to fake or non-prompt leptons and mismeasured event activity

Where useful, the analysis may further separate backgrounds into subcategories for control-region
studies, systematic handling, or inference.

### Data-Taking Context

The target scope of the analysis is **CMS Run 2 NanoAOD** in general, rather than a single year
only. The framework should support the full Run 2 data-taking period and its corresponding Monte
Carlo campaigns through `cmsdb`-provided campaign definitions.

The current repository still contains an example default configuration wired to **Run 2 2017
NanoAOD v9** via `st_entanglement.config.analysis_st_entanglement`, but this should be understood
as a development baseline rather than the intended final physics scope.

The framework should scale to a full Run 2 analysis campaign with expanded datasets, categories,
eras, and systematic variations.

## Analysis Model

The repository should follow the standard `columnflow` analysis flow:

1. configure campaigns, processes, datasets, shifts, and defaults
2. calibrate event content and CMS object corrections
3. apply event selection for the signal region and control regions
4. reduce event content to the columns needed downstream
5. produce high-level analysis columns and weights
6. categorize events
7. create histograms and derived statistical inputs
8. run plotting, ML, or inference tasks as needed

Each stage should be modular, composable, and reusable through `columnflow` conventions.

## Configuration Requirements

The central analysis configuration should:

- define the default analysis object and default config in `law.cfg`
- import campaign and dataset definitions from `cmsdb`
- register the physics processes relevant to the measurement
- declare the default signal and background datasets
- define standard shifts and aliases for systematic variations
- configure default calibrators, selectors, reducers, producers, histogram producers, and inference modules
- expose process, dataset, category, variable, and shift groups for workflow control

The default configuration should remain usable as a development baseline while making it easy to
extend toward a full production analysis.

## Workflow and Execution

The framework should support:

- local execution for development and debugging
- remote execution via `law` workflows
- EOS/WLCG-backed IO through the configured file systems
- reproducible software environments via the provided sandboxes
- submodule-based dependency pinning for framework reproducibility

The repository setup should continue to rely on pinned versions of:

- `modules/columnflow`
- `modules/cmsdb`

This ensures that workflow behavior, metadata definitions, and task interfaces remain reproducible
across users and over time.

## Selection and Categorization Goals

The analysis selection should be designed around the topology of single top t-channel events and
the rejection of the dominant backgrounds. In practice, this means the framework should support:

- lepton-based event selections suitable for single-top analyses
- jet and b-tag requirements that separate signal-like from background-like topologies
- dedicated control categories for `ttbar`, `W+jets`, and QCD validation
- flexible categorization for studies of signal purity and systematic effects

The exact working points and category definitions may evolve, but the framework should make such
changes local to the analysis modules rather than requiring changes to the underlying workflow
engine.

## Histogramming, Plotting, and Inference

The repository should support the production of:

- control plots for physics validation
- cutflow and diagnostic histograms
- signal-versus-background discriminating observables
- inputs for statistical inference or downstream interpretation

Inference modules should be able to treat t-channel single top as signal and all other listed
processes as background unless a dedicated study explicitly defines an alternative signal model.

## Software Design Principles

The code in this repository should remain:

- modular, with one clear responsibility per analysis module
- declarative where possible, using `columnflow` configuration patterns
- reproducible through pinned dependencies and sandboxed execution
- analysis-focused, avoiding reimplementation of generic framework functionality
- easy to extend as the physics model, datasets, and categorization strategy mature

## Near-Term Evolution

The current repository is a starting point and should evolve toward:

- a fuller signal and background process configuration
- expanded dataset coverage for all relevant single-top and background samples
- dedicated control-region definitions
- explicit treatment of systematic uncertainties
- analysis-specific observables for spin-entanglement studies in single top t-channel production

This specification should be read as the target direction for the repository structure and analysis
logic, with `columnflow` and `law` providing the workflow backbone and the `st_entanglement`
package providing the analysis-specific implementation.
