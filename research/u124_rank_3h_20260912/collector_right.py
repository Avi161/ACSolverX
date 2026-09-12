"""Keep every row's right collection frame, including more expensive aliases."""
import exchange_collect


def probe(words, remaining):
    return exchange_collect.probe(words, remaining, direction='right')
