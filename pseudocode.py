Basic theory for DR:
VXX tracks a portfolio of VIX futures contracts, so it has exposure to volatility. SPY is the S&P500 index ETF. There is a fairly well observed inverse correlation between stock index level and volatility levels, so one would expect the SPY and VXX to be negatively correlated.

In options markets, there is no discernable lead-lag relationship between stock levels and volatility, but for whatever reason, the VXX yields appears to lag the SPY. It is several markets displaced and technically trades independently though, so its conceivable that they would be out of sync. Comparison SPY with VIX+timeoffset(x) shows decreasing correlation strength for increasing values of x, as expected. In the last 3 months, the SPY/VXX correlation with no time offset has increased in magnitude and the timeshifted correlations have weakened, suggesting that the market may be getting more efficient.

The basic strategy here is:
General relationship: if SPY goes up, VXX will go down (and vice versa).  This strategy reacts to the series of period to period SPY returns. The time delay is what we are exploiting here, so we will measure period yields of SPY. If the magnitude of any particular yield is particularly large, consider that VXX may react in the next time period, so make the appropriate trade.

[not sure if its clear, but i use "yields" and "returns" interchangably to mean "the % change in value over a given time interval"]

Basic Details:
There should be a price listener that logs prices at set intervals (or constant intervals, but can deliver subsets of the price series).
Convert those prices to returns:

In [4]: SPY_prices 
Out[4]: 
array([ 120.665,  120.685,  120.665,  120.635,  120.655,  120.685,
        120.695,  120.675,  120.715,  120.725,  120.775,  120.785,
        120.775,  120.795,  120.805])

In [5]: SPY_yields = np.diff(np.log(SPY_prices))

In [6]: SPY_yields
Out[6]: 
array([  1.65734411e-04,  -1.65734411e-04,  -2.48653130e-04,
         1.65775623e-04,   2.48611918e-04,   8.28569062e-05,
        -1.65720678e-04,   3.31413898e-04,   8.28363155e-05,
         4.14078681e-04,   8.27951648e-05,  -8.27951648e-05,
         1.65583475e-04,   8.27814570e-05])

In [7]: len(SPY_prices)
Out[7]: 15

In [8]: len(SPY_yields)
Out[8]: 14

These yields are used as the basis for decisions regarding trades.

Compute the standard deviation of the previous N returns. wrap back to the previous day if necessary.

If the last yield is greater than $STANDARD_DEVIATIONS_TO_TRADE then make a trade (or adjust position)

Decide whether to make a trade:

< PSEUDOCODE >

def what_VXX_position_should_i_have(current_VXX_position as integer, SPY_prices as priceseriesarray, VXX_prices as priceseriesarray):

# set some parameters for this trade
    standard_deviation_window = 4 hours
    SPY_yields = diff(ln(SPY_prices))
    last_SPY_yield = SPY_yields[-1]

    # get the standard deviation of last 4 hours worth of yields
    SPY_yields_standard_deviation(SPY_yields, $standard_deviation_window) 

    last_VXX_price = VXX_prices[-1]

    # we trade if the spy_yield is between lower_bound and upper_bound
    # in this case, the sweet spot for good indicators is spy yields that are between 2.5 and 7 "standard deviations" away from the average move
    upper_bound = 2.5 * SPY_yields_standard_deviation
    lower_bound = 7 * SPY_yields_standard_deviation 

# lets compute ideal position
    # number of dollars to allocate to each trade
    # this uses a naive static amount, independent of how "good" the trade is
    standard_notional_value_of_trade = 1000.00
    standard_number_of_shares = standard_notional_value_of_trade / last_VXX_price

    # default to current position.
    desired_position = current_VXX_position

    # if the yield was in the sweet spot, now we have a desired position!
    if lower_bound < abs(last_SPY_yield) < upper_bound:
        # negative correlation, so if spy yield is up, we want to be short. if spy yield is down, we want to be long
        desired_position = -1 * standard_number_of_shares * sign(last_SPY_yield)

    # if the yield is averse to our position, get out.
    # this will make us have positions in places where we wouldn't initiate,
    # but if its already there, just let it ride (from 0 to lower_bound yields, we woudn't initiate, but we won't exit either)
    # broke these into 2 parts for readability.
    if current_VXX_position > 0 and SPY_yield > 0:
        desired_position = 0
    if current_VXX_position < 0 and SPY_yield < 0:
        desired_position = 0

    # we could just return the desired position here, but instead, we'll try to cut down on our costs
    # how? reduce trade volume by comparing to existing position to the yield and
    # don't change the position size if its pretty close to the desired position (within 15%)
    if abs(desired_position - current_VXX_position) / desired_position < 0.15:
        desired_position = current_VXX_position
    return desired_position

        
def main():
    # set program parameters
    interval_length_in_seconds = 10
    price_history_length = 8 hours
    current_VXX_position = get_position(symbol="VXX")

    # have to close every day with zero position. so run until 3pm, then close out positions
    while (its_not_3pm_or_whatever_the_closing_time_is):
        # really getting prices should be more efficient. instead of querying the whole thing, store an array and popping the first, adding to the end
        # but whatever. this is pseudocode
        SPY_prices = get_historical_data(symbol="SPY", start_time=now() - price_history_length, end_time=now(), interval=interval_length_in_seconds)
        VXX_prices = get_historical_data(symbol="VXX", start_time=now() - price_history_length, end_time=now(), interval=interval_length_in_seconds)

        desired_VXX_position = what_VXX_position_should_i_have(current_VXX_position, SPY_prices, VXX_prices)

        # get the right position, if i don't already have it
        if not desired_VXX_position == current_VXX_position:
            trade_quantity = desired_VXX_position - current_VXX_position
            make_trade(symbol="VXX", trade_quantity=trade_quantity, type="market_order")
            current_VXX_position = get_position(symbol="VXX")

    # uh oh! its 3pm! lets get flat!
    current_VXX_position = get_position(symbol="VXX")
    make_trade(symbol="VXX", trade_quantity=-current_VXX_position, type="market_order")

    return lots_of_cash
