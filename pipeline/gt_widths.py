"""Turn official sidewalk polygons into an answer key of widths along each sidewalk centreline.

For every sidewalk polygon: rasterise at 5 cm, distance transform, skeletonise.
Each skeleton pixel gives a width = 2 x distance to the nearest edge. Pixels are thinned to
one point every ~2 m. Points within 1.5 m of a polygon end/corner are dropped (widths blow up there).

Usage (AI environment):
    python gt_widths.py ../benchmark_dc/ground_truth/dc_sidewalks_2023.geojson ../benchmark_dc/ground_truth/gt_width_points.geojson
"""
import sys
import numpy as np
import geopandas as gpd
from scipy import ndimage
from shapely.geometry import Point
from skimage.morphology import skeletonize
from skimage.draw import polygon as draw_polygon

RES = 0.05      # metres per pixel
SPACING = 2.0   # keep one width sample per ~2 m of centreline
MIN_WIDTH = 0.6
MAX_WIDTH = 12.0  # plazas / forecourts are not sidewalks for scoring


def rasterise(poly, res):
    minx, miny, maxx, maxy = poly.bounds
    w = int(np.ceil((maxx - minx) / res)) + 4
    h = int(np.ceil((maxy - miny) / res)) + 4
    m = np.zeros((h, w), bool)
    x0, y0 = minx - 2 * res, maxy + 2 * res

    def fill(ring, val):
        xs, ys = np.asarray(ring.coords).T
        rr, cc = draw_polygon((y0 - ys) / res, (xs - x0) / res, m.shape)
        m[rr, cc] = val

    fill(poly.exterior, True)
    for hole in poly.interiors:
        fill(hole, False)
    return m, x0, y0


def widths_for(poly):
    m, x0, y0 = rasterise(poly, RES)
    if m.sum() < 50:
        return []
    dist = ndimage.distance_transform_edt(m) * RES
    sk = skeletonize(m)
    rr, cc = np.nonzero(sk)
    if len(rr) == 0:
        return []
    w = 2 * dist[rr, cc]
    xs, ys = x0 + cc * RES, y0 - rr * RES
    # thin to ~SPACING by grid snapping
    keep = {}
    for x, y, wi in zip(xs, ys, w):
        key = (int(x // SPACING), int(y // SPACING))
        if key not in keep or wi < keep[key][2]:
            keep[key] = (x, y, wi)
    boundary = poly.boundary
    out = []
    for x, y, wi in keep.values():
        if not (MIN_WIDTH <= wi <= MAX_WIDTH):
            continue
        p = Point(x, y)
        # skip skeleton branches that run into corners (distance to edge << half width means a spur)
        if boundary.distance(p) < 0.35 * wi:
            continue
        out.append((p, round(float(wi), 3)))
    return out


def main(src, dst):
    sw = gpd.read_file(src)
    utm = sw.estimate_utm_crs()
    sw = sw.to_crs(utm).explode(index_parts=False)
    rows = []
    for i, geom in enumerate(sw.geometry):
        if geom is None or geom.is_empty:
            continue
        for p, w in widths_for(geom.buffer(0)):
            rows.append({"sidewalk_idx": i, "gt_width_m": w, "geometry": p})
        if i % 100 == 0:
            print(f"\r{i}/{len(sw)} polygons, {len(rows)} width points", end="")
    gt = gpd.GeoDataFrame(rows, crs=utm)
    gt.to_crs(4326).to_file(dst, driver="GeoJSON")
    print(f"\nwrote {dst}: {len(gt)} points; width median {gt.gt_width_m.median():.2f} m, "
          f"p10 {gt.gt_width_m.quantile(.1):.2f}, p90 {gt.gt_width_m.quantile(.9):.2f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
