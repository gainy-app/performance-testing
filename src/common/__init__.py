import glob
import json
import os
import random
import string
import time
from locust import FastHttpUser, task, between
import logging

logging.basicConfig()

HASURA_ADMIN_SECRET = os.getenv('HASURA_ADMIN_SECRET')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)

def generate_random_string(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

class BaseHttpUser(FastHttpUser):
    abstract = True
    cached_recommended_collections = None

    def __init__(self, environment):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)
        super().__init__(environment)

        self.queries = {}
        for i in glob.glob(os.path.join(os.path.dirname(__file__), '../queries/*.graphql')):
            with open(i, 'r') as f:
                query = f.read()
            (query_name, _) = os.path.splitext(os.path.basename(i))
            self.queries[query_name] = query


    def get_recommended_collections(self):
        if self.cached_recommended_collections is None:
            response = self.make_graphql_request('FetchRecommendedCollections', {
                'profileId': self.profile_id
            }, self.user_id)
            self.cached_recommended_collections = response['data']['get_recommended_collections']

        return self.cached_recommended_collections

    def get_profile(self):
        return self.make_graphql_request('GetProfile', {
            'profileID': self.profile_id
        }, self.user_id)['data']['app_profiles'][0]

    def on_start(self):
        self.user_id = generate_random_string(28, string.ascii_letters + string.digits)
        self.user_email = 'test-%s@gainy.app' % (generate_random_string(28, string.ascii_letters + string.digits))

        response = self.make_graphql_request('CreateProfile', {
            'avatarURL': '',
            'email': self.user_email,
            'firstName': generate_random_string(8, string.ascii_letters),
            'gender': 0,
            'lastName': generate_random_string(8, string.ascii_letters),
            'userID': self.user_id,
            'legalAddress': generate_random_string(28, string.ascii_letters + string.digits + ' '),
            'interests': [
                {
                    'interest_id': 3
                }
            ],
            'averageMarketReturn': random.choice([6, 15, 25, 50]),
            'damageOfFailure': random.random(),
            'marketLoss20': random.random(),
            'marketLoss40': random.random(),
            'investemtHorizon': random.random(),
            'riskLevel': random.random(),
            'stockMarketRiskLevel': random.choice(['very_risky', 'somewhat_risky', 'neutral', 'somewhat_safe', 'very_safe']),
            'tradingExperience': random.choice(['never_tried', 'very_little', 'companies_i_believe_in', 'etfs_and_safe_stocks', 'advanced', 'daily_trader', 'investment_funds', 'professional', 'dont_trade_after_bad_experience']),
            'unexpectedPurchaseSource': random.choice(['checking_savings', 'stock_investments', 'credit_card', 'other_loans']),

        }, None)

        self.profile_id = response['data']['insert_app_profiles']['returning'][0]['id']

    def on_stop(self):
        self.make_graphql_request('DeleteProfile', {
            'profileId': self.profile_id
        })


    def make_graphql_request(self, query_name, variables=None, user_id=None):
        postData = {
            "query": self.queries[query_name],
            "variables": variables,
        }

        headers = {
            "x-hasura-admin-secret": HASURA_ADMIN_SECRET,
            "content-type": "application/json",
        }

        if user_id is not None:
            headers["x-hasura-user-id"] = user_id
            headers["x-hasura-role"] = "user"

        return self.make_request('POST', "/v1/graphql", postData, headers, request_name=query_name)

    def make_request(self, method, url, post_data=None, headers={}, request_name=None):
        self.logger.info("%s %s %s %s" % (method, url, request_name, json.dumps(post_data['variables'])))
        with self.client.request(method, url, json=post_data, headers=headers, name=request_name, catch_response=True) as response:
            try:
                response_data = response.json()
            except:
                response_data = None

            self.logger.info("Status Code: %s " % response.status_code)

            if response_data is None or 'data' not in response_data or not response.status_code or response.status_code < 200 or response.status_code > 299:
                if response_data is not None:
                    self.logger.error("Response: %s" % response_data)

                if response_data is not None and 'errors' in response_data:
                    messages = [i['message'] for i in response_data['errors']]
                    error_message = "Failed: %s" % (json.dumps(messages))
                else:
                    error_message = "Failed with status code: %s", response.status_code

                self.logger.error(error_message)
                response.failure(error_message)
                raise RequestFailedException(error_message)

        self.logger.info("HTTP request successfully executed")

        return response_data

class RequestFailedException(Exception):
    pass