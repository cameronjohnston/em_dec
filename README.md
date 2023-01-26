# Electricity Maps - Data Engineering Challenge

How to run:
- install python. I used python 3.10.
- pip install scipy and pandas. I used pandas 1.5.3 and scipy 1.10.0
- run python gen_hourly_consumption.py

1. How did I solve the problem?

        a. Reviewed the dataset to confirm it makes sense alongside the problem description.
        b. Considered how to take the series of point-in-time data points and use it to estimate consumption for each 1-hour period. See assumption A.
        c. Given assumption A, considered how to code this. Realized some integration would simplify the amount of coding required, so researched scipy as I know it has a bunch of math stuff. Discovered by using its "quad" function, I could pass my own function to integrate over, as well as my own parameter to that function. Figured it's worth a shot.
        d. Coded solution: parse the production for each row, remove unneeded columns, save the data points in a Pandas df, use scipy to integrate, and save results into a Pandas df.
2. Assumptions:

         a. Since time-series data points are provided, the production/import/export in between those times may fluctuate greatly, but the best guess we can make is that the values will trend linearly towards the next data point. For example, just considering production: suppose we have 3 data points: 50MW at 3am, 80MW at 6am, and 160MW at 8am. We should assume that production is 60MW at 4am, 70MW at 5am, and 120MW at 7am.
         b. After the final data point, production/import/export remains the same until now. Continuing with the data points above, we assume production has stayed at 160MW since 8am. Don't tell me you're reading this before 8am, you work at a tech startup...
3. Areas for improvement:

         a. Runtime. The scipy integration function is slow, and coding my own logic to calculate total production/import/export across each hour interval I assume would fix that. 
         b. Cmd line args to offer flexibility without code change. Most beneficial would be the "limit" parameter to the scipy "quad" integrate function, as it has a huge impact on runtime as trade-off vs. accuracy. Also would be nice to add which input file to read, exact location/name of output csv, and ability to optionally open csv once complete.
         c. Some QA on the input dataset. e.g. what if there's a zone_key formatted like a->b->c->d, or a "ElectricityProduction" row without any "production" in the dict? My code would exit with error.
         d. Maybe some more descriptive variable names.
         e. Proper library management, for example using poetry.
         f. Prettier readme