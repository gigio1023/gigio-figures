# Defect memory

Recurring defects, each as symptom, check, and repair. Run the whole list on every review; add an entry when a user corrects a figure or the same defect appears twice. In an installed copy, keep additions in the user's project notes or a local copy of this file so an update of the skill does not erase them. Entries below were observed in real figure sets and published figures.

| Symptom | Check | Repair |
|---|---|---|
| One accent color means many things across a document (a component in one figure, a selected candidate in the next, a metric in a third) | List every hued element on the contact sheet with its meaning; any hue with more than one meaning fails | Assign hues in the semantic map; use position or a label for other emphasis |
| Every node has the same box, stroke, and weight; nothing reads first | Squint at the PNG: is one element obviously first? | Apply the emphasis budget: hue and 2.25u stroke on the claim path, ghost the context |
| The central object is the weakest line (a residual stream drawn as a thin side skip) | Is the object the claim is about the heaviest neutral line? | Redraw it as the spine; move components beside it |
| The accent fill is too faint to register (contrast around 1.1:1 against white) | Is the focus visible in grayscale at the delivery width? | Use the hue stroke at 2.25u with the tint fill, not a tint alone |
| A count or structure is written instead of drawn ("4 streams", "8 of 256 selected") | Does the text state a structure that could be marks? | Draw the four lines; draw selected and unselected experts |
| A controller drawn as a data source (experts appear to read the router's output) | Does every data edge carry data the target reads? | Router to gates as `control`; data from the hidden state |
| Comparison panels repeat the whole structure; the difference is a fifth of the ink | Count the elements that differ between panels | Ghost or superpose the shared scaffold; emphasize only the differences |
| Concept names set in monospace; mono and sans titles mixed at one level | Is every mono string literally in code? Is each level one family? | Sans for concepts, mono only for identifiers, identifiers on their own line |
| Edge labels narrate time or repeat the next node's name ("inputs", "after training", "generate answers" three times) | Delete each label mentally: is the relation still clear from names and style? | Delete it; keep only payload, operation, or condition |
| Tall figures that do not fit one screen with their caption | Height at the delivery width above about 750 CSS px | Rearrange horizontally or split; do not shrink type |
| The same overview stack repeated at 30 percent of the width in figure after figure | Does a figure repeat a structure already shown at full size? | Show it once; afterwards a small ghosted locator |
| Two figures in the set use a different font or math rendering because they were made later by another route | Contact sheet: same families and math glyphs everywhere? | One render pipeline per document; late figures go through it too |
| Unicode imitation of math (`r̂ᵀx`, `x⁽ˡ⁾`) with misaligned hats and superscripts | Lint `unicode-math` | `data-tex` |
| A zoom or inset deleted as "decoration", losing the geometric explanation | Did an inset show the operation itself? | Keep mechanism insets; only titles, footers, badges, icons, and filler are banned |
| Transparent PNG exported with dark lines; arrows and labels vanish on a dark page | Composite the PNG on the dark background | Bake the background; render both themes |
| The simplest box-flow figure chosen as the house example, pulling the set toward labeled boxes | Is the reference figure the most mechanism-rich one? | Choose a figure that draws its mechanism as the reference |
| A validator passed a figure whose labels overlapped, because widths were estimated | Were widths measured with the real fonts? | Use `lint.mjs`, which measures in the browser |
| Logos, emoji, bullet lists inside cards, labels near 9 px in a data pipeline figure | Any decoration or sentence inside the canvas? | Remove; move lists to prose; keep labels at the token size |
| Six categories in nearly identical tints | Can each category be named in grayscale? | At most three semantic hues; position and labels for the rest |
