
from datetime import datetime
import pandas as pd
from scipy import integrate
import time



def integrate_func(t, inputs):
    for i, row in inputs.iterrows():
        sec_since_epoch = pd.to_datetime(row['datetime']).timestamp()
        if t < sec_since_epoch:
            # t is now between this timestamp and the prev timestamp
            time_gap = sec_since_epoch - pd.to_datetime(inputs.iloc[i-1]['datetime']).timestamp()
            prod_diff = inputs.iloc[i]['production'] - inputs.iloc[i-1]['production']
            return row['production'] - (prod_diff * (sec_since_epoch - t) / time_gap)
    # if we got this far, it means t is more recent than any data point -> assume most recent production
    return inputs.iloc[len(inputs) - 1]['production']


def main():
    inputs = pd.read_json('denmark_1day.json', lines=True)
    earliest_time, latest_time = inputs.min()['datetime'], inputs.max()['datetime']
    inputs['production'] = [sum(filter(None, row['data']['production'].values()))
                            if row['kind'] == 'ElectricityProduction'
                            else row['data']['netFlow']
                            for _, row in inputs.iterrows()]
    inputs = inputs[['datetime', 'zone_key', 'production']]  # we'll only need these
    integration_results = pd.DataFrame(columns=['zone_key', 'start_time', 'end_time', 'net_prod'])
    for zk in inputs['zone_key'].unique():
        filtered = inputs[inputs.zone_key == zk]
        ordered = filtered.sort_values('datetime').reset_index(drop=True)
        secs_start = pd.to_datetime(earliest_time).timestamp()
        # now the fun part ... for every hour interval, use scipy to integrate to find total production for the hour
        while secs_start < pd.to_datetime(latest_time).timestamp():
            secs_end = secs_start + 3600  # add 3600s = 1hr
            res = integrate.quad(integrate_func, secs_start, secs_end, args=(ordered,), limit=2)
            # setting limit higher could improve accuracy, but greatly increases runtime.
            # https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.quad.html
            integration_results = pd.concat([integration_results, pd.DataFrame({
                'zone_key': [zk],
                'start_time': [datetime.utcfromtimestamp(secs_start)],
                'end_time': [datetime.utcfromtimestamp(secs_end)],
                'net_prod': [res[0] / 3600.0]  # divide by 3600 to convert from seconds back to hrs
            })])
            secs_start = secs_end
        results_by_zone = pd.DataFrame(columns=['zone_key', 'start_time', 'end_time', 'net_prod'])
        for i, row in integration_results.iterrows():
            if '->' in row['zone_key']:  # will need to generate 2 rows
                zk1, zk2 = row['zone_key'].split('->')
                results_by_zone = pd.concat([results_by_zone, pd.DataFrame({
                    'zone_key': [zk1, zk2],
                    'start_time': [row['start_time'], row['start_time']],
                    'end_time': [row['end_time'], row['end_time']],
                    'net_prod': [-row['net_prod'], row['net_prod']]
                })])
            else:  # just 1 row
                results_by_zone = pd.concat([results_by_zone, pd.DataFrame({
                    'zone_key': [row['zone_key']],
                    'start_time': [row['start_time']],
                    'end_time': [row['end_time']],
                    'net_prod': [row['net_prod']]
                })])

        # now we just need to combine rows which represent the same zone and start/end times
        consumption_by_zone = results_by_zone.groupby(by=['zone_key', 'start_time', 'end_time']).sum().reset_index()
        consumption_by_zone.to_csv('consumption_by_zone.csv', index=False)

if __name__ == "__main__":
    start = time.time()
    main()
    runtime = time.time() - start
    print(f"Runtime: {runtime} seconds")
