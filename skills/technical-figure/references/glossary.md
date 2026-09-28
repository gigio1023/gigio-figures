# Glossary

Terms used in this skill and in figure critique, grouped by what they describe. Each entry says what the term means and what it looks like in a technical figure.

## Seeing and encoding

| Term | Meaning | In a figure |
|---|---|---|
| Mark | The drawn primitive: point, line, area | A box, an arrow, a cell |
| Channel | A visual property of a mark: position, length, color, stroke, shape | Hue for meaning, stroke width for emphasis |
| Expressiveness | Show all of the facts and only the facts | No size difference between equal peers |
| Effectiveness | Put the most important information in the most accurate channel | The key distinction as position, not as a text prefix |
| Preattentive, pop-out | A single difference seen at a glance regardless of clutter | One hued path among gray ones |
| Salience | How strongly an element draws attention first | The claim's subject is the most salient element |
| Figure-ground | Separating an object from its background | Overlapping arrows need different weight or offset |
| Gestalt grouping | Proximity, similarity, common region, connectedness, continuity, closure | Labels beside their element; a container groups its members |
| Common region | Elements inside one boundary read as one group, stronger than proximity | Containers must be real groups |
| Uniform connectedness | A connected region reads as one unit before grouping | One object is one shape, not two boxes |

## Hierarchy and composition

| Term | Meaning | In a figure |
|---|---|---|
| Visual hierarchy | The order in which elements are read | Claim path, then context, then frame |
| Layering and separation | Distinct weight layers for different kinds of information | Gray context, black mechanism, hued claim |
| Smallest effective difference | Every distinction as light as it can be and still visible | Faint frames, one accent |
| Ghost | A context element kept in place at low weight | Unselected experts drawn pale |
| Emphasis budget | One focal element or path per figure | One hue and one heavy stroke |
| Focus plus context | Detail shown inside its surrounding context | The zoomed block marked on a small locator |
| Overview plus detail | Overview and detail in separate views | Stack on the left, zoom panel on the right |
| Locator | A small overview with the current region marked | A thumbnail stack after the first full overview |
| Zoom panel, inset | A panel that details one element shown elsewhere | Dashed panel joined by one dotted leader |
| Micro and macro reading | The whole pattern at a glance and the details up close | A layer strip showing the repeating pattern |
| Small multiples | The same frame repeated with one variable changed | One panel per method or model |
| Delta highlight | A known design in neutral with only additions colored | A new attention branch in green on a gray architecture |
| Sibling variants | Variants on identical coordinates | The second panel is the first minus one component |
| Juxtaposition, superposition, explicit encoding | Side by side, overlaid, or the difference drawn itself | Three panels; one scaffold with three marks; a difference vector |

## Notation

| Term | Meaning | In a figure |
|---|---|---|
| Semiotic clarity | One symbol per concept and one concept per symbol | A hue means one thing in the whole document |
| Symbol overload | One symbol with several meanings | The same blue for components, candidates, and metrics |
| Congruence | The figure's structure matches the concept's structure | Four streams drawn as four lines |
| Semantic map | The document's assignment of meanings to hues and styles | Blue = read, vermillion = write |
| Data flow | A value moving from producer to consumer | Solid arrow |
| Control flow | A decision over selection, weights, or parameters | Dashed arrow |
| Fan-out, exclusive choice | Copy to all, or one of several | Junction dot, or a bracket with a condition |
| Junction dot | A point where a line really splits or merges | Small dot at a T |
| Line hop | A gap or arc showing that crossing lines do not connect | A small bridge |
| Spine | The line of a shared state that components read and write | A vertical residual stream |
| Direct labeling | Names beside the marks instead of a legend | Series name at the end of its line |
| Leader | A thin line connecting a label or panel to its element | Dotted line to a zoom panel |

## Layout and routing

| Term | Meaning | In a figure |
|---|---|---|
| Layered (Sugiyama) layout | Nodes placed in layers so edges mostly point one way | A flow with clear rows |
| Crossing minimization | Reordering nodes within layers to reduce crossings | Untangled edges |
| Orthogonal routing | Edges made of horizontal and vertical segments | Circuit-style lines with rounded bends |
| Port, port side | Where an edge meets a node, and on which side | Outputs on top, skip inputs from the side |
| Model order | Keeping the input order of nodes when it adds no crossings | Experts listed 1, 2, ..., N in order |
| Bend | A change of direction in an edge | At most two or three per edge |
| Compound graph | Nodes inside nodes | A module container with its operations |
| Hand layout | Coordinates chosen by computation or by hand | Spines, zoom panels, geometry |

## Type and color

| Term | Meaning | In a figure |
|---|---|---|
| Typeface, font stack | A design, and the ordered fallbacks used when a font or glyph is missing | Pretendard, then system fallbacks |
| x-height, cap height | Height of lowercase x and of capitals | Used to match math to labels |
| Tracking, kerning, leading | Letter spacing overall, per pair, and line spacing | Tracking only on all-caps micro labels |
| Tabular figures | Digits of equal width | Aligned numbers in columns |
| Stylistic set | A font's alternate glyphs | `ss06` separating I, l, 1 |
| Subsetting | Keeping only the glyphs a file uses | Small embedded fonts in a portable SVG |
| OKLCH | A perceptual color space: lightness, chroma, hue | Picking hues of matched lightness |
| Tint, shade | A lighter or darker version of a hue | Tint fills behind hued outlines |
| Categorical, sequential, diverging palette | Colors for categories, one-direction magnitudes, and two-direction magnitudes | Series colors, heatmaps, signed values |
| Contrast ratio, APCA Lc | Luminance contrast (WCAG) and a polarity-aware lightness contrast | Text 4.5:1, meaningful lines 3:1 |
| Color-vision deficiency | Reduced sensitivity of one cone type (protan, deutan, tritan) | Why red and green are not a pair |
| Baked background | The background color drawn into the image | Opaque PNGs for each theme |

## Reading and load

| Term | Meaning | In a figure |
|---|---|---|
| Split attention | Cost of integrating information placed apart | Labels far from their marks, mechanism only in the caption |
| Redundancy | The same information twice, which costs attention | An edge label repeating the next node's name |
| Expertise reversal | Help for novices that slows experts | No explanatory prose in peer figures |
| Eyes beat memory | Comparing what is visible beats comparing with what was seen before | Comparisons on one screen |
| Cognitive integration | Helping readers connect several figures | One grammar and locators across a document |
