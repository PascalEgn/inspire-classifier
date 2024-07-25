import pandas as pd
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Q, Search
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LiteratureSearch(Search):
    connection_holdingpen = connections.create_connection(
        hosts=["https://os-inspire-legacy-os1.cern.ch/es"],
        timeout=30,
        http_auth=(os.environ["ES_USERNAME"], os.environ["ES_PASSWORD"]),
        verify_certs=False,
        use_ssl=True,
    )
    connection_inspirehep = connections.create_connection(
        hosts=["https://os-inspire-prod.cern.ch/es"],
        timeout=30,
        http_auth=(os.environ["ES_USERNAME"], os.environ["ES_PASSWORD"]),
        verify_certs=False,
        use_ssl=True,
    )

    def __init__(self, index, **kwargs):
        if index == "holdingpen-hep":
            connection = LiteratureSearch.connection_holdingpen
        else:
            connection = LiteratureSearch.connection_inspirehep
        super().__init__(
            using=kwargs.get("using", connection),
            index=index,
        )


df = pd.read_pickle("inspire_classifier_dataset_2021-10-01_2025-12-31.pkl")

df_rejected = df[df["label"] == 0]

df_rejected_sample = df_rejected.sample(frac=1, random_state=42).reset_index(drop=True)[:100]


# -----------------
search_next = LiteratureSearch("holdingpen-hep")
search_hep = LiteratureSearch("records-hep")

for index, row in df_rejected_sample.iterrows():
    document_id = row["id"]
    search_result = search_next.query(
        Q("match", _id=document_id) &
        Q("term", metadata__acquisition_source__source="arXiv")
    ).execute().hits
    if search_result:
        arxiv_id = search_result.hits[0]["_source"]["_extra_data"]["source_data"]["data"]["arxiv_eprints"][0]["value"]
        print(arxiv_id)
        #search_result_hep = search_hep.query(
        #    Q("terms", metadata__arxiv_eprints__contains=[{'value': arxiv_id}])
        #).execute().hits
        #print(search_result_hep)
#_extra_data --> approved

