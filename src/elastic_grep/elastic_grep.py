#!/bin/env python3
import sys
import datetime
from elasticsearch7 import Elasticsearch

from typing import Dict, Any, List

# TODO: put this in a config file
elastic_servers = [
    {'host': 'localhost', 'port': 9200},
]


search_index: str = "filebeat*"


def run_query(and_operator: bool, verbose: bool, words: List[str]) -> List[Dict[str, Any]]:
    operator: str = "AND" if and_operator else "OR"
    es = Elasticsearch(elastic_servers)
    hours = 24*2
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=hours)
    query_old = {
        "match": {
            "message": {
                "query": " ".join(words),
                "analyzer": "pattern",
                "auto_generate_synonyms_phrase_query": False,
                "operator": operator
            }
        }
    }
    query = {
        "bool": {
            "must": [
                {
                    "range": {
                        "@timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat(),
                            "format": "strict_date_optional_time"
                        }
                    }
                },
                {
                    "simple_query_string": {
                        "query": " ".join(words)
                    }
                }
            ]
        }
    }
    index = search_index
    if verbose:
        print("index=", index, "query=", query)
    res = es.search(index=index, query=query, size=1000, request_timeout=100)
    matches = res['hits']['hits']
    return matches


def print_results(results: List[Dict[str, Any]]) -> None:
    for result in results:
        core = result["_source"]
        host = core["host"]["name"]
        path = core["log"]["file"]["path"]
        print(f'{host}: {path}: {core["message"]}')


def print_help() -> None:
    """Print the help text"""
    print("Search the logfiles in elasticsearch for words in log messages")
    print()
    print("Usage: elastic_grep [<option>...<option>] <word>...<word>")
    print("Where <option> is one of:")
    print("-a\t\tSearch for elasticsearch entries that match ALL words (default: ANY word)")
    print("-e\t\tAll subsequent words are patterns, not patterns")
    print("-h\t\tShow this help text")
    print("--host <host>\tSpecify the hostname or IP address of the elasticsearch server to talk to (default: 'localhost'")
    print("--index <index>\tSpecify the index to search (default: 'filebeat*'")
    print("--port <port>\tSpecify the port of the elasticsearch server to talk to (default: 9200)")
    print("-v\t\tIncrease the verbosity of the output")
    print("At least one word should be given. If more than one word is given, all entries")
    print("that contain at least one of these words somewhere in the message are shown.")
    print("With the -a option only entries are shown that contain ALL words somewhere in")
    print("the message.")


def report_commandline_error(msg: str) -> None:
    print("Bad command line: " + msg)
    print_help()
    sys.exit(1)


def main():
    query_words = []
    recognize_options = True
    verbose = False
    and_operator = False
    for arg in sys.argv[1:]:
        if recognize_options:
            if arg == '-h':
                print_help()
                sys.exit(0)
            elif arg == '-a':
                and_operator = True
            elif arg == '-e':
                recognize_options = False
            elif arg == '-v':
                verbose = True
            else:
                if arg[0] == '-':
                    report_commandline_error(f"Unknown option '{arg}'")
                else:
                    query_words.append(arg)
        else:
            # Anything else is a query pattern
            query_words.append(arg)
    if len(query_words) == 0:
        report_commandline_error("There is no pattern to search for")
    matches: List[Dict[str, Any]] = run_query(and_operator, verbose, query_words)
    print_results(matches)

# TODO: allow time interval to be specified
# TODO: allow indices to be specified
# TODO: allow filtering on host
# TODO: allow filtering on log file name
# TODO: document query behavior properly


if __name__ == "__main__":
    main()
