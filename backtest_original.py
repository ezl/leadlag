from projectimports import *
from correlation import get_corr

def backtest_one_day(SPY, VXX, previous_day_std, leb=4, ueb=7, et=0, bs=3):
    '''
    initial backtest. use spy as an indicator for VXX. if spy 15 second yield is
    between 4 and 7 standard deviations of its previous day's 15 second yields,
    then trade one unit of VXX.

    only have to trade one name, which is quite nice.
    '''
    trade_notional = 1.0
    cost_per_share = .015
    lower_bound = previous_day_std * leb
    upper_bound = previous_day_std * ueb
    exit_threshold = previous_day_std * et
    bad_signals_allowed = bs

    pnl =[]
    transaction_cost = []
    pos = 0
    trade_count = 0
    consecutive_averse_signals = 0
    SPY_yields = np.hstack((0, np.diff(np.log(SPY))))
    VXX_yields = np.hstack((0, np.diff(np.log(VXX))))
    trade = False
    for spy, vxx, SPY_yield, VXX_yield in zip(SPY, VXX, SPY_yields, VXX_yields):
        pnl.append(pos * VXX_yield)
        pos += pnl[-1]
        if lower_bound < abs(SPY_yield) < upper_bound:
            desired_pos = -cmp(SPY_yield, 0) * trade_notional
            if not cmp(desired_pos, 0) * cmp(pos, 0) == 1:
                shares_transacted = abs((desired_pos - pos) / vxx)
                pos = desired_pos
                transaction_cost.append(cost_per_share * shares_transacted)
                trade_count += 1
        if (pos > 0 and SPY_yield > exit_threshold) or \
           (pos < 0 and SPY_yield < -exit_threshold):
            consecutive_averse_signals += 1
            if consecutive_averse_signals >= bad_signals_allowed:
                shares_transacted = abs(pos) / vxx
                transaction_cost.append(cost_per_share * shares_transacted)
                trade_count += 1
                pos = 0
                consecutive_averse_signals = 0
        else:
            consecutive_averse_signals = 0

    # close position out at end of day no matter what
    if not pos == 0:
        transaction_cost[-1] += abs(pos / vxx) * (cost_per_share * 1)

    return sum(pnl), sum(transaction_cost), np.std(SPY_yields), trade_count

def backtest_period(plot=False, **kwargs):
    with h5py.File(filename) as root:
        pnl = list()
        cost = list()
        VXX_close = list()
        VXX_vol = list()
        SPY_close = list()
        trade_count = list()
        threshold = 0.00015
        for trade_date in list(root)[start_day:end_day]:
            # print trade_date
            names = root[trade_date]["names"].value
            SPY = root[trade_date][("prices")].value[:, 0][:]
            SPY_close.append(SPY[-1])
            VXX = root[trade_date][("prices")].value[:, 1][:]
            VXX_close.append(VXX[-1])
            epoch_times = root[trade_date]["dates"].value
            raw_profit, raw_cost, threshold, tc = backtest_one_day(SPY, VXX,
                                                        threshold, **kwargs)
            pnl.append(raw_profit)
            cost.append(raw_cost)
            trade_count.append(tc)
i           VXX_vol.append(np.std(np.diff(np.log(VXX))))
        running_pnl = np.cumsum(pnl)
        running_cost = np.cumsum(cost)
        running_net = running_pnl - running_cost
        pnl = np.array(pnl)
        cost = np.array(cost)
        total_pnl = sum(pnl)
        total_cost = sum(cost)

        print "Net:%s," % (total_pnl - total_cost),
        print "Trade:%s," % total_pnl,
        print "Cost:%s," % total_cost,
        print "Avg:%s" % (np.mean(pnl) - np.mean(cost)),
        print "Std:%s" % np.std(pnl - cost),
        print "Trades/Day:%s," % np.mean(trade_count),
        for key in kwargs:
            print "%s:%s," % (key, kwargs[key]),
        print

        if plot==True:
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
            pyplot.plot(trade_count)
        #     pyplot.bar(range(len(trade_count)), trade_count)
            pyplot.title("Trade Count")

            pyplot.subplot(3, 2, 6)
            correlation = get_corr(offset=1)
            pyplot.plot(correlation)
            pyplot.title("Correlation (1 period lag)")

            pyplot.subplot(3, 2, 6)
            pyplot.plot(VXX_vol)
            pyplot.show()

if __name__ == "__main__":
    backtest_period(leb=5,
                    ueb=8,
                    et=0,
                    bs=6,
                    plot=True)

if __name__ == "__main_dd_":
    for lower_entry_bound in range(2,8):
        for upper_entry_bound in range(lower_entry_bound + 1, 10):
            for exit_threshold in range(lower_entry_bound + 1):
                for bad_signals in range(1, 10):
                    backtest_period(leb=lower_entry_bound,
                        ueb=upper_entry_bound,
                        et=exit_threshold,
                        bs=bad_signals)
#     backtest_period()

