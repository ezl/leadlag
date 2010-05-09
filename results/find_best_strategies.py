import numpy as np
from scipy.stats import percentileofscore
import re
import os
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed("Dropping to IPython shell")

results_path = '/home/eric/src/trading/vix_spu_pair_trade/results/'
results_path = '/Users/E/Documents/trading/vix_spu_pair_trade/results'
percentile_cutoff = 60.0


params = ['net', 'trade', 'cost', 'avg', 'std', 'trades_per_day', 'leb', 'ueb', 'et', 'bs']
net_pattern = re.compile(r'Net:([-\d\.e]+),')
trade_pattern = re.compile(r'Trade:([-\d\.e]+),')
cost_pattern = re.compile(r'Cost:([-\d\.e]+),')
avg_pattern = re.compile(r'Avg:([-\d\.e]+) ')
std_pattern = re.compile(r'Std:([-\d\.e]+) ')
leb_pattern = re.compile(r'leb:([-\d\.e]+),')
ueb_pattern = re.compile(r'ueb:([-\d\.e]+),')
et_pattern = re.compile(r' et:([-\d\.e]+),')
bs_pattern = re.compile(r'bs:([-\d\.e]+),')
trades_per_day_pattern = re.compile(r'Trades/Day:([-\d\.e]+),')

csv_pattern = re.compile('.csv')
directory = os.listdir(results_path)
csvs = [csv for csv in directory if re.search(csv_pattern, csv)]

for param in params:
    locals()[param] = dict()
percentile = dict()
is_good_strategy = dict()

for filename in csvs:
    print filename
    with open(filename, "r") as f:
        file_rows = f.readlines()

        net[filename] = [re.search(net_pattern, row).group(1) for row in file_rows]
        for param in params:
            locals()[param][filename] = [re.search(locals()[param + "_pattern"], row).group(1) for row in file_rows]

        net[filename] = [re.search(net_pattern, row).group(1) for row in file_rows]
        percentile[filename] = np.array(map(lambda x: percentileofscore(net[filename], x), net[filename]))
 #        is_good_strategy[filename] = np.array(map(lambda x: x > percentile_cutoff, percentile[filename]))
        is_good_strategy[filename] = percentile[filename] > percentile_cutoff

survived_all_filters = reduce(lambda a, b: a * b, [is_good_strategy[k] for k in is_good_strategy.keys()])

if sum(survived_all_filters) == 0:
    print "No strategy survives"
else:
    strategy_index = np.arange(len(survived_all_filters))
    winners = [strat for strat in strategy_index * survived_all_filters if not strat == 0]
    winners_returns = [net[day][w] for day in csvs for w in winners]

    for param in params:
        print
        for csv in csvs:
            print csv, param,
            print [locals()[param][csv][w] for w in winners]
    # print [[param[w] for w in winners] for param in params]
    # print "* " * 40
    # for param in ['leb', 'ueb', 'et', 'bs']:
    #     print [locals()[param][csv][w]]
ipshell()
