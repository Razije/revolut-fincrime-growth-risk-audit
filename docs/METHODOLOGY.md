# Risk-Priority Methodology

## Objective

The model ranks **users with at least one confirmed-fraud event** for investigative attention. It does not estimate guilt, nationality, realised loss or the legal status of a customer. The word “target” means an investigation target in an internal risk queue.

## Why total value is not the ranking method

`AMOUNT` is a recorded transaction amount, not a loss, chargeback or recovery field. The dataset contains multiple fiat and crypto currencies and supplies no dated foreign-exchange rates. Summing those values into one portfolio number would be false precision. The model instead calculates the percentile of each positive amount within its **transaction type × currency** peer group. A user’s amount-severity signal is the mean of their three highest fraud-event percentiles. It carries only 10% of the final score.

## Eligible population

Only users with at least one row where `IS_FRAUD` is true are scored. In the supplied dataset, that population contains 299 users and 14,543 confirmed-fraud events.

## Components

| Component | Weight | Definition | Risk rationale |
|---|---:|---|---|
| Repeatability | 30% | Percentile rank of `log(1 + confirmed fraud events)` | Persistent activity creates continuing operational exposure and investigatory value. |
| Conviction | 25% | Percentile rank of the 95% Wilson lower bound for the user’s fraud-event rate | Rewards high fraud concentration supported by sufficient observations; avoids equating a single 100% observation with a large 100% pattern. |
| Abnormality | 20% | Percentile rank of the excess-fraud z-score relative to global fraud rates for the user’s transaction-type mix | Prioritises behaviour that is abnormal even after accounting for the riskiness of the methods used. |
| Breadth | 15% | 50% method breadth, 35% merchant-country breadth, 15% currency breadth | Multi-vector and cross-market activity can indicate adaptable, scalable abuse requiring coordinated investigation. |
| Amount severity | 10% | Mean of the top three positive fraud-event percentiles within type × currency | Preserves a severity signal without treating mixed-currency transaction amount as loss. |

The score is the weighted sum of the five 0–100 percentile components. Ties are resolved by confirmed-event count and then stable user ID ordering.

## Deliberate exclusions

Birth year, home country and other demographic attributes are excluded. Merchant country is used only to describe the operational breadth of observed transactions; it is not used to infer an attacker’s nationality. No recency, velocity, device, IP or network signal is used because those fields are absent. No automated customer restriction should be driven by this output.

## Why the Top 5 can outrank users with higher amount signals

The committed `outputs/high_severity_not_selected.csv` isolates non-selected users with the strongest currency/type-normalised amount-severity scores. Their lower composite ranks provide an explicit counterfactual. For example, a user can score in the 99th percentile for amount severity yet rank outside the Top 50 because the file shows fewer confirmed events, fewer fraud methods and less geographic breadth. Conversely, a selected user may have only a mid-tier severity rank but remain a priority because hundreds of confirmed events span all five transaction types and multiple merchant countries.

## Required next data

A production model should add timestamps, authorisation and settlement state, reversals, refunds, chargebacks, realised loss, recoveries, beneficiary/counterparty identifiers, devices, IP/network signals, case outcomes, false-positive outcomes and control-action history. Those fields are necessary for velocity, recency, network centrality, loss severity and intervention effectiveness.
