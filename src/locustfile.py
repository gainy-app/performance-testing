import glob
import json
import logging
import os
import random
import string
import time
from locust import FastHttpUser, task, between
from common import generate_random_string, BaseHttpUser
from common.collections import open_collection, update_favorite_collections
from common.interests import update_profile_interests

class Default(BaseHttpUser):
    wait_time = between(1, 5)
    tasks = {
        open_collection: 100,
        update_favorite_collections: 10,
        update_profile_interests: 1
        }
