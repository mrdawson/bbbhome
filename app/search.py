from flask import current_app
from pprint import pprint


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        attrs = field.split(".")
        payload[field] = getattr(model, attrs[0])
        if len(attrs) > 1:
            for attr in attrs[1:]:
                payload[field] = (
                    getattr(payload[field][0], attr)
                    if len(payload[field]) > 0
                    else None
                )
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                    "fields": ["title^5", "author_sort^2", "tags^1000", "series^5", "*"],
                }
            },
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]["value"]
