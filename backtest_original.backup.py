from projectimports import *
from correlation import get_corr

def backtest_one_day(SPY, VXX, previous_day_std):
    '''
    initial backtest. use spy as an indicator for VXX. if spy 15 second yield is
    between 3 and 7 standard deviations of its previous day's 15 second yield diff

    only have to trade one name, which is quite nice.
    '''
    trade_notional = 1.0
    cost_per_share = .03
    lower_bound = previous_day_std * 4
    upper_bound = previous_day_std * 7

    pnl =[]
    transaction_cost = []
    pos = 0
    trade_count = 0
    SPY_yields = np.hstack((0, np.diff(np.log(SPY))))
    VXX_yields = np.hstack((0, np.diff(np.log(VXX))))
    trade = False
    for spy, vxx, SPY_yield, VXX_yield in zip(SPY, VXX, SPY_yields, VXX_yields):
        pnl.append(pos * VXX_yield)
        pos += pnl[-1]
        if lower_bound < abs(SPY_yield) < upper_bound:
            if SPY_yield > 0:
                if not pos < 0:
                    trade = True
                    num_shares = (pos - trade_notional) / vxx
                    # the error! it has to be PLUS. stupid me. counting almost no costs every time i got short
                    pos = -trade_notional
            if SPY_yield < 0:
                if not pos > 0:
                    trade = True
                    num_shares = (trade_notional - pos) / vxx
                    pos = trade_notional

            if trade == True:
                trade = False
                transaction_cost.append(cost_per_share * abs(num_shares))
                trade_count += 1
    # close position out at end of day no matter what
    if not pos == 0:
        transaction_cost[-1] += (pos / vxx) * (cost_per_share * 2)

    return sum(pnl), sum(transaction_cost), np.std(SPY_yields), trade_count

print " * " * 20
with h5py.File(filename) as root:
    pnl = list()
    naive_cost = list()
    cost = list()
    VXX_close = list()
    SPY_close = list()
    trade_count = list()
    threshold = 0.00
    for trade_date in list(root)[start_day:end_day]:
        # print trade_date
        names = root[trade_date]["names"].value
        SPY = root[trade_date][("prices")].value[:, 0][:]
        SPY_close.append(SPY[-1])
        VXX = root[trade_date][("prices")].value[:, 1][:]
        VXX_close.append(VXX[-1])
        epoch_times = root[trade_date]["dates"].value
        raw_profit, raw_cost, threshold, tc = backtest_one_day(SPY, VXX,
                                                    threshold)
        pnl.append(raw_profit)
        cost.append(raw_cost)
        trade_count.append(tc)

    running_pnl = np.cumsum(pnl)
    running_cost = np.cumsum(cost)
    running_net = running_pnl - running_cost
    pnl = np.array(pnl)
    cost = np.array(cost)
    total_pnl = sum(pnl)
    total_cost = sum(cost)

    print "Net pnl: %s" % (total_pnl - total_cost)
    print "Raw pnl: %s" % total_pnl
    print "Raw cost: %s" % total_cost
    print "Average: %s" % (np.mean(pnl) - np.mean(cost))
    print "Standard Deviation: %s" % np.std(pnl - cost)
    print "Average Trades/Day: %s" % np.mean(trade_count)
    print

    ax1 = pyplot.subplot(3, 2, 1)
    pyplot.plot(VXX_close, "r")
    ax1.set_ylabel("V (red)")
    ax2 = pyplot.twinx()
    pyplot.plot(SPY_close, "k")
    ax2.set_ylabel("S (black)")
    pyplot.title("V and S Closing Px")

    pyplot.subplot(3, 2, 3)
    pyplot.plot(pnl)
    pyplot.plot(cost)
    pyplot.title("PnL v cost")

    pyplot.subplot(3, 2, 2)
    pyplot.plot(running_pnl)
    pyplot.plot(running_cost)
    pyplot.title("Running PnL v Cost")

    pyplot.subplot(3, 2, 4)
    pyplot.plot(running_net)
    pyplot.title("Running Net")

    pyplot.subplot(3, 2, 5)
    pyplot.bar(range(len(trade_count)), trade_count)
    pyplot.title("Trade Count")

    pyplot.subplot(3, 2, 6)
    correlation = get_corr(offset=1)
    pyplot.plot(correlation)
    pyplot.title("Correlation (1 period lag)")

    pyplot.show()

