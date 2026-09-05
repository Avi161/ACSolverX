"""Combinatorial audit of the supplied Fagan section 4.6.1 face data."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations

SOURCE_FACES = (
    (1, 9, -3, -8), (3, 11, 13, -7, -12, -10),
    (7, 8, 10, -4, -9, -14), (4, 12, -6, -11),
    (6, 14, 2, -8, -13), (2, 10, 5, -11, -9),
    (5, 13, 1, -14, -12), (1, 2, 3, 4, 5, 6, 7),
)
EDGE_ENDPOINTS = {
    **{edge: (edge, edge % 7 + 1) for edge in range(1, 8)},
    **{edge: (edge - 7, (edge - 6) % 7 + 1) for edge in range(8, 15)},
}


def oriented_endpoints(edge: int) -> tuple[int, int]:
    if not isinstance(edge, int) or edge == 0 or abs(edge) not in EDGE_ENDPOINTS:
        raise ValueError("unknown signed source edge")
    endpoints = EDGE_ENDPOINTS[abs(edge)]
    return endpoints if edge > 0 else endpoints[::-1]


@dataclass(frozen=True)
class SourceComplexAudit:
    faces: tuple[tuple[int, ...], ...]
    boundary_vertices: tuple[tuple[int, ...], ...]
    edge_occurrences: tuple[int, ...]
    vertex_links: tuple[tuple[tuple[int, int], ...], ...]
    euler_characteristic: int


def validate_source_complex(faces: tuple[tuple[int, ...], ...] = SOURCE_FACES) -> SourceComplexAudit:
    boundaries, links = [], defaultdict(list)
    occurrences = Counter()
    for face in faces:
        if not face:
            raise AssertionError("empty source face")
        endpoints = tuple(oriented_endpoints(edge) for edge in face)
        vertices = tuple(start for start, _ in endpoints)
        if any(endpoints[index][1] != endpoints[(index + 1) % len(face)][0]
               for index in range(len(face))):
            raise AssertionError("the signed source face path does not close")
        if len(set(vertices)) != len(vertices):
            raise AssertionError("the source face repeats a boundary vertex")
        boundaries.append(vertices)
        for index, edge in enumerate(face):
            occurrences[abs(edge)] += 1
            vertex = endpoints[index][1]
            corner = tuple(sorted((-edge, face[(index + 1) % len(face)])))
            links[vertex].append(corner)
    counts = tuple(occurrences[edge] for edge in range(1, 15))
    if counts != (3,) * 14:
        raise AssertionError("each source edge must have three face occurrences")
    pinned_links = []
    for vertex in range(1, 8):
        germs = tuple(sorted(signed for edge in range(1, 15) for signed in (edge, -edge)
                             if oriented_endpoints(signed)[0] == vertex))
        if len(germs) != 4 or Counter(links[vertex]) != Counter(combinations(germs, 2)):
            raise AssertionError("the source vertex link is not exactly K4")
        pinned_links.append(tuple(sorted(links[vertex])))
    euler = 7 - 14 + len(faces)
    if euler != 1:
        raise AssertionError("the source Euler count drifted")
    return SourceComplexAudit(tuple(faces), tuple(boundaries), counts, tuple(pinned_links), euler)


@dataclass(frozen=True)
class FaceSheetTransport:
    core_face: int
    starting_side_faces: tuple[int, int]
    ending_side_faces: tuple[int, int]
    traces: tuple[tuple[int, ...], tuple[int, ...]]
    monodromy: str


def trace_face_sheet_transport(audit: SourceComplexAudit, core_face: int) -> FaceSheetTransport:
    if not 0 <= core_face < len(audit.faces):
        raise ValueError("unknown core face")
    corners = {}
    incident = defaultdict(list)
    for face_index, face in enumerate(audit.faces):
        for index, edge in enumerate(face):
            vertex = oriented_endpoints(edge)[1]
            corners[(vertex, face_index)] = frozenset((-edge, face[(index + 1) % len(face)]))
            incident[abs(edge)].append(face_index)
    core = audit.faces[core_face]
    sides = tuple(index for index in incident[abs(core[0])] if index != core_face)
    if len(sides) != 2:
        raise AssertionError("the core edge does not have two side faces")
    traces = []
    for initial in sides:
        current, trace = initial, [initial]
        for index, incoming in enumerate(core):
            outgoing = core[(index + 1) % len(core)]
            vertex = oriented_endpoints(incoming)[1]
            side_corner = corners[(vertex, current)]
            if -incoming not in side_corner:
                raise AssertionError("the incoming sheet misses its corner germ")
            external = side_corner - {-incoming}
            if len(external) != 1 or outgoing in external:
                raise AssertionError("the sheet has no unique external germ")
            expected = frozenset((outgoing, next(iter(external))))
            candidates = [side for side in incident[abs(outgoing)] if side != core_face
                          and corners[(vertex, side)] == expected]
            if len(candidates) != 1:
                raise AssertionError("the outgoing sheet is not unique")
            current = candidates[0]
            trace.append(current)
        traces.append(tuple(trace))
    endings = tuple(trace[-1] for trace in traces)
    if set(endings) != set(sides):
        raise AssertionError("the sheet transport is not a permutation")
    return FaceSheetTransport(core_face, sides, endings, tuple(traces),
                              "identity" if endings == sides else "swap")


@dataclass(frozen=True)
class FaganFakeSurfaceDecision:
    audit: SourceComplexAudit
    sheet_transports: tuple[FaceSheetTransport, ...]
    contractibility_claimed: bool
    source_equivalence_checked: bool
    verdict: str


def decide_fagan_fake_surface() -> FaganFakeSurfaceDecision:
    audit = validate_source_complex()
    transports = tuple(trace_face_sheet_transport(audit, index) for index in range(len(SOURCE_FACES)))
    return FaganFakeSurfaceDecision(audit, transports, False, False,
                                    "FAGAN_SOURCE_COMBINATORICS_AND_SHEET_TRANSPORT_ONLY")


FIRST_TARGET_FACES = (
    (3, 15, 17, -16), (3, 11, 13, -16, 18, -12, -10),
    (-18, 10, -4, -14), (4, 12, -6, -11, 15),
    (6, 14, -15, 19, -13), (19, -16, 10, 5, -11),
    (5, 13, -17, -14, -12), (3, 19, -17, 4, 5, 6, -18),
)
SOURCE_TREE = (2, 4, 7, 8, 9, 11)
FIRST_TARGET_TREE = (4, 11, 15, 16, 18, 19)
EXPECTED_SOURCE_COLLAPSED = (
    (1, -3), (3, 13, -12, -10), (10, -14), (12, -6),
    (6, 14, -13), (10, 5), (5, 13, 1, -14, -12), (1, 3, 5, 6),
)


def integer_inverse(word: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-letter for letter in reversed(word))


def integer_reduce(word: tuple[int, ...]) -> tuple[int, ...]:
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


@dataclass(frozen=True)
class EndpointGraphAudit:
    endpoints: tuple[tuple[int, int, int], ...]
    vertex_count: int
    edge_count: int
    face_count: int
    edge_occurrences: tuple[tuple[int, int], ...]
    vertex_links: tuple[tuple[tuple[int, int], ...], ...]


def reconstruct_endpoint_graph(faces: tuple[tuple[int, ...], ...]) -> EndpointGraphAudit:
    edges = sorted({abs(letter) for face in faces for letter in face})
    if not edges or 0 in edges or any(not face for face in faces):
        raise AssertionError("endpoint reconstruction requires nonempty signed-edge faces")
    parent = {(edge, end): (edge, end) for edge in edges for end in (0, 1)}

    def find(endpoint):
        while parent[endpoint] != endpoint:
            parent[endpoint] = parent[parent[endpoint]]
            endpoint = parent[endpoint]
        return endpoint

    for face in faces:
        for index, incoming in enumerate(face):
            outgoing = face[(index + 1) % len(face)]
            head = (abs(incoming), 1 if incoming > 0 else 0)
            tail = (abs(outgoing), 0 if outgoing > 0 else 1)
            parent[find(head)] = find(tail)
    roots = sorted({find(endpoint) for endpoint in parent})
    vertex = {root: index for index, root in enumerate(roots)}
    endpoints = {edge: (vertex[find((edge, 0))], vertex[find((edge, 1))]) for edge in edges}
    counts = Counter(abs(letter) for face in faces for letter in face)
    if len(roots) != 7 or len(edges) != 14 or any(counts[edge] != 3 for edge in edges):
        raise AssertionError("the endpoint vertex, edge, or incidence counts drifted")
    links = defaultdict(list)
    for face in faces:
        for index, incoming in enumerate(face):
            head = endpoints[abs(incoming)][1 if incoming > 0 else 0]
            outgoing = face[(index + 1) % len(face)]
            links[head].append(tuple(sorted((-incoming, outgoing))))
    for at in range(7):
        germs = sorted(signed for edge in edges for signed in (edge, -edge)
                       if endpoints[edge][0 if signed > 0 else 1] == at)
        if len(germs) != 4 or Counter(links[at]) != Counter(combinations(germs, 2)):
            raise AssertionError("the reconstructed endpoint link is not exactly K4")
    reached = {0}
    for _ in range(7):
        reached |= {other for ends in endpoints.values() for at, other in (ends, ends[::-1]) if at in reached}
    if len(reached) != 7:
        raise AssertionError("the reconstructed endpoint graph is disconnected")
    return EndpointGraphAudit(tuple((edge, *endpoints[edge]) for edge in edges), 7, 14, len(faces),
                              tuple(sorted(counts.items())), tuple(tuple(sorted(links[at])) for at in range(7)))


def validate_endpoint_tree(audit: EndpointGraphAudit, tree: tuple[int, ...]) -> None:
    endpoints = {edge: (start, end) for edge, start, end in audit.endpoints}
    if len(tree) != 6 or len(set(tree)) != 6 or not set(tree) <= endpoints.keys():
        raise AssertionError("the endpoint tree must contain six distinct source edges")
    parent = list(range(audit.vertex_count))
    for edge in tree:
        start, end = endpoints[edge]
        while parent[start] != start:
            start = parent[start]
        while parent[end] != end:
            end = parent[end]
        if start == end:
            raise AssertionError("the endpoint tree has a cycle")
        parent[start] = end
    roots = set()
    for vertex in range(audit.vertex_count):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        roots.add(vertex)
    if len(roots) != 1:
        raise AssertionError("the endpoint tree is not spanning")


@dataclass(frozen=True)
class FirstFourgonEndpointDecision:
    source_audit: EndpointGraphAudit
    target_audit: EndpointGraphAudit
    source_tree: tuple[int, ...]
    target_tree: tuple[int, ...]
    source_collapsed: tuple[tuple[int, ...], ...]
    target_collapsed: tuple[tuple[int, ...], ...]
    defect: tuple[int, ...]
    product: tuple[int, ...]
    geometric_local_rewrite_certified: bool
    complexity_reduction_claimed: bool
    verdict: str


def decide_first_fourgon_endpoint() -> FirstFourgonEndpointDecision:
    source = reconstruct_endpoint_graph(SOURCE_FACES)
    target = reconstruct_endpoint_graph(FIRST_TARGET_FACES)
    validate_endpoint_tree(source, SOURCE_TREE)
    validate_endpoint_tree(target, FIRST_TARGET_TREE)
    source_rows = tuple(integer_reduce(tuple(letter for letter in face if abs(letter) not in SOURCE_TREE))
                        for face in SOURCE_FACES)
    target_rows = tuple(integer_reduce(tuple(-1 if letter == 17 else 1 if letter == -17 else letter
                                             for letter in face if abs(letter) not in FIRST_TARGET_TREE))
                        for face in FIRST_TARGET_FACES)
    expected_target = (integer_inverse(EXPECTED_SOURCE_COLLAPSED[0]),) + EXPECTED_SOURCE_COLLAPSED[1:-1] + ((3, 1, 5, 6),)
    if source_rows != EXPECTED_SOURCE_COLLAPSED or target_rows != expected_target:
        raise AssertionError("the first-fourgon collapsed presentation drifted")
    defect = integer_reduce(source_rows[-1] + integer_inverse(target_rows[-1]))
    r_row = source_rows[0]
    product = integer_reduce(r_row + (3,) + integer_inverse(r_row) + (-3,))
    if defect != (1, 3, -1, -3) or defect != product:
        raise AssertionError("the first-fourgon retained-row identity drifted")
    return FirstFourgonEndpointDecision(source, target, SOURCE_TREE, FIRST_TARGET_TREE,
                                        source_rows, target_rows, defect, product, False, False,
                                        "FIRST_FOURGON_ENDPOINT_PRESENTATION_EQUIVALENCE_ONLY")


@dataclass(frozen=True)
class SourceToAK3Decision:
    tree: tuple[int, ...]
    collapsed_rows: tuple[tuple[int, ...], ...]
    defining_eliminations: tuple[tuple[int, int, tuple[int, ...]], ...]
    stages: tuple[tuple[str, tuple[tuple[int, tuple[int, ...]], ...]], ...]
    correction_donor: tuple[int, ...]
    correction_before: tuple[int, ...]
    correction_after: tuple[int, ...]
    correction_defect: tuple[int, ...]
    correction_product: tuple[int, ...]
    final_source_rows: tuple[tuple[int, ...], ...]
    target_rows: tuple[tuple[int, ...], ...]
    trivialization_claimed: bool
    verdict: str


def decide_source_to_ak3() -> SourceToAK3Decision:
    tree = (2, 3, 5, 7, 10, 13)
    validate_endpoint_tree(reconstruct_endpoint_graph(SOURCE_FACES), tree)
    collapsed = tuple(integer_reduce(tuple(letter for letter in face if abs(letter) not in tree))
                      for face in SOURCE_FACES)
    if collapsed != ((1, 9, -8), (11, -12), (8, -4, -9, -14), (4, 12, -6, -11),
                     (6, 14, -8), (-11, -9), (1, -14, -12), (1, 4, 6)):
        raise AssertionError("the source-to-AK3 tree collapse drifted")
    rows = dict(enumerate(collapsed, 1))
    stages = [("tree_collapse", tuple(rows.items()))]
    eliminations = ((2, 11, (12,)), (6, 12, (-9,)), (3, 4, (-9, -14, 8)),
                    (4, 6, (-14, 1)), (5, 8, (-14, 1, 14)), (7, 9, (14, -1)))

    def eliminate(row_index, generator, image):
        defining = rows[row_index]
        if sum(abs(letter) == generator for letter in defining) != 1 or generator in map(abs, image):
            raise AssertionError("the prescribed defining row is not uniquely solvable")
        updated = {}
        for index, word in rows.items():
            letters = tuple(value for letter in word for value in (
                image if letter == generator else integer_inverse(image) if letter == -generator else (letter,)
            ))
            updated[index] = integer_reduce(letters)
        if updated[row_index]:
            raise AssertionError("the source-to-AK3 defining row did not vanish")
        del updated[row_index]
        if any(abs(letter) == generator for word in updated.values() for letter in word):
            raise AssertionError("an eliminated source generator remains")
        rows.clear()
        rows.update(updated)
        stages.append((f"delete_row_{row_index}_generator_{generator}", tuple(rows.items())))

    for elimination in eliminations[:3]:
        eliminate(*elimination)
    before = integer_reduce((9,) + rows[4] + (-9,))
    donor = rows[1]
    after = (-14, 1, -6)
    if before != (-14, 8, -9, -6) or donor != (1, 9, -8):
        raise AssertionError("the source-to-AK3 correction inputs drifted")
    defect = integer_reduce(before + integer_inverse(after))
    product = integer_reduce((-14,) + integer_inverse(donor) + (14,))
    if defect != product:
        raise AssertionError("the source-to-AK3 retained-row correction drifted")
    rows[4] = before
    stages.append(("conjugate_row_4_by_9", tuple(rows.items())))
    rows[4] = after
    stages.append(("correct_row_4_using_row_1", tuple(rows.items())))
    for elimination in eliminations[3:]:
        eliminate(*elimination)
    final_rows = (rows[1], rows[8])
    if final_rows != ((1, 14, -1, -14, -1, 14), (1, 1, -14, -14, -14, 1, 1)):
        raise AssertionError("the final source-to-AK3 rows drifted")
    rename = {14: 1, -14: -1, 1: 2, -1: -2}
    first, second = tuple(tuple(rename[letter] for letter in word) for word in final_rows)
    target = (integer_reduce((1,) + first + (-1,)),
              integer_reduce((2, 2) + integer_inverse(second) + (-2, -2)))
    if target != ((1, 2, 1, -2, -1, -2), (1, 1, 1, -2, -2, -2, -2)):
        raise AssertionError("the canonical AK3 target rows drifted")
    return SourceToAK3Decision(tree, collapsed, eliminations, tuple(stages), donor, before, after,
                               defect, product, final_rows, target, False,
                               "SOURCE_TO_AK3_STABLE_EQUIVALENCE_ONLY")
