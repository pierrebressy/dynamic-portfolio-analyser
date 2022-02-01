# dynamic-portfolio-analyser

STATE: in development


- dynamic computation of the portfolio content (dynamic = updated with the last data for the products),
- manage `CHF`, `USD` and `EUR`,
- one global view the content as a table with:
  - product symbol,
  - quantity,
  - mean buy price (mean computation if I buy the same product at different times),
  - last known value,
  - P&L (CHF and %),
  - dividende estimate for the year,
- one detailed pie by ratio (%)  with the markets repartition (USA, EUROPE, EMERGING, PACIFIC, MID. EAST),
- one detailed pie by ratio (%)  with products types (CASH, ETF, SHARE),
- one detailed pie by ratio (%) with sectors (TECH, FINANCIALS, ENERGY...),
- one detailed pie by ratio (%) of products in the while portfolio),
- a graph of positive/negatives P&L in % and CHF for each product.

To feed the tool, the data to process must be 'easy' to setup. I choose a text format (YAML):
- a file for **products descriptions** (tickers.yaml): it contains the definition of each product (symbol, description, geographic repartition, sectors repartition)
- a file for **transactions** (transactions.yaml): it contains the list of the whole transactions I have made for the portfolio. It could be:
  - `INSERT_MONEY` when I move money from by bank account to IB in CHF (qty, date),
  - `BUY_CURRENCY` to convert CHF to USD (from/to currencies, qty, rate),
  - `BUY_SHARE` to buy a product (symbol, qty, rate, commission, date).

