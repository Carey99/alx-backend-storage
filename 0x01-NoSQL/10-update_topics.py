#!/usr/bin/env python3
"""
    Change school topics
"""


def update_topics(mongo_collection, name, topics):
    """Changes all topics based on name"""
    mongo_collection.update_many(
            {"name": name},
            {"$set:" {"topics": topics}}
    )
