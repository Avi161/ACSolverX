"""Keep every row's left collection frame, including more expensive aliases."""
import exchange_collect


def probe(words, remaining):
    return exchange_collect.probe(words, remaining, direction='left')
