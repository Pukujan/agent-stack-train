# Human-sounding writing and plain charts

This guide helps agents write posts, blogs, social copy, general prose, and
papers or data writeups that do not read as AI-smoothed averages. Follow the
rules when instinct conflicts with them. Tags in brackets point at the research
corpus summarized in section 8. Machine-checkable versions live in
[`human-sounding-rules.json`](human-sounding-rules.json).

**Out of scope here:** README and product-entry pages. Those keep
`writing-direction` scan/bold rules. See [`WRITING_ROUTING.md`](WRITING_ROUTING.md).

## 1. Why AI text sounds like AI

- **It drifts toward the average.** Models pick likely phrasing, so specific
  facts fade into generic claims that sound important [WP:AISIGNS] [Bednar].
- **It overuses a small word set.** Style words such as delve, underscore,
  showcasing, crucial, realm, intricate, and pivotal spiked after ChatGPT
  [Kobak] [Liang] [Juzek]. The list shifts over time [WP:AISIGNS].
- **Its grammar differs.** Instruction-tuned models use present-participle
  tails (“…, highlighting the need”) and nominalizations far more than people
  do [Reinhart]. Prose runs long and even, with few short sentences [Economist].
- **Its rhetoric follows formulas:** “not X, but Y”, the rule of three,
  “No X. No Y. Just Z.”, bold inline headers, “serves as” instead of “is”,
  and “despite these challenges” endings [WP:AISIGNS] [Kriss] [UZH].
- **What is missing matters most.** No person doing the work, no story, no
  concrete example, no stakes. Thin evidence gets filled with rhetoric [Bednar].

Synonym swaps will not fix this. Add specifics, a narrator, and an example.
No single tell proves a text is AI-written; use tells as editing targets only
[UZH] [WP:AISIGNS].

## 2. DO / DON'T rules

**1. Plain title that says what happened.** Avoid colon-reveal titles and
slogans [WP:AISIGNS] [Kriss].

**2. Open with one concrete case, then give the numbers.** Start with a single
data point, question, or character, then zoom out [Pudding].

**3. Write as people.** Use “we” (or a clear narrator), active verbs, and
present tense for findings [Plain language] [Orwell]. Say what you did and what
surprised you [Bednar].

**4. Use contrast formulas rarely.** Avoid “not X, but Y”, “not only … but
also”, and “rather than” unless they mark a real boundary readers get wrong.
At most one per section. Edit contrasts after drafting [Pickles].

**5. Cut sneaky adverbs and mood words.** quietly, silently, notably, whisper,
echo, ghost — say what happened [Kriss] [UZH].

**6. Vary sentence length.** Target about 10–20 words on average. At least
roughly 1 in 7 sentences should be 8 words or fewer. Cap sentences near 35
words [Economist] [UZH].

**7. Prefer concrete words and uncovered verbs.** “Conduct an analysis of”
becomes “analyze” [Plain language] [Orwell] [Reinhart].

**8. Ask the research question in one plain sentence** a friend might ask
[Muscatello].

**9. State scope once, plainly, with the reason.**

**10. Keep jargon and internal names out of the main text.** Move methods,
IDs, and stats vocabulary to a methods section or footnote [Datawrapper text]
[Orwell].

**11. Earn every claim.** Every paragraph needs a number, a named entity, or an
example [Bednar]. Use only numbers you can verify.

**12. Don't restate.** No “In short…” or “despite these challenges” endings.
End on the last new fact [WP:AISIGNS].

**13. Formatting for this module.** Sentence-case headings. Bold at most one
short phrase per section. No bullets with bold inline headers. Prose by
default; bullets for real lists; tables for real rows. Prefer commas, periods,
or parentheses over em dashes [WP:AISIGNS] [UZH] [Economist].

**14. Hedge once, precisely.** Not “may potentially suggest.” Name the actual
limit [UZH].

**15. Cut participle tails.** Don't end with “, highlighting …”,
“, reflecting …”, or “, underscoring …”. Give implications their own sentence
with evidence [Reinhart].

**16. Use “is” and put new information at the end.** Prefer “is” over
“serves as” / “stands as” / “represents” [WP:AISIGNS] [Gopen & Swan].

**17. Name your sources.** Don't write “experts say” or “studies show” without
a link [WP:AISIGNS] [UZH].

**18. Use short, plain words.** “use” not “leverage”; “method” not
“methodology”; “more and more” not “increasingly” [Orwell] [Economist].

## 3. Banned and suspicious words

Full severity and fixes: [`human-sounding-rules.json`](human-sounding-rules.json).

**Banned (replace every time):** delve, underscore(s), showcase, highlight(s/ing)
as a verb, pivotal, tapestry, testament, intricate, realm, meticulous, vibrant,
palpable, camaraderie, amidst, multifaceted, groundbreaking, boasts, garner,
bolster, foster, seamless, holistic, paradigm, transformative, unprecedented,
nuanced, game-changer, “serves as”, “stands as”, “plays a key role”, “it's worth
noting”, “in today's world”, “sheds light on”, “paves the way”, “a growing body
of”, “experts argue”, “studies have shown”.

**Suspicious (at most once per page, and only when literal):** key (adjective),
crucial, robust, landscape, insights, comprehensive, leverage, enhance, align
with, notably, additionally, furthermore, moreover, ultimately, essentially,
significant, increasingly, methodology, empirical, causal, framework,
quiet(ly), echo, “give rise to”, “the fact that”, “conduct an analysis”,
“rather than”, “in other words”.

**Structural tells:** colon titles, rule-of-three lists used for rhythm,
“-ing” tails, same-shaped bullets, “Despite X, Y” openers, “No X. No Y. Just
Z.”, moralizing section endings.

## 4. Chart rules (papers and data writeups)

1. **One message per chart.** Write the message as a sentence first [UK AF]
   [Pudding].
2. **Pick the type from the relationship.** Ranking → ordered bars. Parts of a
   whole → stacked bars. Default to bars for mainstream readers; avoid dumbbell
   and range charts in main text [FT VV] [Datawrapper types] [Muscatello].
3. **Use two titles.** Headline = takeaway in plain words. Subtitle = what is
   measured, where, and when. No stats jargon in titles [UK AF] [SWD]
   [Datawrapper text].
4. **Show uncertainty in words or with grey, not whiskers.** Error bars confuse
   many readers [Belia] [Muscatello] [Hofman]. Bars are fine for counts and
   shares; means with spread work better as dots [Newman].
5. **Label directly.** Names beside bars, values at ends. Prefer no separate
   legend [Datawrapper text] [SWD].
6. **Limit series.** At most about 4 stack segments; at most 3 colours plus
   grey; about 15 rows in a main-text chart [UK AF] [SWD].
7. **Use plain row names.** No version tags, run IDs, or file paths.
8. **Annotate 1–3 things** you want people to see, as sentences next to the
   data.
9. **Label reference lines in words**, not just a number.
10. **Sort bars by the value that matters.** Start bar axes at zero [UK AF].
11. **Make the footer a usable source**, not a script path.
12. **Add a 1–3 sentence text description** under each chart, plus alt text.
13. **Declutter.** No border; light or no gridlines; no rotated text; at most
    one decimal place.
14. **Test it.** After five seconds, a colleague should say the takeaway back.

## 5. Self-check before submitting

- [ ] Title has no colon slogan; it states a finding.
- [ ] First paragraph contains one concrete example or case.
- [ ] A narrator (“we” / named actor) appears early with something done or noticed.
- [ ] Zero banned words; each suspicious word at most once.
- [ ] At most one real contrast per section; no “, highlighting” tails.
- [ ] Em dashes sparse; sentence lengths vary.
- [ ] No bold-inline-header bullet lists (for this module’s outputs).
- [ ] Every paragraph has a number, name, or example; no “experts say”.
- [ ] No paragraph ends by restating itself.
- [ ] Internal IDs and file paths stay out of the main text.
- [ ] Charts use takeaway titles, direct labels, plain names, few colours,
      usable sources, and no dumbbell/whisker charts in main text.
- [ ] Every number matches source data.
- [ ] A smart friend outside the project can explain the main finding back.

## 6. How to use the tells without overcorrecting

- Fix structure first: title, opening example, narrator. Then fix words
  [Bednar] [Kobak].
- Do a separate edit pass for contrasts and triplets [Pickles].
- Don't replace one tic with another uniform habit [UZH].

## 7. Sample opening shape

> [Plain title that states the finding]
>
> [One concrete case a reader can picture.] [Zoom out to the measured set and
> the surprising number.] [One sentence on why that gap is the piece.]
>
> What we found:
>
> 1. [Takeaway with a number.]
> 2. [Takeaway with a number.]
> 3. [Takeaway with a number.]

Swap the hypothetical case for a real item from the material whenever you can.

## 8. Sources

Research and practitioner sources behind the rules (fetched and read for the
original corpus; [Belia] and [Newman] as abstracts):

- [WP:AISIGNS] Wikipedia: Signs of AI writing
- [Kobak] Kobak et al., excess vocabulary in biomedical abstracts (Science Advances 2025)
- [Reinhart] Reinhart et al., LLM grammatical and rhetorical styles (PNAS 2025)
- [Liang] Liang et al., LLMs in scientific papers
- [Juzek] Juzek & Ward, Why Does ChatGPT "Delve" So Much?
- [Economist] How to spot AI writing
- [Kriss] Sam Kriss on machine-text patterns
- [Bednar] Why AI Writing Sounds Like AI Writing
- [UZH] Marco Weber, Do I Sound Like an AI?
- [Pickles] The Thinking Inside the LLM Clichés
- [Orwell] Politics and the English Language
- [Plain language] Digital.gov writing guidance
- [Gopen & Swan] The Science of Scientific Writing
- [Datawrapper text / types] Lisa Charlotte Muth
- [SWD] Storytelling with Data declutter guidance
- [FT VV] Financial Times Visual Vocabulary
- [UK AF] UK Government Analysis Function chart guidance
- [Muscatello] Communicating population health statistics through graphs
- [Pudding] Making Internet Things, storytelling
- [Belia] Misunderstanding of CI / SE bars
- [Newman] Within-the-bar bias
- [Hofman] Visualizing inferential uncertainty

URLs and match rules for linting live in [`human-sounding-rules.json`](human-sounding-rules.json).
