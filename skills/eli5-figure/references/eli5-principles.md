# ELI5 figure principles

## Contents

- What this register is for
- Why it is explicit-only
- Rules and where they come from
- Anti-patterns
- Worked example
- Sources

## What this register is for

An ELI5 figure gives a reader outside the field a true first model of one mechanism in one look. It is the entry level of the same content that the exact figure carries at peer level. The reader is a smart adult who has not worked in this domain: an executive, a colleague from another team, a new hire on day one. Not a child. The name is a convention for "assume no background", not a tone.

## Why it is explicit-only

For a reader who already holds the domain, the simple figure is redundancy. The expertise reversal effect (Kalyuga, Ayres, Chandler, and Sweller, 2003) reports that instructional support which helps novices, including explanatory text integrated into diagrams, becomes redundant for experienced readers and can lower their performance, because they must reconcile it with what they already know. In the diagram experiments they review, novices learned best from diagram plus text and experienced learners from the diagram alone. The default readers of this pack are peers, so simplification is a decision the user makes, never the model's default. The exact figure is `technical-diagram`'s; this skill reduces it.

## Rules and where they come from

1. **Start from the exact structure.** Feynman's practice treats a simple explanation as a test of understanding: when the exact figure cannot be reduced without inventing a relation, the gap is in the understanding, and the fix is to go back to the exact inventory, not to smooth the picture.
2. **One analogy, chosen before drawing, held throughout.** Two analogies make two figures. Shared by the ELI5 skills that produce readable prose (patrick204nqh, guicortei).
3. **State where the analogy breaks**, in the prose beside the figure (explain-simply, guicortei). Where the break would make the picture lie, draw the real relation at that point instead of the analogy.
4. **Constrain concepts, not vocabulary.** Thing Explainer's thousand-word constraint produced drawings that critics found cryptic; the reader is helped by fewer ideas, not by circumlocution. Keep an exact name as a second line when the reader will meet it again.
5. **Verbs on arrows.** Explanations aimed at novices stress action and behavior, not only structure (Kang, Tversky, and Black, 2015). An unlabeled arrow assumes a schema this reader does not have.
6. **Simplify language, never facts** (Cloudflare docs eli5). A merged node hides detail; it may not assert what the exact figure contradicts. The "80 percent accurate is fine" stance some ELI5 skills take is not adopted here, because this figure sits in documents that peers also read.
7. **Ten-second test by a fresh reader.** The author cannot judge their own simplicity (Pinker's curse of knowledge: experts think in chunks and cannot reconstruct not knowing). Give the figure alone to a fresh-context reader or subagent and ask what happens and to whom.
8. **Nothing above or below the figure.** The analogy sentence, the mapping, and the limits are prose. Same rule as `technical-diagram`.
9. **A path from simple to exact.** The reduction record names what was merged and hidden, so a reader can step from this figure to the exact one; the Wired "5 Levels" format works because each level declares itself and the viewer chooses where to enter.

## Anti-patterns

- Drawing from the source material and simplifying as you go.
- Talking down: "simply", "just", "basically", "magic", "imagine you are five".
- Cartoon devices: icons, emoji, clip-art people, thought bubbles.
- A magic box: a node whose action the reader cannot picture.
- The analogy as a title above the figure; the mapping table as a footer below it.
- Two mechanisms in one analogy.
- Vocabulary policing that yields "the box that remembers things you asked before" when "sticky note" would do.

## Worked example

`assets/eli5-example.d2` is the simple register of a cache-aside read path whose exact figure, in `technical-diagram`'s register, would be: `client -> API gateway -> order-service -> PostgreSQL`, with `order-service -> Redis` labeled `GET order:{id}`, a miss labeled `SELECT ... then SET with TTL 300s`, and the gateway's token check on the first edge.

Reduction record for the example:

```text
reader: a colleague outside engineering asking why the same page loads faster the second time
question: why a repeated request is answered faster
analogy: asking a counter clerk who keeps a sticky note of recent answers
exact_source: the cache-aside read path above
kept: []            # no name the reader will meet again
merged: [{from: [API gateway, order-service], to: Counter clerk}, {from: [Redis], to: Sticky note of answers}, {from: [PostgreSQL], to: Storeroom}, {from: [HTTP 200 response], to: Your answer}]
hidden: [TTL expiry (answers "how long is it fast"), token check (answers "who may ask"), the write path (answers "how does the note get wrong")]
analogy_breaks: a sticky note never goes stale by itself; the real note is thrown away after a set time, and the storeroom's contents can change while the clerk walks
```

## Sources

Checked 2026-09-18. Skill repositories are cited for the practice observed in their instructions, not as authorities.

- Kalyuga, S., Ayres, P., Chandler, P., and Sweller, J. (2003). The expertise reversal effect. Educational Psychologist, 38(1). Summary: https://en.wikipedia.org/wiki/Expertise_reversal_effect
- Kang, S., Tversky, B., and Black, J. B. (2015). Coordinating gesture, word, and diagram: explanations for experts and novices. Spatial Cognition and Computation. Abstract: https://scholarworks.utrgv.edu/tl_fac/155/
- Canham, M., and Hegarty, M. (2010). Effects of knowledge and display design on comprehension of complex graphics. Learning and Instruction, 20(2). Removing task-irrelevant content helped low-knowledge viewers most.
- Farnam Street, The Feynman Technique: https://fs.blog/feynman-technique/
- Storythings, Formats Unpacked: Wired's 5 Levels: https://formatsunpacked.storythings.com/p/formats-unpacked-wireds-5-levels
- Thing Explainer and its reception: https://en.wikipedia.org/wiki/Thing_Explainer
- Pinker on the curse of knowledge: https://www.psychologicalscience.org/observer/the-curse-of-knowledge-pinker-describes-a-key-cause-of-bad-writing
- Tufte, E. (1990). Envisioning Information: "Clutter and confusion are failures of design, not attributes of information."
- Skill practice: github.com/guicortei/feynman-technique (five-level ladder, analogy limits, expertise reversal cited), github.com/yash2002vardhan/explain-simply (where the analogy breaks), github.com/cloudflare/cloudflare-docs eli5 (simplify language, never facts), github.com/patrick204nqh/skills eli5 (one analogy chosen first, smart adult), github.com/anthropics/claude-plugins-community eli5 (the ten-line official community skill; "big pictures and few words" and nothing about what to merge or drop).
