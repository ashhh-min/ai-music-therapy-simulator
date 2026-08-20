# Chart Interpretation Guide

This guide explains what each dashboard chart shows, what it can and cannot support, and how to read it honestly. Every chart in this project summarizes **synthetic simulation output**. No chart, title, axis, or export constitutes evidence about real children, real therapy, or clinical effectiveness.

## Standing rules for all charts

- Titles and captions are **descriptive** ("mean composite under identical music"), never causal or outcome-based ("music reduced anxiety").
- Sample counts (`n_trials`) and engine labels (deterministic / openai) stay attached to every aggregate, so any number can be traced to its source trials.
- Missing combinations are shown as empty or NaN. Values are **never imputed**.
- Every view carries the notice: descriptive view of synthetic outputs, not evidence of clinical efficacy.

## Persona x scenario heatmap (mean composite index)

- **What it shows**: mean composite index for each persona-scenario cell that has stored trials.
- **How to read**: darker/higher cells mean the simulated composite (weighted calm/engagement/mood/regulation) was higher for that synthetic persona-scenario pair.
- **Cannot support**: comparisons across personas as if they were participants in one condition. Each cell is a separate simulation; personas differ by design.

## Same music, different personas (bar chart)

- **What it shows**: mean composite for personas run under one identical music configuration, with `n_trials` printed on bars and engine labels in hover.
- **How to read**: a descriptive contrast of how the same simulated music input maps to different synthetic personas.
- **Cannot support**: conclusions about music "working differently" for autistic children. Differences reflect the simulator's persona definitions and rule arithmetic (or AI-generated variation), not observed behavior.

## Six-dimension descriptive profile (radar)

- **What it shows**: mean of six researcher-defined normalized dimensions (0 to 1) over one persona's stored trials:
  - `calm`: inverse anxiety level.
  - `engagement`, `mood`, `regulation`: level fields rescaled from 1-10 to 0-1.
  - `attention`: attended fraction of the configured trial duration.
  - `stability`: inverse of the anxiety change magnitude between the stored start and end stages (1 = no change, 0 = nine-point swing).
- **How to read**: a shape summary of the simulated reaction pattern for that persona. A larger area is a higher synthetic score profile, not a "better outcome".
- **Cannot support**: interpretation as a validated psychological profile. The dimensions are software signals defined by this project.

## Temporal stage view (line chart)

- **What it shows**: mean stored anxiety and engagement levels at the start, middle, and end stages across all trials.
- **How to read**: the average simulated trajectory. A downward anxiety line means the simulator (or AI engine) produced declining values across stages in the stored synthetic trials.
- **Cannot support**: claims about habituation, adaptation, or within-session change in real people. The stages are model-generated observations, one per trial.

## Descriptive rankings by persona

- **What it shows**: personas sorted by mean composite index, always with `n_trials` and engine labels.
- **How to read**: an ordering of stored synthetic trial averages. With 1-3 trials per persona, ranks are essentially arbitrary.
- **Cannot support**: league tables, "responders vs non-responders", or any comparative effectiveness claim.

## Uncertainty and provenance notes

- **What it shows**: engine mix counts and each trial's stored `uncertainty_note` from the generating model.
- **How to read**: AI-engine (openai) trials carry model-stated uncertainty and are non-deterministic; deterministic trials are reproducible given the stored seed. Mixed-engine aggregates blend both behaviors.
- **Cannot support**: treating an uncertainty note as a calibrated confidence statement.

## Exported figures and data

- **What it shows**: every chart has a camera icon for PNG download; the Export section downloads the underlying radar, stage-mean, and ranking data as CSV.
- **How to read**: exports contain synthetic simulation output only. If reused in a portfolio or paper, keep the synthetic label attached.
