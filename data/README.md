# Data directory

Raw data are intentionally **not committed**. Place either of the following here for local use:

- `fin_crime_data.csv.zip`, containing exactly one CSV; or
- `fin_crime_data.csv`.

Required columns:

| Column | Use |
|---|---|
| `USER_ID` | Stable pseudonymous user key |
| `TYPE` | Transaction method and fraud-method breadth |
| `AMOUNT` | Currency/type-normalised severity only; never treated as realised loss |
| `CURRENCY` | Amount peer group |
| `MERCHANT_COUNTRY` | Operational attack breadth only |
| `KYC` | Growth-audit cohort reconstruction and descriptive review |
| `BIRTH_YEAR` | Required by source schema but excluded from risk scoring |
| `COUNTRY` | Required by source schema but excluded from risk scoring |
| `IS_FRAUD` | Confirmed-fraud label |

Do not commit production customer data, direct identifiers, investigator notes or suspicious-activity reports. The repository `.gitignore` blocks CSV and ZIP files under `data/` by default.
