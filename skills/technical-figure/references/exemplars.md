# Exemplars

Published figures worth opening before drawing a similar one, each with the lesson it teaches. Before drawing a figure of the same form, download the cited figure (or extract it from the paper PDF) and look at it; study the structure and the emphasis, not the palette. Images are not vendored because they belong to their publishers; keep downloaded copies out of the repository and out of deliverables. Dates are publication dates; all were inspected in 2026-09.

## Residual stream, reading and writing

| Figure | Source | Lesson |
|---|---|---|
| Residual stream diagrams | Elhage et al., A Mathematical Framework for Transformer Circuits, https://transformer-circuits.pub/2021/framework/index.html (2021-12) | The stream is a vertical spine; components branch off to read and add back through ⊕; the layer under discussion is in full ink and the rest are ghosted in place; equations align with the stage they describe |
| Subspace band | same | A direction inside the stream drawn as a colored ribbon within a band, and removal as a darker ribbon |
| Figure 1 | Qwen3.8-Next, https://arxiv.org/abs/2608.30320 (2026-08) | Read and write paths in two fixed colors across the whole figure; a literal layer sequence on the left, the repeating unit zoomed on the right |
| Figure 7 | same | Layer index as an axis, bands for the minority layer type, writer and reader markers along it |
| Figure 1 | Gemma Scope, https://arxiv.org/abs/2408.05147 (2024-08) | Only the read and write sites the method touches are filled; the rest of the block is plain |

## Interventions and method comparison

| Figure | Source | Lesson |
|---|---|---|
| Intervention panels | Lindsey et al., On the Biology of a Large Language Model, https://transformer-circuits.pub/2025/attribution-graphs/biology.html (2025-03) | Same graph repeated as small multiples; the intervened node carries a small accent badge, downstream nodes fade, outputs sit below each panel; narrower layouts rearrange panels instead of shrinking text |
| Token intervention rows | Tracing the thoughts of a large language model, https://www.anthropic.com/research/tracing-thoughts-language-model (2025-03) | Token chips per position, the intervened position outlined, one row per condition |
| Figure 15 | Deliberative alignment, https://arxiv.org/abs/2412.16339 (2024-12) | Methods as rows, shared stages as columns; cells identical to the baseline are hatched ghosts, only differing cells carry color |
| Figure 2 | DeepSeek-V3.2, https://arxiv.org/abs/2512.02556 (2025-12) | Delta highlight: the known design stays neutral, the new component and its edges are green, and the caption names the color |
| Figures 3 and 4 | DeepSeek-V4, https://arxiv.org/abs/2606.19348 (2026-06) | Sibling variants on identical coordinates; the second figure is the first minus one component |
| Figure 1 | mHC, https://arxiv.org/abs/2512.24880 (2025-12) | Residual, hyper-connection, and constrained variant on one skeleton; only the changed mapping is colored |
| Figure 3 | DeepSeek-V2, https://arxiv.org/abs/2405.04434 (2024-05) | MHA, GQA, MQA, MLA as small multiples where only head sharing changes; hatching marks cached tensors |
| Demo figure | Making LLMs more accurate by using all of their layers (SLED), https://research.google/blog/making-llms-more-accurate-by-using-all-of-their-layers/ (2025-09) | Baseline and method on the same layout; the method's extra taps are the only new marks |

## Directions, vectors, geometry

| Figure | Source | Lesson |
|---|---|---|
| Extraction pipeline | Persona vectors, https://www.anthropic.com/research/persona-vectors (2025-08) | Two mirrored columns in two semantic tints meet at ⊖ and ⊜ and end in a vector glyph; header bars carry hierarchy |
| Figure 1 | Rimsky et al., Steering Llama 2 via Contrastive Activation Addition, https://arxiv.org/abs/2312.06681 (2023-12) | A vector drawn as a strip of cells, reused as the same glyph wherever that vector appears |
| Geometry panels | Elhage et al., Toy Models of Superposition, https://transformer-circuits.pub/2022/toy_model/index.html (2022-09) | Several geometric states in aligned panels with the same axes and orientation |
| Dot product and direction lessons | 3Blue1Brown, How might LLMs store facts, https://www.3blue1brown.com/lessons/mlp (2024) | A label's color equals its arrow's color equals the symbol's color in the equation |

## Mixture of experts

| Figure | Source | Lesson |
|---|---|---|
| Expert path across layers | Grootendorst, A Visual Guide to Mixture of Experts, https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts (2024-10) | The selected path is about three times heavier than context paths; unselected experts stay as pale dots; the annotation sits outside in gray italic with a leader |
| Router and experts | same | Router, gate, and expert colors fixed for the whole guide and reused in its equations |
| Figure 2 | DeepSeek-V3, https://arxiv.org/abs/2412.19437 (2024-12) | Shared experts apart from routed ones, a small router histogram, gates only on selected experts, one ⊕ collecting outputs; the MoE block zoomed from the stack by dashed leaders |
| Figure 2 | LongCat-Flash, https://arxiv.org/abs/2509.01322 (2025-09) | Router bars colored by the kind of expert they select |

## Hybrid layers and layer patterns

| Figure | Source | Lesson |
|---|---|---|
| Figure 3 | MiniMax-01, https://arxiv.org/abs/2501.08313 (2025-01) | Macro stack with `1×` and `N×`, zoom panels whose background is a tint of the parent block |
| Figure 5 | same | Tensor rectangles sized by their dimensions so complexity reads as area |
| Figure 5 | SambaY, https://arxiv.org/abs/2507.06607 (2025-07) | Four hybrid variants on one template |
| Figure 2 | MiMo-V2-Flash, https://arxiv.org/abs/2601.02780 (2026-01) | One accent marks the attention type that the paper is about; norms are borderless gray |
| Big LLM Architecture Comparison | Raschka, https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison (2025-07, updated 2026) | Same template per model, only changed blocks outlined; its small labels are the counterexample for column width |

## Precision and formats

| Figure | Source | Lesson |
|---|---|---|
| Figures 6 and 7 | DeepSeek-V3, https://arxiv.org/abs/2412.19437 (2024-12) | Casts as italic edge labels, stored dtypes under nodes; tile and block scaling as an inset beside the step with swatch colors fixed across panels |
| Figure 25 | Llama 3, https://arxiv.org/abs/2407.21783 (2024-07) | Higher precision as a saturated hue and lower precision as a tint of the same hue; scale granularity as the scale vector's shape |
| Figure 6 | Step-3, https://arxiv.org/abs/2507.19427 (2025-07) | Two columns split by a divider; dtypes on the edges that cross it |
| Quantization guide | Grootendorst, A Visual Guide to Quantization, https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization (2024-07) | Formats stacked on one number line for range; bit fields as proportional colored segments |

## Pipelines and recipes

| Figure | Source | Lesson |
|---|---|---|
| Workflow figures | Building effective agents, https://www.anthropic.com/engineering/building-effective-agents (2024-12) | Role-tinted boxes with same-hue text, thin gray arrows, dashed for conditional paths; very little else |
| Figure 3 | Deliberative alignment, https://arxiv.org/abs/2412.16339 (2024-12) | Shape encodes type: model, data, specification |
| Figure 3 | MiMo-V2-Flash, https://arxiv.org/abs/2601.02780 (2026-01) | Gray backbone, one colored feedback loop, stages marked by a ruler beneath instead of boxes |
| Figure 5 | GLM-5, https://arxiv.org/abs/2602.15763 (2026-02) | Stroke color encodes data kind consistently across stages |
| Figure 2 | AlphaEvolve, https://arxiv.org/abs/2506.13131 (2025-06) | Component colors reused on the matching identifiers in the pseudocode beside the diagram |
| Overview | Titans and MIRAS, https://research.google/blog/titans-miras-helping-ai-have-long-term-memory/ (2025-12) | A right-hand column states what changes in each row |

## Token and position figures

| Figure | Source | Lesson |
|---|---|---|
| Figure 4 | OpenAI, weight-sparse transformers, https://cdn.openai.com/pdf/41df8f28-d4ef-43e9-aed2-823f9393e470/circuit-sparsity-paper.pdf (2025-11) | One column per token, dashed layer boundaries, the active circuit in one hue and everything else gray |
| Transformer Explainer | Georgia Tech Polo Club, https://poloclub.github.io/transformer-explainer/ (live) | Token rows keep their position through every stage; Q, K, V colors persist into the attention matrix |

## Counterexamples

| Figure | Source | Why it fails |
|---|---|---|
| Figure 3 | MiniMax-M2 report, https://arxiv.org/abs/2605.26494 (2026-05) | Trademark logos, bullet lists inside cards, labels around 9 px at column width |
| Figure 10 | GLM-5, https://arxiv.org/abs/2602.15763 (2026-02) | Emoji, a novelty font, three arrow styles without meaning |
| Architecture PNG | Qwen3-Next model card image, https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct (2025-09) | Transparent background with black lines: repeat counts and arrows vanish on a dark page |
| Figure 1 | Gemma 4 report, https://arxiv.org/abs/2607.02770 (2026-06) | Crossing dashed lines and rotated text |
| Figure 2 | DeepSeek-R1, https://arxiv.org/abs/2501.12948 (2025-01) | Six categories in near-identical blue-violet tints and white text on light fills |
