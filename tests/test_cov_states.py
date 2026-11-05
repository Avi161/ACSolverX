"""acx.cov.states: every CoV state of a state, the function the CoV-gate search calls at a gate opening."""
from itertools import combinations

from acx.core.words import Presentation
from acx.cov import apply_steps, iter_images
from acx.cov.images import class_key as reference_key
from acx.cov.states import class_key, cov_states

AK3 = Presentation.parse("xyxYXY", "xxxYYYY")
PLANTED = Presentation.parse("XyXXy", "yyXXyXX")          # has the image <x, y | xYX, xYxYX> (tests/test_cov.py)
PLANTED_IMAGE = Presentation.parse("xYX", "xYxYX")
ROWS = [AK3, PLANTED, Presentation.parse("yyXYx", "Yx"), Presentation.parse("YYXyx", "YYxxxYXX"),   # MS640 row 100
        Presentation.parse("YYYYYYYXyyyyyyx", "YXXyx")]                                                   # MS640 row 590


def test_same_images_as_the_family_in_the_same_order():
    for pres in ROWS:
        ours = [(i.pres.rels, i.steps) for i in cov_states(*pres.rels)]
        family = [(i.pres.rels, i.steps) for i in iter_images(pres, None, "suballpxyb8")]
        assert ours == family and ours


def test_class_key_identifies_exactly_what_the_reference_identifies():
    images = [i.pres for pres in ROWS for i in iter_images(pres, None, "suballpxyb8")] + ROWS
    for p, q in combinations(images, 2):
        assert (class_key(*p.rels) == class_key(*q.rels)) == (reference_key(p) == reference_key(q))


def test_signed_relabellings_rotations_and_order_are_one_class():
    a, b = Presentation.parse("xyxYXY", "xxxYYYY").rels
    for c, d in [(b, a), (a[2:] + a[:2], b), (tuple(-g for g in a), tuple(-g for g in b)),
                 (tuple(3 - g if g > 0 else -3 - g for g in a), tuple(3 - g if g > 0 else -3 - g for g in b))]:
        assert class_key(c, d) == class_key(a, b)


def test_every_image_replays_and_the_planted_one_is_found():
    for pres in ROWS:
        for image in cov_states(*pres.rels):
            assert class_key(*apply_steps(pres, image.steps).rels) == class_key(*image.pres.rels)
    keys = {class_key(*i.pres.rels) for i in cov_states(*PLANTED.rels)}
    assert class_key(*PLANTED_IMAGE.rels) in keys and class_key(*PLANTED.rels) not in keys
