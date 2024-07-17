#!/usr/bin/env python3
"""
    Inserts a new doc in a colection based on kwargs
"""


def insert_school(mongo_collection, **kwargs):
    """Inserts a new doc"""
    added = mongo_collection.insert_one(kwargs)
    return added.inserted_id
