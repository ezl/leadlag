from projectimports import *
from correlation import get_corr

def get_next_position(VXX_current_position, SPY_prices, VXX_prices, SPY_yields_standard_deviation):
    '''Input: trailing price history [and yield std deviation]
       Output: position you should have for the next period
    '''
    # don't trade beginning of day
    if len(SPY_prices) < 0:
        return 0

    SPY_yields = np.hstack(( 0, np.diff(np.log(SPY_prices)) ))
    SPY_last_yield = SPY_yields[-1]

    VXX_last_price = VXX_prices[-1]

    lower_bound = 5 * SPY_yields_standard_deviation
    upper_bound = 8 * SPY_yields_standard_deviation
    exit_threshold = 3 * SPY_yields_standard_deviation

    # compute the ideal position

    # default to current position
    ideal_position = VXX_current_position

    # entry conditions
    standard_notional_trade_value = 1.00
    standard_number_of_shares = standard_notional_trade_value / VXX_last_price

    if lower_bound < abs(SPY_last_yield) < upper_bound:
        ideal_position = -1 * standard_number_of_shares * cmp(SPY_last_yield, 0)

    # exit conditions
    # TODO: consider only exiting after 2 consecutive bad signals
    if (VXX_current_position > 0 and SPY_last_yield > exit_threshold) or \
       (VXX_current_position < 0 and SPY_last_yield < -exit_threshold):
        ideal_position = 0

    # don't bother changing the trade unless the change is significant
#    if not (VXX_current_position == 0 or ideal_position == 0):
#        if abs(np.log(ideal_position / VXX_current_position)) < 0.15:
    if cmp(ideal_position, 0) == cmp(VXX_current_position, 0):
            ideal_position = VXX_current_position

    return ideal_position

def backtest_one_day(SPY_prices, VXX_prices, previous_day_yield_standard_deviation):
    assert SPY_prices.shape == VXX_prices.shape

    # set parameters
    cost_per_share = .03

    SPY_price_changes = np.hstack((0, np.diff(SPY_prices)))
    VXX_price_changes = np.hstack((0, np.diff(VXX_prices)))
    SPY_yields = np.hstack((0, np.diff(np.log(SPY_prices))))
    VXX_yields = np.hstack((0, np.diff(np.log(VXX_prices))))

    positions = np.zeros_like(SPY_prices)
    for i in range(len(SPY_prices)):
        positions[i] = get_next_position(VXX_current_position=positions[i-1],
                                         SPY_prices=SPY_prices[:i + 1],
                                         VXX_prices=VXX_prices[:i + 1],
                                         SPY_yields_standard_deviation=previous_day_yield_standard_deviation)
    positions[-1] = 0 # always close out at end of day
    trades = np.hstack((0, np.diff(positions)))
    trade_made = trades != 0
    transaction_costs = abs(trades) * cost_per_share
    pnls = positions[:-1] * VXX_price_changes[1:]

#    ipshell("wtf")
    return sum(pnls), sum(transaction_costs), np.std(SPY_yields), sum(trade_made)

def main():
    with h5py.File(filename) as root:
        trade_dates = list(root)[start_day:end_day]
        pnls = np.zeros(len(trade_dates))
        costs = np.zeros(len(trade_dates))
        VXX_closes = np.zeros(len(trade_dates))
        SPY_closes = np.zeros(len(trade_dates))
        trade_counts = np.zeros(len(trade_dates))
        std = 0.00015
        for day, trade_date in enumerate(trade_dates):
            # print trade_date
            names = root[trade_date]["names"].value
            SPY_prices = root[trade_date][("prices")].value[:, 0][:]
            VXX_prices = root[trade_date][("prices")].value[:, 1][:]
            epoch_times = root[trade_date]["dates"].value

            SPY_closes[day] = SPY_prices[-1]
            VXX_closes[day] = VXX_prices[-1]

            pnls[day], costs[day], std, trade_counts[day] = \
                                   backtest_one_day(SPY_prices, VXX_prices, std)

        running_pnls = np.cumsum(pnls)
        running_costs = np.cumsum(costs)
        running_nets = running_pnls - running_costs

        total_pnl = sum(pnls)
        total_cost = sum(costs)

        print " *" * 40
        print "Net pnl: %s" % (total_pnl - total_cost)
        print "Trading pnl: %s" % total_pnl
        print "Gross cost: %s" % total_cost
        print "Shares traded: %s" % "hello"
        print "Average: %s" % (np.mean(pnls) - np.mean(costs))
        print "Standard Deviation: %s" % np.std(pnls - costs)
        print "Average Trades/Day: %s" % np.mean(trade_counts)
        print

        ax1 = pyplot.subplot(3, 2, 1)
        pyplot.plot(VXX_closes, "r")
        ax1.set_ylabel("VXX (red)")
        ax2 = pyplot.twinx()
        pyplot.plot(SPY_closes, "k")
        ax2.set_ylabel("SPY (black)")
        pyplot.title("VXX and SPY Closing Px")

        pyplot.subplot(3, 2, 3)
        pyplot.plot(pnls)
        pyplot.plot(costs)
        pyplot.title("PnL v cost")

        pyplot.subplot(3, 2, 2)
        pyplot.plot(running_pnls)
        pyplot.plot(running_costs)
        pyplot.title("Running PnL v Cost")

        pyplot.subplot(3, 2, 4)
        pyplot.plot(running_nets)
        pyplot.title("Running Net")

        pyplot.subplot(3, 2, 5)
        pyplot.bar(range(len(trade_counts)), trade_counts)
        pyplot.title("Trade Count")

        pyplot.subplot(3, 2, 6)
        correlation = get_corr(offset=1)
        pyplot.plot(correlation)
        pyplot.title("Correlation (1 period lag)")

        pyplot.show()

if __name__ == "__main__":
    main()
