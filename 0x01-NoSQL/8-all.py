#!/usr/bin/env python3
"""
    Function that lists all doc in a collection
    returns an empty list if no document in collection
"""
from typing import List
import pymongo


def list_all(mongo_collection) -> List:
    """ list_all - lists all documents in a collection
    Args:
        mongo_collection: pymongo collection object
    Returns: list of documents or empty list
    """
    docs = []
    for doc in mongo_collection.find():
        docs.append(doc)
    return docs
