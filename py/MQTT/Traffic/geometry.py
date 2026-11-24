"""geoemtria da cidade resenha"""
from dataclasses import dataclass
from typing import List, Tuple

point = Tuple[float, float]

@dataclass(frozen=True)
class Street:
    """linhas retas
    horizontal: embaixo esqurda e embaixo direita
    vertical: mesma coisa porem em cima
    largura 2 * tamanho ( são duas faixas né)"""
    orientation: str # "H" ou "V"
    p1: point 
    p2: point 
    width: float
    
    @property
    def corners(self):
        if self.orientation == "H":
            (x0,y0), (x1, _) = self.p1, self.p2
            return (x0,y0), (x1,y0), (x1, y0 + self.width), (x0, y0 + self.width)
        (x0, y_top), (_, y_bot) = self.p1, self.p2
        return (x0, y_bot), (x0 + self.width, y_bot), (x0 + self.width, y_top), (x0, y_top)
    @property
    def centerline(self) -> float:
        """coordenadas das ruas (cenrtro)"""
        if self.orientation == "H":
            return self.p1[1] + self.width / 2
        return self.p1[0] + self.width / 2
 
    def contains(self, p: point) -> bool:
        (x0, y0), _, (x1, y1), _ = self.corners
        return x0 <= p[0] <= x1 and y0 <= p[1] <= y1
 
 
class City:
    def __init__(self, width, height, lane_width, horizontals: List[Street], verticals: List[Street]):
        self.width, self.height = width, height
        self.lane_width = lane_width
        self.horizontals = horizontals
        self.verticals = verticals
 
    @classmethod
    def from_config(cls, cfg: dict) -> "City":
        w = 2 * cfg["lane_width"]
        hs = [Street("H", tuple(s["bottom_left"]), tuple(s["bottom_right"]), w)
              for s in cfg["horizontal_streets"]]
        vs = [Street("V", tuple(s["top_left"]), tuple(s["bottom_left"]), w)
              for s in cfg["vertical_streets"]]
        return cls(cfg["city"]["width"], cfg["city"]["height"], cfg["lane_width"], hs, vs)
 
    def intersections(self) -> List[Tuple[int, int, point]]:
        """(h_index, v_index, center) pra cada cruzamento."""
        return [(i, j, (v.centerline, h.centerline))
                for i, h in enumerate(self.horizontals)
                for j, v in enumerate(self.verticals)]
 
    def street_at(self, p: point):
        return [s for s in self.horizontals + self.verticals if s.contains(p)]
 