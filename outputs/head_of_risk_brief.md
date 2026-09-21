# Head of Risk Brief: Growth Audit and Top 5 Priority Targets

## Executive answer

Marketing's rate is reproducible as **78.17%** (5,463 / 6,989). The stricter repeat-use and no-confirmed-fraud proxy is **71.74%** (5,014 / 6,989), a reduction of **6.42 percentage points**.

The dataset contains **14,543 confirmed-fraud events** involving **299 users**. The Top 5 below are investigative priorities, not legal conclusions about identity or culpability.

## Top 5 investigative priorities

| Rank | User ID | Score | Fraud events | Fraud rate | Types | Merchant countries | Severity-only rank |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `dc283b17-bbe1-4ae9-a11c-0029d5ae71d9` | 99.4 | 1029 | 100.0% | 5 | 11 | 1 |
| 2 | `b8271606-4633-4d8f-8729-a2c8ebb8a49f` | 97.8 | 340 | 100.0% | 5 | 3 | 6 |
| 3 | `25c2ecb3-5ec7-4fa6-8fc3-bbcf3a691217` | 97.6 | 460 | 100.0% | 5 | 5 | 31 |
| 4 | `5c75c857-61f0-400e-ac7b-25451c57e8de` | 96.6 | 238 | 100.0% | 5 | 3 | 20 |
| 5 | `4ee8690a-ebf7-435b-9fe2-103e8f83edc6` | 96.0 | 508 | 100.0% | 5 | 8 | 84 |

### Why each target made the cut

**#1 `dc283b17-bbe1-4ae9-a11c-0029d5ae71d9`.** Priority rank 1: 1029 confirmed events across 5 transaction type(s) and 11 merchant country/countries. Strongest signals: repeatability (100.0/100), conservative fraud-rate conviction (100.0/100), excess fraud versus transaction mix (100.0/100). Amount severity is capped at 10% of the score.

**#2 `b8271606-4633-4d8f-8729-a2c8ebb8a49f`.** Priority rank 2: 340 confirmed events across 5 transaction type(s) and 3 merchant country/countries. Strongest signals: repeatability (98.7/100), conservative fraud-rate conviction (98.7/100), excess fraud versus transaction mix (98.7/100). Amount severity is capped at 10% of the score.

**#3 `25c2ecb3-5ec7-4fa6-8fc3-bbcf3a691217`.** Priority rank 3: 460 confirmed events across 5 transaction type(s) and 5 merchant country/countries. Strongest signals: excess fraud versus transaction mix (99.3/100), repeatability (99.0/100), conservative fraud-rate conviction (99.0/100). Amount severity is capped at 10% of the score.

**#4 `5c75c857-61f0-400e-ac7b-25451c57e8de`.** Priority rank 4: 238 confirmed events across 5 transaction type(s) and 3 merchant country/countries. Strongest signals: repeatability (98.0/100), conservative fraud-rate conviction (98.0/100), excess fraud versus transaction mix (97.7/100). Amount severity is capped at 10% of the score.

**#5 `4ee8690a-ebf7-435b-9fe2-103e8f83edc6`.** Priority rank 5: 508 confirmed events across 5 transaction type(s) and 8 merchant country/countries. Strongest signals: repeatability (99.3/100), conservative fraud-rate conviction (99.3/100), excess fraud versus transaction mix (99.0/100). Amount severity is capped at 10% of the score.

## Why higher-amount users can rank below the Top 5

`AMOUNT` is a transaction amount, not a realised-loss field, and the dataset spans multiple currencies. The model therefore never sums mixed-currency amounts. It converts each positive amount to a percentile within its transaction type and currency, then gives that severity signal only 10% weight. Repeatability, conservative fraud-rate conviction, excess fraud versus expected transaction mix, and attack breadth drive 90%.

| Priority rank | High-severity non-selected user | Severity score | Fraud events | Repeatability | Conviction | Breadth | Why not selected |
|---:|---|---:|---:|---:|---:|---:|---|
| 91 | `1632f5e0-e2da-4668-b487-5cc897b963d3` | 99.7 | 41 | 69.1 | 69.1 | 42.1 | Higher amount-severity signal alone was insufficient: composite rank 91, 41 confirmed events, repeatability 69.1, conviction 69.1, breadth 42.1. |
| 54 | `11fa06ae-839a-4279-b85e-191f57d0138a` | 99.3 | 63 | 80.9 | 80.9 | 57.7 | Higher amount-severity signal alone was insufficient: composite rank 54, 63 confirmed events, repeatability 80.9, conviction 80.9, breadth 57.7. |
| 22 | `5151da7c-4008-43f0-9471-da9bce725db3` | 99.0 | 113 | 91.6 | 91.6 | 66.9 | Higher amount-severity signal alone was insufficient: composite rank 22, 113 confirmed events, repeatability 91.6, conviction 91.6, breadth 66.9. |
| 32 | `9fa08d28-fdf0-49d5-a92c-7fb78512a8ab` | 98.7 | 72 | 83.1 | 83.1 | 82.4 | Higher amount-severity signal alone was insufficient: composite rank 32, 72 confirmed events, repeatability 83.1, conviction 83.1, breadth 82.4. |
| 13 | `1ac43c83-6c00-41cb-943c-7279a79ff2aa` | 98.0 | 143 | 93.0 | 93.0 | 76.1 | Higher amount-severity signal alone was insufficient: composite rank 13, 143 confirmed events, repeatability 93.0, conviction 93.0, breadth 76.1. |

## Model governance

The ranking is deterministic and configurable in `risk_model.json`. Demographics, birth year and home country are excluded from the score. Merchant country is used only as operational attack breadth, not as an attribution of nationality. The file has no timestamps, device/IP data, counterparty network, case loss, chargeback or recovery fields; the ranking is therefore a triage queue for investigation, not an automated customer action or proof that a user is an attacker.

## Limitations

- The file contains no app-install, sign-up or product-eligibility cohort.
- The file contains no timestamps, so distinct-day use, velocity, recency and fixed maturation windows cannot be calculated.
- The file contains no settlement, reversal, refund, chargeback or realised-loss field.
- Confirmed fraud is an ex-post label and should not silently rewrite a contemporaneous conversion KPI.
- User-level priority should be independently reviewed before any restriction, filing or customer-impacting action.

Model version: `1.0.0`. Generated deterministically from the supplied dataset.
