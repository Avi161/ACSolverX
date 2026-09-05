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
