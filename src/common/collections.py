import random
import time
from common import RequestFailedException

METRICS = [
    "profit_margin",
    "avg_volume_10d",
    "short_percent_outstanding",
    "shares_outstanding",
    "avg_volume_90d",
    "shares_float",
    "short_ratio",
    "beta",
    "absolute_historical_volatility_adjusted_current",
    "relative_historical_volatility_adjusted_current",
    "absolute_historical_volatility_adjusted_min_1y",
    "absolute_historical_volatility_adjusted_max_1y",
    "relative_historical_volatility_adjusted_min_1y",
    "relative_historical_volatility_adjusted_max_1y",
    "implied_volatility",
    "revenue_growth_yoy",
    "revenue_growth_fwd",
    "ebitda_growth_yoy",
    "eps_growth_yoy",
    "eps_growth_fwd",
    "address_city",
    "address_state",
    "address_county",
    "address_full",
    "exchange_name",
    "market_capitalization",
    "enterprise_value_to_sales",
    "price_to_earnings_ttm",
    "price_to_sales_ttm",
    "price_to_book_value",
    "enterprise_value_to_ebitda",
    "price_change_1m",
    "price_change_3m",
    "price_change_1y",
    "dividend_yield",
    "dividends_per_share",
    "dividend_payout_ratio",
    "years_of_consecutive_dividend_growth",
    "dividend_frequency",
    "eps_actual",
    "eps_estimate",
    "beaten_quarterly_eps_estimation_count_ttm",
    "eps_surprise",
    "revenue_estimate_avg_0y",
    "revenue_actual",
    "revenue_ttm",
    "revenue_per_share_ttm",
    "net_income",
    "roi",
    "asset_cash_and_equivalents",
    "roa",
    "total_assets",
    "ebitda",
    "net_debt",
]

def open_collection(user):
    try:
        recommended_collections = user.get_recommended_collections()
        if not len(recommended_collections):
            return

        time.sleep(random.random() * 2)

        response = user.make_graphql_request('FetchSelectedCollections', {
            'ids': [i['id'] for i in recommended_collections]
        }, user.user_id)

        collection = random.choice(response['data']['collections'])

        if random.random() > 0.5:
            response = user.make_graphql_request('GetTickersForCollection', {
                'collectionId': collection['id'],
                'offset': 0,
                'orderBy': {"ticker": {"ticker_metrics": {random.choice(METRICS): random.choice(["asc", "desc"])}}}
            }, user.user_id)
        else:
            response = user.make_graphql_request('GetTickersByMSForCollection', {
                'collectionId': collection['id'],
                'offset': 0,
                'orderBy': random.choice(["asc", "desc"])
            }, user.user_id)

        ticker = random.choice(response['data']['ticker_collections'])['ticker']

        user.make_graphql_request('TickerDetails', {
            'symbol': ticker['symbol']
        }, user.user_id)

        for period in ['1d', '1w', '1m', '3m', '1y', '5y', 'all']:
            user.make_graphql_request('Charts', {
                'period': period,
                'symbol': ticker['symbol'],
            }, user.user_id)

            time.sleep(random.random() * 2)
    except RequestFailedException as e:
        return


def update_favorite_collections(user):
    try:
        response = user.make_graphql_request('GetProfile', {
            'profileID': user.profile_id
        }, user.user_id)

        favorite_collections = response['data']['app_profiles'][0]['profile_favorite_collections']

        if len(favorite_collections):
            collection_to_remove = random.choice(favorite_collections)
            response = user.make_graphql_request('DeleteFavouriteCollections', {
                'profileID': user.profile_id,
                'collectionID': collection_to_remove['collection_id'],
            }, user.user_id)

        recommended_collections = user.get_recommended_collections()
        if len(recommended_collections):
            collection_to_add = random.choice(recommended_collections)
            response = user.make_graphql_request('InsertFavouriteCollection', {
                'profileID': user.profile_id,
                'collectionID': collection_to_add['id'],
            }, user.user_id)
    except RequestFailedException as e:
        return