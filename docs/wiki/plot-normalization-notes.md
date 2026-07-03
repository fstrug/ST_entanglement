# Entry 7: Plot Normalization Notes

## Question

An apparent inconsistency showed up between the cutflow-style outputs and the 1D variable plots:

- the cutflow results suggested more events in `st_tchannel_t`
- the `PlotVariables1D` output suggested more events in `st_tchannel_tbar`

The relevant question was whether these two plotting paths apply luminosity and cross section
normalization in the same way.

## Short Answer

They do not, at least not in the current configuration.

- `PlotVariables1D` is currently unweighted by default in this repo
- `PlotCutflow` uses `normalization_weight` and is therefore luminosity/cross-section scaled for MC
- the printed selection stats are a third thing again: they report raw event counts and sums of
  `mc_weight`, not luminosity-scaled yields

So these outputs should not be expected to agree numerically unless they are configured to use the
same weighting convention.

## Why `PlotVariables1D` Is Currently Unweighted

The analysis config sets:

```python
cfg.x.default_hist_producer = "cf_default"
```

The built-in `cf_default` histogram producer returns unit weights:

```python
return events, ak.Array(np.ones(len(events), dtype=np.float32))
```

That means the default `CreateHistograms -> MergeHistograms -> PlotVariables1D` chain fills
histograms with raw event entries rather than with luminosity-normalized MC yields.

In other words, the default 1D plots show event counts after selection, but not the expected event
yield after applying

```text
L * sigma / sumw
```

normalization.

## Why `PlotCutflow` Is Weighted

The cutflow path is different.

Before `PlotCutflow` runs, `MergeSelectionMasks` computes and writes a `normalization_weight`
column for MC events. `CreateCutflowHistograms` then reads that column and uses it as the event
weight when filling the cutflow histograms.

That `normalization_weight` is computed from:

```text
normalization_weight = mc_weight * (lumi * xsec / sum_mc_weight)
```

with the exact lookup-table factor built from:

```text
weight = norm_factor * xsec * lumi / sum_weights
```

Therefore, `PlotCutflow` for MC is effectively plotting luminosity- and cross-section-scaled
selection yields.

## Why The Printed Selection Stats Are Different Again

The selection stats output printed by `SelectEvents` and stored in `stats.json` is not the same as
`PlotCutflow`.

It reports:

- `num_events`
- `num_events_selected`
- `sum_mc_weight`
- `sum_mc_weight_selected`

This means it mixes:

- raw event counts
- sums of generator weights

but it does not apply the full `normalization_weight` used by `PlotCutflow`.

So if the comparison was made between `stats.json` and `PlotVariables1D`, that is a comparison
between two differently normalized outputs. If the comparison was made between `PlotCutflow` and
`PlotVariables1D`, that is also a comparison between two differently normalized outputs in the
current default setup.

## How To Make `PlotVariables1D` Use Luminosity Scaling

This repo already contains a custom histogram producer named `example` that multiplies:

- `normalization_weight`
- `muon_weight`

for MC.

So a weighted 1D plotting command can be run as:

```bash
law run cf.PlotVariables1D ... --hist-producer example
```

If this should become the default behavior, the config can be changed from:

```python
cfg.x.default_hist_producer = "cf_default"
```

to:

```python
cfg.x.default_hist_producer = "example"
```

## Practical Interpretation For The Single-Top Comparison

The observed inversion between `st_tchannel_t` and `st_tchannel_tbar` is therefore not, by itself,
evidence of a bug in the process definitions.

A more likely explanation is:

- the unweighted selected event count is larger for one process
- the luminosity-normalized expected yield is larger for the other

This can happen naturally when the processes differ in:

- generated event counts
- summed generator weights
- cross sections
- additional scale factors included in the weighted path

For a physics comparison of expected MC yields, the weighted convention is the meaningful one. For
workflow debugging, bookkeeping, or acceptance studies, the unweighted convention can still be
useful, but it should be interpreted accordingly.

## Practical Rule

When comparing yields in this analysis, first identify which of the following conventions is being
used:

- raw selected event counts
- sums of `mc_weight`
- full event yields using `normalization_weight`
- full event yields using `normalization_weight` times additional scale factors

Only outputs produced with the same convention should be compared directly.
