from projectimports import *

# offset describes the number of periods the second name lags the first

def get_corr(offset=0):
    correlations = list()
    dates = list()
    with h5py.File(filename) as root:
        for trade_date in list(root)[start_day:end_day]:
            # print trade_date
            names = root[trade_date]["names"].value
            prices = root[trade_date][("prices")].value[:]
            epoch_times = root[trade_date]["dates"].value
            yields = np.diff(np.log(prices), axis=0)
            if offset > 0:
                y1 = yields[:-offset, 0]
                y2 = yields[offset:, 1]
            if offset < 0:
                offset = -offset
                y1 = yields[offset:, 0]
                y2 = yields[:-offset, 1]
            if offset == 0:
                y1 = yields[:, 0]
                y2 = yields[:, 1]
            correlations.append(np.corrcoef(y1, y2)[0,1])
    #        pyplot.plot(y1, y2, 'b.')
    #        pyplot.show()
    return correlations


if __name__ == "__main__":
    correlations = get_corr(offset=1)
    pyplot.plot(correlations)
    pyplot.show()
