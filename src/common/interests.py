import random
from common import RequestFailedException

def update_profile_interests(user):
    try:
        profile = user.get_profile()

        profile_interests = profile['profile_interests']

        if len(profile_interests):
            interest_to_remove = random.choice(profile_interests)
            response = user.make_graphql_request('DeleteProfileInterest', {
                'profileID': user.profile_id,
                'interestID': interest_to_remove['interest_id'],
            }, user.user_id)

        response = user.make_graphql_request('AppInterests', None, user.user_id)
        interests = response['data']['interests']
        interest_to_add = random.choice(interests)

        response = user.make_graphql_request('InsertProfileInterest', {
            'profileID': user.profile_id,
            'interestID': interest_to_add['id'],
        }, user.user_id)
        user.cached_recommended_collections = None
    except RequestFailedException as e:
        return
