from collections import namedtuple
from config import TARGET_EMAILS_1, TARGET_EMAILS_2

QUERY_STRING_1 = {
    "utf8": "✓",
    "property_type_id": "1",
    "district": "28,71",
    "page": 1,
    "rooms_radio": "custom",
    "rooms_from": 3,
    "rooms_to": 10,
}


QUERY_STRING_2_behinderfreunchlich = {
    "utf8": "✓",
    "property_type_id": "1",
    "district": "33,28,71,64,4-65",
    "page": 1,
    "rooms_radio": "custom",
    "rooms_from": 3,
    "rooms_to": 10,
    "features[]": [11],
}
QUERY_STRING_3_aufzug = {
    "utf8": "✓",
    "property_type_id": "1",
    "district": "33,28,71,64,4-65",
    "page": 1,
    "rooms_radio": "custom",
    "rooms_from": 3,
    "rooms_to": 10,
    "features[]": [2],
}
QUERY_STRING_4_rollstuhl = {
    "utf8": "✓",
    "property_type_id": "1",
    "district": "33,28,71,64,4-65",
    "page": 1,
    "rooms_radio": "custom",
    "rooms_from": 3,
    "rooms_to": 10,
    "features[]": [12],
}

Query = namedtuple("Query", ["name", "receiver", "queries_string"])

query_elise = Query("elise", TARGET_EMAILS_1, [QUERY_STRING_1])
query_christin = Query(
    "christin",
    TARGET_EMAILS_2,
    [
        QUERY_STRING_2_behinderfreunchlich,
        QUERY_STRING_3_aufzug,
        QUERY_STRING_4_rollstuhl,
    ],
)
