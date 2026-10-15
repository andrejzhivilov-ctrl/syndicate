---
name: jack-quant-models
description: Estimate sports, esports and poker probabilities from explicit quantitative inputs.
---

# jack-quant-models

Use model with sport and inputs. Available models: football Poisson/Dixon-Coles; basketball possession/normal baseline; tennis IID-point Markov set; esports independent maps exact enumeration; poker supplied-equity chip EV; ICM prize equity. These are mathematical baselines, not calibrated trained models or a GTO solver. Preserve calibration=false, input provenance and model limitations. Use benchmark for proportional vig removal; outcomes must form one complete mutually exclusive market. Validate with held-out data before relying on predicted probabilities.
