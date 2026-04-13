# ST_entanglement

`ST_entanglement` is a CMS analysis repository built on top of `columnflow` and `law`.
It contains the analysis-specific layer for a Run 2 single-top study, while relying on pinned
framework submodules for workflow orchestration, dataset metadata, and columnar processing.

The analysis focus is **single top t-channel production**. Other single-top production modes are
treated as background, together with the major backgrounds **ttbar**, **W+jets**, and **QCD**.

## Framework Overview

This repository follows the standard `columnflow` analysis model:

- `law` handles workflow orchestration, task dependencies, reproducible outputs, and local or
  remote execution
- `columnflow` provides the columnar analysis pipeline for calibration, selection, reduction,
  column production, categorization, histogramming, plotting, ML, and inference
- `cmsdb` provides CMS campaign and dataset metadata used to construct analysis configurations

The repository itself stays intentionally thin and contains only the analysis-specific code and
configuration needed on top of those shared tools.

## Repository Structure

- `setup.sh`: analysis bootstrap and environment setup
- `law.cfg`: central workflow and analysis configuration
- `st_entanglement/config/`: analysis and campaign-specific configuration
- `st_entanglement/calibration/`: calibration modules
- `st_entanglement/selection/`: event selection logic
- `st_entanglement/reduction/`: reduced event content definitions
- `st_entanglement/production/`: derived columns and event weights
- `st_entanglement/categorization/`: event categorization
- `st_entanglement/histogramming/`: histogram production logic
- `st_entanglement/plotting/`: plotting helpers
- `st_entanglement/ml/`: machine learning modules
- `st_entanglement/inference/`: inference model definitions
- `st_entanglement/tasks/`: lightweight custom task definitions
- `modules/columnflow`: pinned `columnflow` framework submodule
- `modules/cmsdb`: pinned `cmsdb` metadata submodule

## Physics Scope

The long-term target is a **full CMS Run 2 NanoAOD analysis** of single top t-channel production.

The framework is meant to support:

- full Run 2 campaign coverage
- signal-region and control-region selections
- background-constraining categories
- systematic variations and shifted event content
- histogram production, plotting, and downstream statistical inference

The current default configuration in the repo is still a development baseline based on a Run 2
2017 NanoAOD v9 setup, but the framework is intended to grow beyond that into a full Run 2
analysis.

## Getting Started

Initialize the repository and its pinned framework dependencies:

```bash
git submodule update --init --recursive
```

Set up the analysis environment:

```bash
source setup.sh
```

From there, `law` / `columnflow` tasks can be run using the configuration defined in `law.cfg`
and `st_entanglement.config.analysis_st_entanglement`.

## Dependencies

Core upstream projects used by this repository:

- [columnflow](https://github.com/columnflow/columnflow/)
- [law](https://github.com/riga/law)
- [cmsdb](https://github.com/uhh-cms/cmsdb)
- [order](https://github.com/riga/order)
- [luigi](https://github.com/spotify/luigi)

## Documentation

The project-level specification is documented in [docs/spec.md](docs/spec.md).
