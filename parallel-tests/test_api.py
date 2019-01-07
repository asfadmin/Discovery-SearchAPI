import pytest
import requests


with open('queries.txt', 'r') as f:
    query_txt = f.read()

queries = [
    q for q in query_txt.split('\n')
    if q and q[0] != '#' and '\n' not in q
]


@pytest.mark.parametrize("query", queries)
def test_api(query):
    api_url = 'http://localhost:5000/services/search/param'

    resp = requests.get("{}?{}".format(
        api_url, query
    ))

    assert resp.status_code == 200 and resp.text
