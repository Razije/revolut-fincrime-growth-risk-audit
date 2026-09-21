#import "report-theme.typ": report-accent, report-theme

#show: report-theme.with(
  title: "Head of Risk Investigation Priority Brief",
  author: "Razije",
  rhythm: "report",
  body-size: 9.4pt,
  running-header: false,
)

#set text(lang: "en", region: "gb", font: "Libertinus Serif")
#set heading(numbering: none)
#show heading: set text(font: "Libertinus Serif")
#show link: set text(fill: rgb("#2f65a7"))

#let navy = rgb("#17324d")
#let blue = rgb("#2f65a7")
#let green = rgb("#0b7355")
#let red = rgb("#a31d37")
#let amber = rgb("#b86f2c")
#let muted = rgb("#64748b")
#let line-col = rgb("#dce5ee")
#let soft-blue = rgb("#eef4fa")
#let soft-green = rgb("#eaf6f0")
#let soft-red = rgb("#faedf0")
#let soft-amber = rgb("#fbf2e8")
#let paper = rgb("#ffffff")

#let metric(label, value, note, tone: navy, fill: soft-blue) = rect(
  width: 100%,
  height: 2.55cm,
  fill: fill,
  stroke: 0.55pt + line-col,
  radius: 7pt,
  inset: 10pt,
)[
  #text(size: 6.8pt, weight: 700, fill: muted, tracking: 0.5pt)[#label]
  #v(4pt)
  #text(size: 21pt, weight: 700, fill: tone)[#value]
  #v(2pt)
  #text(size: 7.3pt, fill: muted)[#note]
]

#let callout(title, body, tone: green, fill: soft-green) = rect(
  width: 100%,
  fill: fill,
  stroke: (left: 3pt + tone, rest: 0.5pt + line-col),
  radius: 5pt,
  inset: (x: 12pt, y: 9pt),
)[
  #text(weight: 700, fill: tone)[#title]
  #h(5pt)
  #body
]

#let page-title(kicker, title, subtitle: none) = [
  #text(size: 7pt, weight: 700, fill: blue, tracking: 0.8pt)[#kicker]
  #v(3pt)
  #text(size: 20pt, weight: 700, fill: navy)[#title]
  #if subtitle != none [
    #v(3pt)
    #text(size: 8.5pt, fill: muted)[#subtitle]
  ]
  #v(8pt)
  #line(length: 100%, stroke: 0.75pt + line-col)
  #v(10pt)
]

#let uid(a, b) = text(font: "DejaVu Sans Mono", size: 6.25pt, fill: navy)[#a\#b]

#let target-card(rank, id, score, events, markets, severity, kyc, focus, fill: soft-blue) = rect(
  width: 100%,
  height: 5.0cm,
  fill: fill,
  stroke: 0.55pt + line-col,
  radius: 7pt,
  inset: 10pt,
)[
  #grid(
    columns: (auto, 1fr, auto),
    gutter: 8pt,
    align: (left, horizon),
    circle(radius: 12pt, fill: navy)[#align(center + horizon, text(size: 8pt, weight: 700, fill: white)[#rank])],
    text(size: 6.6pt, font: "DejaVu Sans Mono", fill: navy)[#id],
    text(size: 15pt, weight: 700, fill: green)[#score],
  )
  #v(7pt)
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 5pt,
    stack(dir: ttb, spacing: 2pt, text(size: 6pt, fill: muted)[EVENTS], text(size: 9pt, weight: 700)[#events]),
    stack(dir: ttb, spacing: 2pt, text(size: 6pt, fill: muted)[METHODS], text(size: 9pt, weight: 700)[5]),
    stack(dir: ttb, spacing: 2pt, text(size: 6pt, fill: muted)[MARKETS], text(size: 9pt, weight: 700)[#markets]),
    stack(dir: ttb, spacing: 2pt, text(size: 6pt, fill: muted)[SEVERITY RANK], text(size: 9pt, weight: 700)[#severity]),
  )
  #v(6pt)
  #text(size: 7.25pt, fill: navy)[*Investigative focus:* #focus]
  #v(3pt)
  #text(size: 6.5pt, fill: muted)[Observed KYC state: #kyc. All five users have a 100% confirmed-fraud rate in this file.]
]

// -----------------------------------------------------------------------------
// Page 1 — executive cover and decision
// -----------------------------------------------------------------------------
#page(
  margin: (top: 1.4cm, bottom: 1.35cm, x: 1.65cm),
  numbering: none,
  header: none,
  footer: none,
  fill: paper,
)[
  #grid(
    columns: (1fr, auto),
    align: (left, horizon),
    text(size: 7pt, weight: 700, fill: red, tracking: 0.9pt)[CONFIDENTIAL · MANAGEMENT USE],
    text(size: 7pt, fill: muted)[21 SEPTEMBER 2026],
  )
  #v(1.6cm)
  #text(size: 31pt, weight: 700, fill: navy)[Head of Risk]
  #v(-2pt)
  #text(size: 31pt, weight: 700, fill: navy)[Investigation Priority Brief]
  #v(0.4cm)
  #text(size: 13pt, fill: blue)[Growth reconciliation, Top 5 targets and control priorities]
  #v(1.0cm)

  #rect(width: 100%, fill: navy, radius: 9pt, inset: 16pt)[
    #text(size: 7pt, weight: 700, fill: rgb("#9fc3e8"), tracking: 0.8pt)[EXECUTIVE DECISION]
    #v(5pt)
    #text(size: 16pt, weight: 700, fill: white)[Prioritise five users for immediate cross-functional investigation.]
    #v(7pt)
    #text(size: 9.5pt, fill: rgb("#e6edf4"))[
      The selection is not a disguised transaction-volume ranking. Ninety per cent of the score reflects repeatability,
      statistical conviction, abnormality and attack breadth. Amount severity contributes ten per cent and is normalised
      within transaction type and currency.
    ]
  ]
  #v(0.8cm)

  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 8pt,
    metric("MARKETING", "78.17%", "5,463 / 6,989", tone: red, fill: soft-red),
    metric("SUSTAINABLE PROXY", "71.74%", "5,014 / 6,989", tone: green, fill: soft-green),
    metric("FRAUD EVENTS", "14,543", "2.11% of rows", tone: navy),
    metric("AFFECTED USERS", "299", "confirmed-fraud population", tone: amber, fill: soft-amber),
  )
  #v(0.8cm)

  #text(size: 7pt, weight: 700, fill: blue, tracking: 0.8pt)[MANAGEMENT TAKEAWAYS]
  #v(6pt)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 10pt,
    rect(fill: soft-green, stroke: 0.5pt + line-col, radius: 6pt, inset: 11pt)[
      #text(size: 11pt, weight: 700, fill: green)[1 · Act now]
      #v(5pt)
      #text(size: 8pt)[Open coordinated investigations on the five ranked users, preserving evidence and mapping linked entities before customer-impacting action.]
    ],
    rect(fill: soft-blue, stroke: 0.5pt + line-col, radius: 6pt, inset: 11pt)[
      #text(size: 11pt, weight: 700, fill: blue)[2 · Govern the KPI]
      #v(5pt)
      #text(size: 8pt)[Keep 71.74% as an internal sensitivity. It is stricter than Marketing's 78.17%, but the file cannot support a true app conversion or retention rate.]
    ],
    rect(fill: soft-amber, stroke: 0.5pt + line-col, radius: 6pt, inset: 11pt)[
      #text(size: 11pt, weight: 700, fill: amber)[3 · Close data gaps]
      #v(5pt)
      #text(size: 8pt)[Add timestamps, realised loss, reversals, devices, counterparties and case outcomes before operationalising the ranking.]
    ],
  )
  #v(0.75cm)

  #callout([Decision standard.], [This report establishes an investigation queue, not a legal conclusion, automated restriction rule or attribution of attacker identity.], tone: red, fill: soft-red)

  #v(1fr)
  #grid(
    columns: (1fr, auto),
    text(size: 7pt, fill: muted)[Source: supplied `fin_crime_data.csv` · 688,651 rows · 8,021 users],
    text(size: 7pt, fill: muted)[Model v1.0.0 · Prepared for senior risk management],
  )
]

#counter(page).update(1)
#set page(
  paper: "a4",
  margin: (top: 1.35cm, bottom: 1.45cm, x: 1.55cm),
  numbering: "1",
  header: context {
    set text(size: 6.8pt, fill: muted)
    grid(columns: (1fr, auto), [HEAD OF RISK INVESTIGATION PRIORITY BRIEF], [CONFIDENTIAL])
    v(-2pt)
    line(length: 100%, stroke: 0.4pt + line-col)
  },
  footer: context {
    line(length: 100%, stroke: 0.4pt + line-col)
    v(2pt)
    set text(size: 6.7pt, fill: muted)
    grid(columns: (1fr, auto), [Internal management use · Model v1.0.0], counter(page).display("1"))
  },
)

// -----------------------------------------------------------------------------
// Page 2 — growth reconciliation and portfolio risk
// -----------------------------------------------------------------------------
#page-title(
  [SECTION 01 · CONTEXT],
  [Growth reconciliation and portfolio risk],
  subtitle: [The same denominator produces a 6.42-point gap once confirmed fraud and repeat use are made explicit.],
)

#grid(
  columns: (1fr, auto, 1fr, auto, 1fr),
  gutter: 7pt,
  metric("MARKETING RECONSTRUCTION", "78.17%", "5,463 users · ≥1 card payment", tone: red, fill: soft-red),
  align(center + horizon)[#text(size: 18pt, weight: 700, fill: red)[→]],
  metric("QUALITY SCREEN", "75.30%", "−200 users · confirmed fraud", tone: blue, fill: soft-blue),
  align(center + horizon)[#text(size: 18pt, weight: 700, fill: amber)[→]],
  metric("SUSTAINABLE PROXY", "71.74%", "−249 users · repeat use", tone: green, fill: soft-green),
)
#v(8pt)
#callout([Reconciliation.], [The total reduction is 449 users, or 6.42 percentage points, on the same cohort of 6,989 users observed exclusively as KYC PASSED.], tone: green, fill: soft-green)
#v(12pt)

#grid(
  columns: (1fr, 1fr),
  gutter: 12pt,
  [
    #text(size: 12pt, weight: 700, fill: navy)[Portfolio risk signal]
    #v(7pt)
    #grid(
      columns: (1fr, 1fr),
      gutter: 7pt,
      metric("CONFIRMED-FRAUD EVENTS", "14,543", "across all transaction rows", tone: red, fill: soft-red),
      metric("FRAUD EVENT RATE", "2.11%", "row-level confirmed fraud", tone: red, fill: soft-red),
      metric("USERS WITH FRAUD", "299", "eligible ranking population", tone: navy, fill: soft-blue),
      metric("NON-POSITIVE AMOUNTS", "12,023", "excluded from severity", tone: amber, fill: soft-amber),
    )
  ],
  [
    #text(size: 12pt, weight: 700, fill: navy)[Risk by transaction type]
    #v(7pt)
    #set text(size: 7.4pt)
    #table(
      columns: (1.45fr, 1fr, 1fr, 0.9fr),
      inset: (x: 5pt, y: 5pt),
      stroke: (x, y) => if y == 0 { 0pt } else { (bottom: 0.35pt + line-col) },
      fill: (x, y) => if y == 0 { navy } else if calc.rem(y, 2) == 0 { rgb("#f7f9fb") } else { white },
      table.header(
        text(fill: white, weight: 700)[TYPE],
        text(fill: white, weight: 700)[ROWS],
        text(fill: white, weight: 700)[FRAUD],
        text(fill: white, weight: 700)[RATE],
      ),
      [Bank transfer], [15,858], [1,230], [7.76%],
      [ATM], [47,324], [2,236], [4.72%],
      [Top up], [132,561], [3,792], [2.86%],
      [Card payment], [436,570], [6,849], [1.57%],
      [P2P], [56,338], [436], [0.77%],
    )
    #v(8pt)
    #text(size: 7.8pt, fill: muted)[Bank transfer has the highest event rate, while card payment generates the largest event count. Control allocation should therefore distinguish concentration from frequency.]
  ],
)
#v(13pt)

#text(size: 12pt, weight: 700, fill: navy)[What the growth rate does—and does not—say]
#v(5pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  callout([Supported.], [The file supports a stricter behavioural proxy: at least two card-payment rows and no confirmed fraud among the same KYC-PASSED denominator.], tone: green, fill: soft-green),
  callout([Not supported.], [The file has no app installs, sign-up cohort, timestamps, settlement status or fixed fraud-maturation window. It cannot establish a true app funnel or retention rate.], tone: red, fill: soft-red),
)
#v(9pt)
#text(size: 7.3pt, fill: muted)[Governance implication: label 71.74% as an internal sustainable-behaviour sensitivity. Do not silently replace a contemporaneous conversion KPI with an ex-post fraud outcome.]

#pagebreak()

// -----------------------------------------------------------------------------
// Page 3 — top five ranking
// -----------------------------------------------------------------------------
#page-title(
  [SECTION 02 · PRIORITY QUEUE],
  [The five investigation priorities],
  subtitle: [All five combine sustained confirmed-fraud activity with multi-method breadth; amount alone does not determine rank.],
)

#image("assets/top5_priority_scores.png", width: 100%, height: 8.6cm, fit: "contain")
#v(6pt)

#set text(size: 7.1pt)
#table(
  columns: (0.45fr, 3.0fr, 0.7fr, 0.8fr, 0.65fr, 0.8fr, 0.85fr),
  inset: (x: 4pt, y: 5pt),
  stroke: (x, y) => if y == 0 { 0pt } else { (bottom: 0.35pt + line-col) },
  fill: (x, y) => if y == 0 { navy } else if calc.rem(y, 2) == 0 { rgb("#f7f9fb") } else { white },
  align: (center, left, right, right, right, right, right),
  table.header(
    text(fill: white, weight: 700)[RANK],
    text(fill: white, weight: 700)[USER ID],
    text(fill: white, weight: 700)[SCORE],
    text(fill: white, weight: 700)[EVENTS],
    text(fill: white, weight: 700)[METHODS],
    text(fill: white, weight: 700)[MARKETS],
    text(fill: white, weight: 700)[SEVERITY RANK],
  ),
  [1], uid("dc283b17-bbe1-4ae9-", "a11c-0029d5ae71d9"), [99.4], [1,029], [5], [11], [1],
  [2], uid("b8271606-4633-4d8f-", "8729-a2c8ebb8a49f"), [97.8], [340], [5], [3], [6],
  [3], uid("25c2ecb3-5ec7-4fa6-", "8fc3-bbcf3a691217"), [97.6], [460], [5], [5], [31],
  [4], uid("5c75c857-61f0-400e-", "ac7b-25451c57e8de"), [96.6], [238], [5], [3], [20],
  [5], uid("4ee8690a-ebf7-435b-", "9fe2-103e8f83edc6"), [96.0], [508], [5], [8], [84],
)
#v(10pt)

#callout(
  [Why these five.],
  [Each user has confirmed fraud across all five observed transaction methods. The ranking then separates them through event persistence, conservative fraud-rate conviction, excess fraud versus expected transaction mix, cross-market breadth and a deliberately limited amount-severity signal.],
  tone: green,
  fill: soft-green,
)
#v(8pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  rect(fill: soft-red, stroke: 0.5pt + line-col, radius: 6pt, inset: 10pt)[
    #text(weight: 700, fill: red)[Immediate escalation]
    #v(4pt)
    #text(size: 7.6pt)[Ranks 1 and 4 are observed with KYC state PENDING. That does not prove a control failure, but it makes onboarding and state-transition evidence an immediate review item.]
  ],
  rect(fill: soft-blue, stroke: 0.5pt + line-col, radius: 6pt, inset: 10pt)[
    #text(weight: 700, fill: blue)[Cross-functional response]
    #v(4pt)
    #text(size: 7.6pt)[Join transaction history with devices, IPs, beneficiaries, funding sources, prior alerts and linked-account evidence before deciding on restrictions or filings.]
  ],
)
#v(8pt)
#text(size: 6.9pt, fill: muted)[“Market” means distinct merchant country observed on fraud-labelled rows. It is an operational breadth signal, not an inference about attacker nationality.]

#pagebreak()

// -----------------------------------------------------------------------------
// Page 4 — target-by-target rationale
// -----------------------------------------------------------------------------
#page-title(
  [SECTION 03 · INVESTIGATIVE RATIONALE],
  [Why each target made the cut],
  subtitle: [The strongest signals are persistent, statistically convincing and operationally broad patterns.],
)

#target-card(
  [1],
  [dc283b17-bbe1-4ae9-a11c-0029d5ae71d9],
  [99.4], [1,029], [11], [1], [PENDING],
  [Map the multi-vector campaign and linked infrastructure. This user leads every core component and spans the broadest merchant-country footprint.],
  fill: soft-green,
)
#v(8pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  target-card(
    [2], [b8271606-4633-4d8f-8729-a2c8ebb8a49f], [97.8], [340], [3], [6], [PASSED],
    [Trace the four-currency footprint and determine whether the five-method pattern shares devices, beneficiaries or funding sources with rank 1.],
  ),
  target-card(
    [3], [25c2ecb3-5ec7-4fa6-8fc3-bbcf3a691217], [97.6], [460], [5], [31], [PASSED],
    [Prioritise method-to-method linkage. The amount signal is not extreme, yet observed fraud materially exceeds that expected from the transaction mix.],
  ),
)
#v(8pt)
#grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  target-card(
    [4], [5c75c857-61f0-400e-ac7b-25451c57e8de], [96.6], [238], [3], [20], [PENDING],
    [Review onboarding progression and why a PENDING profile accumulated a broad, fully fraud-labelled transaction history across all five methods.],
    fill: soft-amber,
  ),
  target-card(
    [5], [4ee8690a-ebf7-435b-9fe2-103e8f83edc6], [96.0], [508], [8], [84], [PASSED],
    [Prioritise scale and dispersion. This user ranks only 84th on amount severity but has 508 confirmed events across eight merchant countries.],
    fill: soft-green,
  ),
)
#v(9pt)
#callout([Selection discipline.], [A high composite score determines review order; it must not replace investigator judgement, customer-victim assessment or legally required case handling.], tone: red, fill: soft-red)

#pagebreak()

// -----------------------------------------------------------------------------
// Page 5 — counterfactual, model and actions
// -----------------------------------------------------------------------------
#page-title(
  [SECTION 04 · GOVERNANCE],
  [Why higher-amount users can rank below the Top 5],
  subtitle: [The counterfactual confirms that the model rewards sustained, broad and statistically convincing abuse—not merely large recorded amounts.],
)

#image("assets/selected_vs_severity_challenger.png", width: 100%, height: 8.1cm, fit: "contain")
#v(5pt)

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  [
    #text(size: 11pt, weight: 700, fill: navy)[Counterfactual evidence]
    #v(5pt)
    #set text(size: 7.25pt)
    #table(
      columns: (1.8fr, 0.65fr, 0.65fr, 0.65fr),
      inset: (x: 4pt, y: 4pt),
      stroke: (x, y) => if y == 0 { 0pt } else { (bottom: 0.35pt + line-col) },
      fill: (x, y) => if y == 0 { navy } else if calc.rem(y, 2) == 0 { rgb("#f7f9fb") } else { white },
      table.header(
        text(fill: white, weight: 700)[USER],
        text(fill: white, weight: 700)[SEV.],
        text(fill: white, weight: 700)[EVENTS],
        text(fill: white, weight: 700)[RANK],
      ),
      [1632f5e0…63d3], [99.7], [41], [91],
      [11fa06ae…138a], [99.3], [63], [54],
      [5151da7c…5db3], [99.0], [113], [22],
    )
    #v(6pt)
    #text(size: 7.25pt, fill: muted)[These users show stronger normalised amount signals than several selected targets, but far fewer confirmed events and narrower behavioural footprints.]
  ],
  [
    #text(size: 11pt, weight: 700, fill: navy)[Model weights]
    #v(5pt)
    #grid(
      columns: (auto, 1fr),
      column-gutter: 8pt,
      row-gutter: 5pt,
      text(weight: 700, fill: green)[30%], [Repeatability],
      text(weight: 700, fill: green)[25%], [Conservative fraud-rate conviction],
      text(weight: 700, fill: green)[20%], [Abnormality versus transaction mix],
      text(weight: 700, fill: green)[15%], [Method, merchant-country and currency breadth],
      text(weight: 700, fill: amber)[10%], [Currency/type-normalised amount severity],
    )
    #v(7pt)
    #text(size: 7.25pt, fill: muted)[Birth year, home country and other demographics are excluded. Mixed currencies are never summed. Non-positive amounts are excluded from severity scoring.]
  ],
)
#v(10pt)

#text(size: 11pt, weight: 700, fill: navy)[Recommended next actions]
#v(5pt)
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 8pt,
  rect(fill: soft-red, stroke: 0.5pt + line-col, radius: 6pt, inset: 9pt)[
    #text(weight: 700, fill: red)[0–48 hours]
    #v(3pt)
    #text(size: 7.2pt)[Open the five cases, preserve evidence, and compare shared devices, IPs, counterparties, beneficiaries and funding sources.]
  ],
  rect(fill: soft-blue, stroke: 0.5pt + line-col, radius: 6pt, inset: 9pt)[
    #text(weight: 700, fill: blue)[Within 30 days]
    #v(3pt)
    #text(size: 7.2pt)[Back-test investigator outcomes, false positives and realised loss. Challenge weights and document any override.]
  ],
  rect(fill: soft-green, stroke: 0.5pt + line-col, radius: 6pt, inset: 9pt)[
    #text(weight: 700, fill: green)[Before production]
    #v(3pt)
    #text(size: 7.2pt)[Add timestamps, settlement and recovery data, network features and formal model approval. Keep human review in the decision loop.]
  ],
)
#v(9pt)
#callout([Final control statement.], [This model is suitable for investigative triage on the supplied file. It is not suitable for automated customer restrictions, suspicious-activity filing decisions or public performance disclosure without enrichment and independent validation.], tone: red, fill: soft-red)
#v(8pt)
#text(size: 7pt, weight: 700, fill: navy)[References]
#v(2pt)
#text(size: 6.8pt, fill: muted)[[1] Supplied `fin_crime_data.csv`, 688,651 transaction rows and 8,021 unique users. [2] Private repository `Razije/revolut-fincrime-growth-risk-audit`, analysis commit `d0ee49b`; deterministic outputs in `outputs/`. The raw dataset is not committed.]
