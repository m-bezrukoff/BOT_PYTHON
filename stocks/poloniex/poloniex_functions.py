def init_exchange_balaces(shared, market):
    d = shared.dict()
    for coin in market:
        d[coin] = market[coin]
    return d


def update_ticker(data):
    """
    Обновление тикера в pairs через rest api
    """
    return {
        'rate': float(data['last']),
        'ask_rate': float(data['lowestAsk']),
        'bid_rate': float(data['highestBid']),
        'day_change': round(float(data['percentChange']) * 100, 2),
        'day_volume_rated': float(data['baseVolume']),
        'day_volume_cur': float(data['quoteVolume']),
        'is_frozen': int(data['isFrozen']),
        'day_high_rate': float(data['high24hr']),
        'day_low_rate': float(data['low24hr']),
        'is_updated_by_ticker': True
    }
