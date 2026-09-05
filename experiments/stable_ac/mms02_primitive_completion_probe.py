"""One bounded stage-three free-word completion probe."""

from collections import deque
import json

ALPHABET = "abAB"
LIMIT = 1000
RAW_B = "XyyXYXyxYYxy"
DELTA = "bAbABaBB"
PHI_B = "bbAbaB"


def inverse(word):
    return word[::-1].swapcase()


def reduce_word(word):
    stack = []
    for letter in word:
        if stack and stack[-1].swapcase() == letter:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def phi(word, b_image=PHI_B):
    images = {"a": "b", "A": "B", "b": b_image, "B": inverse(b_image)}
    return reduce_word("".join(images[letter] for letter in word))


def word_power(word, exponent):
    return reduce_word((word if exponent >= 0 else inverse(word)) * abs(exponent))


def stage_three_height_scan(word, b_image=PHI_B):
    height, pieces = 0, []
    for letter in word:
        if letter in "xX":
            height += 1 if letter == "x" else -1
        elif letter in "yY":
            if height + 3 < 0:
                raise AssertionError("the stage-three scan has a negative iterate")
            image = "a"
            for _ in range(height + 3):
                image = phi(image, b_image)
            pieces.append(image if letter == "y" else inverse(image))
        else:
            raise ValueError("unknown height-scan letter")
    if height != 0:
        raise AssertionError("the stage-three input has nonzero final height")
    return reduce_word("".join(pieces))


def candidates():
    queue, words = deque([""]), []
    while len(words) < LIMIT:
        word = queue.popleft()
        words.append(word)
        queue.extend(word + letter for letter in ALPHABET
                     if not word or word[-1].swapcase() != letter)
    return words


def abelianization(word):
    return (word.count("a") - word.count("A"), word.count("b") - word.count("B"))


def parameters_and_controls():
    d_word = phi("b")
    u_word = reduce_word(d_word + inverse(DELTA))
    v_word = phi(phi(phi("a")))
    raw_stage = stage_three_height_scan(RAW_B + "x")
    if raw_stage != u_word or abelianization(v_word) != (0, 4):
        raise AssertionError("the stage-three pinned completion inputs drifted")
    controls = []
    for exponent in (2, 0, -2):
        control_u = reduce_word("b" + word_power(d_word, exponent) + "A")
        w_word = reduce_word(inverse(phi("b")) + phi(control_u) + "b")
        target = word_power(v_word, exponent)
        if w_word != target:
            raise AssertionError("a prescribed completion positive control failed")
        controls.append({"m": exponent, "N": "b", "u": control_u, "W": w_word, "target": target, "passed": True})
    wrong_raw_stage = stage_three_height_scan(RAW_B + "x", "bbAba")
    if wrong_raw_stage == u_word:
        raise AssertionError("the truncated monodromy was accepted by the pinned source check")
    return d_word, u_word, v_word, raw_stage, controls, wrong_raw_stage


def data():
    d_word, u_word, v_word, raw_stage, controls, wrong_raw_stage = parameters_and_controls()
    tested = candidates()
    if len(tested) != LIMIT or len(set(tested)) != LIMIT or any(reduce_word(word) != word for word in tested):
        raise AssertionError("the finite reduced-word BFS prefix drifted")
    phi_u = phi(u_word)
    hits = []
    for n_word in tested:
        w_word = reduce_word(inverse(phi(n_word)) + phi_u + n_word)
        a_exponent, b_exponent = abelianization(w_word)
        if a_exponent or b_exponent % 4:
            continue
        exponent = b_exponent // 4
        if w_word == word_power(v_word, exponent):
            hits.append({"N": n_word, "m": exponent, "W": w_word})
    return {"parameters": {"alphabet": ALPHABET, "limit": LIMIT, "stage": 3,
                           "raw_B": RAW_B, "phi": {"a": "b", "b": PHI_B}, "delta": DELTA},
            "d": d_word, "u": u_word, "V": v_word, "V_abelianization": [0, 4],
            "raw_Bx_stage_three": raw_stage, "tested_N": tested, "hits": hits,
            "controls": controls,
            "corrupted_phi_control": {"b_image": "bbAba", "raw_stage": wrong_raw_stage, "rejected": True},
            "status": "bounded_stage_three_prefix_only"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
