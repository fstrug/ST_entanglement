# Entry 6: ColumnFlow Notes

## The `nMuon` Lesson

In this analysis, the input datatier is NanoAOD. NanoAOD contains an `nMuon` branch that stores the
number of muons in each event, so it is tempting to assume that plotting `nMuon` should work as soon
as the branch exists in the source file.

That is not quite how ColumnFlow sees the data. The `--variables` argument of tasks such as
`cf.PlotVariables1D` refers to variables registered in the analysis config, not directly to
arbitrary NanoAOD branch names. Therefore, a command like

```bash
law run cf.PlotVariables1D --variables nMuon
```

requires a corresponding `cfg.add_variable(...)` entry named `nMuon`.

The first natural attempt is to register the variable with the NanoAOD branch name as its
expression:

```python
cfg.add_variable(
    name="nMuon",
    expression="nMuon",
    binning=(8, -0.5, 7.5),
    x_title="Number of muons",
)
```

For `nMuon`, this failed in practice. The branch exists in the original NanoAOD input, but the event
arrays used by the downstream histogramming task did not contain a normal field named `nMuon`.
Awkward therefore raised:

```text
FieldNotFoundError: no field 'nMuon'
```

Adding `nMuon` to `keep_columns`, changing the default reducer, or adding `nMuon` to the example
reducer's `uses`/`produces` did not fix this. The reducer could not receive a column named `nMuon`
because the NanoEvents reader did not expose that count branch as a normal event field in the first
place.

## NanoAOD Count Branches and NanoEvents Collections

NanoAOD stores count branches such as `nMuon`, `nElectron`, and `nJet`. These branches describe
the number of entries in the corresponding jagged object collections.

When ColumnFlow reads NanoAOD through the NanoEvents/coffea-style interface, these count branches
are not always exposed downstream as ordinary event fields. Instead, they can be consumed by the
reader to build the jagged collection structure, such as `events.Muon`.

For count branches like `nMuon`, the robust ColumnFlow expression is to count the jagged collection
entries that NanoEvents has already built:

```python
cfg.add_variable(
    name="nMuon",
    expression=lambda events: ak.num(events.Muon, axis=1),
    binning=(8, -0.5, 7.5),
    x_title="Number of muons",
    aux={"inputs": ["Muon.pt"]},
)
```

The `aux={"inputs": ["Muon.pt"]}` entry tells `CreateHistograms` to load enough of the `Muon`
collection for the callable expression to see `events.Muon`. The expression then counts the jagged
collection entries. Conceptually, this is using the collection structure that NanoEvents built from
the original count branch, not applying a new physics definition of the muon selection.

This definition was tested with:

```bash
source setup.sh && law run cf.PlotVariables1D --version v1 --calibrators example --selector baseline --producer example --datasets 'st*' --variables nMuon
```

After clearing the histogram and plot outputs, `CreateHistograms`, `MergeHistograms`, and
`PlotVariables1D` all completed successfully for `nMuon`.

## Ordinary Scalar Branches

The `nMuon` case should not be generalized to every NanoAOD branch. For ordinary scalar columns
that remain visible in the downstream event files, the branch name can still be used directly as
the variable expression. For example:

```python
cfg.add_variable(
    name="run",
    expression="run",
    binning=(1, 100000.0, 500000.0),
    x_title="Run number",
)
```

The `name` is what ColumnFlow resolves from `--variables`. The `expression` tells ColumnFlow which
column or expression to read when filling the histogram. The binning and title define how the
histogram should be created and displayed.

## Why This Matters

ColumnFlow has several processing stages. The original NanoAOD file is read early, but downstream
tasks usually work on reduced or produced event files. A branch existing in NanoAOD is therefore
not enough by itself. The branch must also survive into the event content used by the task that
needs it.

For plot variables based on original NanoAOD branches, check both:

- the variable is registered with `cfg.add_variable`
- the required branch is kept in `cfg.x.keep_columns` for the relevant processing step

For ordinary scalar branches, this can mean keeping the branch during reduction:

```python
cfg.x.keep_columns = DotDict.wrap({
    "cf.ReduceEvents": {
        ...
        "someScalarBranch",
        ...
    },
})
```

Without this, the variable may be defined in the config, but the reduced files used by
histogramming can still be missing the underlying column. For NanoAOD count branches such as
`nMuon`, however, this branch-preservation rule is not the whole story: keeping the raw branch may
still not be enough because the reader may represent the information only through the jagged
collection layout.

## The Cutflow Example

A related issue appeared with the configured variable `cf_jet1_pt`:

```python
cfg.add_variable(
    name="cf_jet1_pt",
    expression="cutflow.jet1_pt",
    ...
)
```

This variable points to a ColumnFlow-created column, not a NanoAOD branch. The column is produced
during selection as `cutflow.jet1_pt`, but the reduction config intentionally skips cutflow
columns:

```python
ColumnCollection.ALL_FROM_SELECTOR,
skip_column("cutflow.*"),
```

When a normal histogramming task tries to plot `cf_jet1_pt` from reduced event files, Awkward can
raise an error like:

```text
FieldNotFoundError: no field 'cutflow'
```

The meaning is simple: the variable definition asks for `cutflow.jet1_pt`, but the event record
being read no longer contains a `cutflow` field.

## Adding Cutflow Variables for Plotting

Cutflow variables such as `cf_jet1_pt` or `cf_muon_pt` follow a different pattern from ordinary
plot variables. Registering a config variable alone is not enough. The quantity must first be
created as a produced column under the `cutflow.*` namespace.

The workflow has three parts:

1. Add the cutflow column in `st_entanglement/production/example.py` inside
   `cutflow_features(...)`.
2. Declare that column in the producer `produces={...}` set, and declare any needed input object
   columns in `uses={...}`.
3. Register the plotting variable in the config with `expression="cutflow.<name>"`.

For example, `cf_jet1_pt` works because `cutflow_features(...)` produces the column
`cutflow.jet1_pt`:

```python
@producer(
    uses={mc_weight, category_ids, "Jet.{pt,phi}"},
    produces={mc_weight, category_ids, "cutflow.jet1_pt"},
)
def cutflow_features(...):
    ...
    reduced_events = create_collections_from_masks(events, object_masks)
    ...
    events = set_ak_column(
        events,
        "cutflow.jet1_pt",
        Route("Jet.pt[:,0]").apply(reduced_events, EMPTY_FLOAT),
    )
```

and the config then exposes it for plotting:

```python
cfg.add_variable(
    name="cf_jet1_pt",
    expression="cutflow.jet1_pt",
    ...
)
```

The same pattern is required for additional cutflow variables. For `cf_muon_pt`, the producer must
explicitly create `cutflow.muon_pt`:

```python
@producer(
    uses={mc_weight, category_ids, "Jet.{pt,phi}", "Muon.{pt,eta,phi}"},
    produces={mc_weight, category_ids, "cutflow.jet1_pt", "cutflow.muon_pt"},
)
def cutflow_features(...):
    ...
    reduced_events = create_collections_from_masks(events, object_masks)
    ...
    events = set_ak_column(
        events,
        "cutflow.muon_pt",
        Route("Muon.pt[:,0]").apply(reduced_events, EMPTY_FLOAT),
    )
```

and only then will a config variable such as

```python
cfg.add_variable(
    name="cf_muon_pt",
    expression="cutflow.muon_pt",
    ...
)
```

work reliably.

Two details matter in practice:

- Read from `reduced_events` rather than the unreduced `events` object when the quantity should
  follow the selected/masked collections from the selector.
- Keep the producer `uses` and `produces` declarations synchronized with the new cutflow column.
  If the config variable exists but the producer never created `cutflow.<name>`, plotting tasks can
  fail because the `cutflow` field is missing.

In short: for cutflow plotting variables, always add both the producer-side `cutflow.<name>` column
and the config-side `cfg.add_variable(...)` entry.


## Practical Rule

When adding a quantity for plotting, distinguish three things:

- **NanoAOD branch**: a quantity stored in the original input file
- **kept column**: a quantity preserved into reduced or produced event files
- **ColumnFlow variable**: a named plotting definition registered with `cfg.add_variable`

For an ordinary scalar NanoAOD branch, all three layers have to line up for plotting to work: the
branch must exist upstream, survive into the downstream event content, and be registered as a
ColumnFlow variable. For NanoAOD count branches such as `nMuon`, the original branch may instead be
represented through the jagged collection layout, so the variable should use that collection rather
than assuming the raw count branch is still readable.

## Recommended Workflow

When adding a new plot variable:

1. Decide whether the quantity comes from NanoAOD or from a ColumnFlow producer/selector.
2. For ordinary scalar branches, add or confirm the needed entry in `cfg.x.keep_columns`.
3. Register the variable with `cfg.add_variable`.
4. Run a focused plotting command with `--variables <name>`.

For simple scalar NanoAOD branches that remain visible in the downstream event arrays, the variable
expression can often be the branch name directly. For NanoAOD count branches and object-derived
quantities, a lambda expression or producer output may be more robust.

## Cutflow Memory Leak

The command

```bash
source setup.sh && law run cf.PlotCutflow --version v1 --dataset 'st*' --selector-steps jet,muon,MET
```

previously crashed while running `cf.CreateCutflowHistograms` for
`st_tchannel_t_4f_powheg`. The failure is not a Python exception from the task code. The inner
sandbox process is killed with exit code `-9`, and the outer `law` process reports:

```text
Exception: sandbox 'bash::$CF_BASE/sandboxes/venv_columnar_dev.sh' failed with exit code -9
```

To define the problem more precisely, the command was rerun with a memory monitor attached to the
process tree. The wrapper processes stayed essentially flat, around 80-95 MB RSS. The memory growth
was isolated to the inner `CreateCutflowHistograms` process while it was still processing the first
chunk:

| Time | State | RSS |
|---|---|---:|
| 19:39:03 | sandbox just started | 26 MB |
| 19:39:08 | loading/importing | 106 MB |
| 19:39:13 | before chunk processing | 148 MB |
| 19:39:18 | `handling chunk 0` | 759 MB |
| 19:39:23 | still chunk 0 | 2.5 GB |
| 19:39:28 | still chunk 0 | 4.0 GB |
| 19:39:34 | still chunk 0 | 5.6 GB |
| 19:39:39 | still chunk 0 | 7.1 GB |
| 19:39:49 | still chunk 0 | 15.9 GB |
| 19:39:54 | still chunk 0 | 27.2 GB |
| 19:39:59 | still chunk 0 | 32.0 GB |
| 19:40:04 | still chunk 0 | 33.0 GB |
| 19:40:17 | last sample before death | 34.1 GB |

This means the problem to solve is a very large allocation or leak inside
`CreateCutflowHistograms.run`, already during `handling chunk 0`. It is not a slow accumulation
over many chunks, and it is not caused by the wrapper `law` processes.

Two mitigation/debugging fixes have already been made:

- In `law.cfg`, cutflow histogram creation now uses smaller chunks and a single IO worker:

```diff
diff --git a/law.cfg b/law.cfg
--- a/law.cfg
+++ b/law.cfg
@@
 # ChunkedIOHandler defaults
 chunked_io_chunk_size: 100000
 chunked_io_pool_size: 2
 chunked_io_debug: False
 
+# Keep cutflow histogram creation memory-light.  The default 100k-event chunks
+# can get the sandbox killed while repeatedly filling per-step histograms.
+cf.CreateCutflowHistograms__chunked_io_chunk_size: 20000
+cf.CreateCutflowHistograms__chunked_io_pool_size: 1
+
 # settings for merging parquet files in several locations
 merging_row_group_size: 50000
```

- In the local `modules/columnflow` checkout, `MergeSelectionMasks.merge` now passes a row-group
  target to `law.pyarrow.merge_parquet_task`:

```diff
diff --git a/columnflow/tasks/selection.py b/columnflow/tasks/selection.py
--- a/columnflow/tasks/selection.py
+++ b/columnflow/tasks/selection.py
@@
         law.pyarrow.merge_parquet_task(
-            self, inputs, output["masks"], writer_opts=self.get_parquet_writer_opts(),
+            self,
+            inputs,
+            output["masks"],
+            writer_opts=self.get_parquet_writer_opts(),
+            target_row_group_size=law.config.get_expanded_int("analysis", "merging_row_group_size", 50_000),
         )
```

The second change fixed a separate row-group issue. Before rebuilding, the merged
`masks.parquet` file had only 2 row groups for 1,942,000 events. After deleting the stale generated
`masks.parquet` and rerunning, it was rebuilt with 39 row groups of 50,000 rows. This is better for
chunked reading, but it did not by itself remove the `CreateCutflowHistograms` memory blow-up.

## Removing `discrete_x=True`

The actual source of the cutflow memory blow-up was the `event` bookkeeping variable definition.
It used:

```python
cfg.add_variable(
    name="event",
    expression="event",
    binning=(1, 0.0, 1.0e9),
    x_title="Event number",
    discrete_x=True,
)
```

For `discrete_x=True`, ColumnFlow builds a `hist.axis.Integer` from the first to the last bin edge.
For `event`, that meant an integer axis spanning roughly `0` to `1e9`, i.e. an enormous histogram
axis. The process was then killed while filling the first cutflow chunk.

The fix was to remove `discrete_x=True` from the bookkeeping variables `event`, `run`, and `lumi`:

```diff
diff --git a/st_entanglement/config/analysis_st_entanglement.py b/st_entanglement/config/analysis_st_entanglement.py
--- a/st_entanglement/config/analysis_st_entanglement.py
+++ b/st_entanglement/config/analysis_st_entanglement.py
@@
 cfg.add_variable(
     name="event",
     expression="event",
     binning=(1, 0.0, 1.0e9),
     x_title="Event number",
-    discrete_x=True,
 )
 cfg.add_variable(
     name="run",
     expression="run",
     binning=(1, 100000.0, 500000.0),
     x_title="Run number",
-    discrete_x=True,
 )
 cfg.add_variable(
     name="lumi",
     expression="luminosityBlock",
     binning=(1, 0.0, 5000.0),
     x_title="Luminosity block",
-    discrete_x=True,
 )
```

These variables are used by cutflow tasks mainly as one-bin counting variables, so regular one-bin
axes are sufficient and avoid the huge integer-axis allocation.

After this change, the same cutflow command processed all 98 chunks successfully. The sampled
memory stayed around a few hundred MB instead of climbing to about 34 GB.

## Matplotlib Format Error

After the memory issue was fixed, the workflow reached the actual plotting step and exposed a
separate Matplotlib error:

```text
AttributeError: This method only works with the ScalarFormatter
```

This happened because `plot_all()` applies a generic x-axis scientific-formatting default:

```python
"xticklabelformat": {"style": "sci", "useMathText": True}
```

Cutflow plots do not have a normal numeric x axis. Their x axis contains selection-step labels such
as `Initial`, `jet`, `muon`, and `MET`. Once Matplotlib uses a categorical/string-style formatter
for those labels, calling `ticklabel_format(..., style="sci")` is invalid.

The local ColumnFlow fix was to disable scientific formatting for the cutflow x axis in the
cutflow plot style config:

```diff
diff --git a/columnflow/plotting/plot_functions_1d.py b/columnflow/plotting/plot_functions_1d.py
--- a/columnflow/plotting/plot_functions_1d.py
+++ b/columnflow/plotting/plot_functions_1d.py
@@
         "ax_cfg": {
             "ylabel": "Selection efficiency" if shape_norm else "Selection yield",
             "xlabel": "Selection step",
             "xticklabels": xticklabels,
+            "xticklabelformat": None,
+            "xrotation": 45,
             "yscale": yscale,
         },
```

This disables scientific notation only for the cutflow x axis. It does not change any histogram
contents, yields, or efficiencies. The `xrotation` line belongs to the clipping fix below, but it is
part of the same local hunk.

## Plot Clipping Error

Once the cutflow plot was produced, the x-axis title `Selection step` was visibly clipped at the
bottom of the saved PDF. The underlying ordering was awkward: `plot_all()` calls `tight_layout()`,
but `plot_cutflow()` then adjusts the cutflow tick labels afterwards. That means the layout
calculation can miss the final rotated labels and x-axis title.

The first part of the fix was to move rotation into the style config and call `fig.tight_layout()`
after applying the final cutflow tick labels:

```diff
diff --git a/columnflow/plotting/plot_functions_1d.py b/columnflow/plotting/plot_functions_1d.py
--- a/columnflow/plotting/plot_functions_1d.py
+++ b/columnflow/plotting/plot_functions_1d.py
@@
         "ax_cfg": {
             "ylabel": "Selection efficiency" if shape_norm else "Selection yield",
             "xlabel": "Selection step",
             "xticklabels": xticklabels,
+            "xticklabelformat": None,
+            "xrotation": 45,
             "yscale": yscale,
         },
@@
     fig, (ax,) = plot_all(plot_config, style_config, **kwargs)
-
     ax.set_xticklabels(xticklabels, rotation=45, ha="right")
-
+    fig.tight_layout()
     return fig, (ax,)
```

This improved the order of operations, but rendered checks showed the CMS-style figure could still
clip the bottom text. The final local fix was to save `PlotCutflow` outputs with
`bbox_inches="tight"`:

```diff
diff --git a/columnflow/tasks/cutflow.py b/columnflow/tasks/cutflow.py
--- a/columnflow/tasks/cutflow.py
+++ b/columnflow/tasks/cutflow.py
@@
             # save the plot
             for outp in self.output()["plots"]:
-                outp.dump(fig, formatter="mpl")
+                outp.dump(fig, formatter="mpl", bbox_inches="tight")
```

This is dynamic: instead of hard-coding a larger bottom margin, Matplotlib computes the actual
bounding box of the figure contents and expands the saved PDF to include all text artists. This was
verified by rendering both the nominal and shape-normalized PDFs.

The shape-normalized check was run as:

```bash
law run cf.PlotCutflow --version v1 --dataset 'st*' --selector-steps jet,muon,MET --shape-norm --plot-suffix shape_norm
```

Both the nominal cutflow and the shape-normalized cutflow completed successfully after these fixes.
 
