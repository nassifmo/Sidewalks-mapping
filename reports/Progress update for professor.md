# Sidewalk mapping in Lebanon — progress update

**Research question:** How can we obtain the dimensions of sidewalks in Lebanon, and identify the objects on them together with each object's location within the sidewalk?

## 1. What exists today

- **No sidewalk dataset exists for any Lebanese city.**
  - OpenStreetMap has only 32 mapped sidewalks nationwide, with no widths. About 0.2% of roads carry any sidewalk tag.
  - No public body (Beirut municipality, CDR, DGU, Army Geographic Affairs) publishes a sidewalk layer.
- **The closest sources are both Beirut-only and need permission to access:**
  - an AUB curb-line layer for Municipal Beirut (2010, 1:2,000);
  - an MIT/AUB "Community Streets" study (2022), which estimated sidewalk presence, width and obstructions for a few central neighbourhoods. Its data is not public.

## 2. Which imagery can be used

| Source | Usable? | Why |
|---|---|---|
| NASA / ESA satellites (Landsat, Sentinel) | No | 10–30 m pixels; a sidewalk is 1–3 m wide |
| Esri / Google imagery | Manual tracing only | Licences forbid AI processing or building datasets |
| Commercial 30 cm satellite | Possible, paid | About US$20/km² |
| Drones | Not currently | Army suspended drone permits nationwide, March 2026 |
| **Mapillary street-level photos** | **Yes, main source** | Open licence (CC BY-SA); dense in Beirut |

**Beirut test area (Mar Mikhael–Gemmayzeh–Achrafieh):** 11,001 Mapillary photos from 2016 onwards, mostly 2018–2020. Of these, 3,433 are 360° panoramas and 753 were taken on foot.

## 3. Method: an automated AI pipeline (minimal human input)

1. **Download** street photos with their position and heading (Mapillary API).
2. **Segment** every pixel as sidewalk, curb, road, pole, car, bin, etc. using Mask2Former trained on Mapillary Vistas, a worldwide street dataset.
3. **Measure in 3D:** estimate the ground plane and camera height (MoGe-2), then place every sidewalk pixel on the ground by geometry.
4. **Fuse all photos** into one overhead sidewalk map at 10 cm resolution. Each photo sees the sidewalk only between parked cars; combining photos fills the gaps.
5. **Measure widths** every 2 m along every street, on both sides, using OpenStreetMap streets.
6. **Detect objects** (poles, street lights, signs, bins, benches, parked cars and motorcycles, barriers, kiosks) and place them on the map. Each object is flagged as on or off the sidewalk, with its footprint size.
7. **Score automatically** against an answer key (see 4).

## 4. Validation before Lebanon: a benchmark with known answers

Lebanon has no measured sidewalks, so the accuracy of the method cannot be checked there directly. The pipeline is therefore first tested in **Washington DC (Adams Morgan)**.

- **Official data serving as the answer key:**
  - 926 sidewalk polygons;
  - 1,211 curb lines;
  - about 8,000 street objects (trees, street lights, poles, signs, meters, barriers);
  - 2,895 Project Sidewalk obstacle labels.
- **Same tools as for Lebanon:** the DC test uses only methods that also work there.

**Current status (preliminary):**
- **Pipeline:** runs end to end on a laptop GPU (RTX 5070).
- **Sidewalk location:** about 90% of detected sidewalk points fall within 3 m of an official sidewalk; median offset about 0.5 m.
- **Width:** not yet accurate. Average error is about 1.4 m in a 12-photo test; the target is 0.3–0.5 m. Multi-photo fusion was added to address this.
- **Full run:** a 300-panorama benchmark run is in progress.
- **Objects:** detected, but their placement on the map still needs work.

**Key lesson so far:** car-mounted cameras miss sidewalks hidden behind parked cars. In Lebanon, where cars park on sidewalks, photos taken on foot will be needed for reliable widths.

## 5. Next steps

1. Finish the DC benchmark and improve width and object accuracy until the targets are met.
2. Run the same pipeline on the Beirut test area, first as a visual check.
3. Teach the AI Lebanon-specific obstacles (generators, vendors, shop goods spilling out, kiosks, low wires) using a few hundred labelled Beirut examples.
4. Check Beirut results against the AUB 2010 curb lines and a small set of tape measurements.
5. Report each object's position across the sidewalk (distance from curb) and the clear walkable width left beside it.
6. Speed up processing for city-scale and national runs.

## 6. Where your support would help

- **AUB 2010 curb-line layer and MIT/AUB data:** an introduction to request them.
- **Ethics guidance:** advice on whether IRB review is needed if we do small field checks or capture new street photos in Beirut.
- **Computing resources:** possible access to university GPU time for larger runs.

*Background reports with sources (in the project folder):*
- *Lebanon sidewalk data collection*
- *Free imagery data for Lebanon sidewalks*
- *Sidewalk mapping framework for Lebanon*
- *Nationwide sidewalk mapping plan Lebanon*
