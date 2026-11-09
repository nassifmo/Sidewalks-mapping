# Street-Level Imagery Capture Specification and Operations Plan (City-to-Country Scale, Lebanon)

Research date: 2026-11-06. Scope: equipment, mounting, settings, positioning, throughput, data volumes, pipeline, privacy, costs, temporal design. Note: roughly 30 tool calls were used; several vendor pages (help.mapillary.com) returned HTTP 403 to direct fetch, so some Mapillary guidance is taken from search-result excerpts of those pages (marked). Everything not backed by a URL is in "Inferences" or "Gaps".

---

## 1. Cameras: specs, interval modes, GPS, price, and platform recommendations

### Takeaway
Buy the GoPro MAX 2 (about USD 500, 8K 360 video, 29 MP 360 stills, built-in GPS). Mapillary names it as its recommended consumer 360 camera, and Trekview's backpack rig uses the GoPro MAX. The Insta360 X5 has a sharper sensor (72 MP stills) but no GPS of its own: it takes position from a paired phone, and its GPS tagging in interval-photo mode is unreliable. Survey-grade mobile mapping systems such as the Trimble MX50 are quote-only, 23 kg LiDAR+camera rigs, which is overkill for a volunteer- or NGO-scale campaign.

### Cited Findings
- **Mapillary recommendation:** Mapillary's help center says "The GoPro MAX series is our recommended consumer-grade 360° camera to use with Mapillary. The MAX 2 is the highest resolution version available, but the MAX and MAX 2025 will also work well." (search excerpt) — [Mapillary Help: Our favorite cameras](https://help.mapillary.com/hc/en-us/sections/17261805417500-Our-favorite-cameras); [Mapillary camera recommendations](https://www.mapillary.com/cameras)
- **Why Mapillary prefers GoPro:** it has built-in GPS, Mapillary Desktop Uploader and CLI support it natively, and it does not need stitching before upload. A Mapillary staff forum post adds that it is "generally more affordable" — [Mapillary forum: Better Insta360 X3 support](https://forum.mapillary.com/t/new-better-insta360-x3-support/7667)
- **Mapillary .360 support:** Mapillary announced seamless support for native .360 video files from the GoPro MAX2 — [Mapillary forum: Seamless support for .360 video files (GoPro MAX2)](https://forum.mapillary.com/t/new-seamless-support-for-360-video-files-gopro-max2/10119)
- **Mapillary camera grant program:** 40 GoPro MAX cameras went to contributors in the US (via OSM US) and Europe (via OSM Belgium). After about one year they had produced about 8.5 million images, with a median of 39,749 and a mean of 212,460 photos per camera. Lessons from the program: "past behavior is a great indicator of future behavior", periodic check-ins keep people capturing, embedded GPS and on-device stitching make the camera easy to use, and one Mapillary organization per camera makes tracking easier — [Mapillary blog: Recapping the Camera Grant Program (Oct 2024)](https://blog.mapillary.com/update/2024/10/31/recapping-the-camera-grant-program)
- **GoPro MAX 2 specs and price:** launched September 2025 at USD 499.99 (UK from GBP 449.99, DE about EUR 519.99). It records 8K30 360 video, 5.6K60 and 4K100, and takes 29 MP 360 stills. It has built-in GPS (GoPro calls it the only 360 camera with built-in GPS), is waterproof to 5 m, has a 1960 mAh Enduro battery, and weighs 195 g. Its lenses are replaceable — [Imaging Resource](https://old.imaging-resource.com/news/2025/09/23/gopro-max-2-launched-price-8k-360-video-features-and-where-to-buy); [New Atlas](https://newatlas.com/photography/gopro-360-action-cam-max2-8k-lenses); [Business Standard](https://www.business-standard.com/amp/technology/gadgets/gopro-max-2-360-lit-hero-action-camera-launched-125092400249_1.html)
- **GoPro MAX 2 field report (OSM diary):** the author tested 5.6K and 8K. At 5.6K, house numbers and business signs were hard to read; 8K made them readable. Files reach about 10 GB each, a 64 GB card fills in about 2 hours, and the camera takes SD cards up to 1 TB. Battery life is about 2 hours or less. If the battery or card runs out mid-recording, the file is left unclosed and must be repaired with a tool such as Disk Drill. Copying the 10 GB files failed through an old card reader — [OSM diary apm-wa: Update on the GoPro Max2 for street-level imagery](https://www.openstreetmap.org/user/apm-wa/diary/409291)
- **Insta360 X5:** base price USD 549.99 at launch (April 2025). Later listings ranged from about USD 465 to USD 649. It has a 1/1.28-inch sensor, F2.0, weighs 200 g, and takes 72 MP (11904x5952) or 18 MP photos. Its modes include Interval, Timelapse and Burst. It has **no built-in GPS** and uses the paired phone's position instead — [Engadget hands-on](https://www.engadget.com/cameras/insta360-x5-launch-date-price-hands-on-132439941.html); [Insta360 X5 manual: shooting specs](https://onlinemanual.insta360.com/x5/en-us/specs/shooting-specs); [Mapillary forum: Insta360 X5](https://forum.mapillary.com/t/insta-360-x5-camera/9516)
- **Mapillary Insta360 guidance (search excerpt; the page returned 403 to direct fetch):**
  - Walking: timelapse 360 video at a 2 s interval and 8K.
  - Driving: timelapse 360 video at a 0.2 s interval and 8K.
  - The X5 can take interval photos at 3 s and 72 MP, but Mapillary "doesn't currently recommend interval photos" because GPS tagging fails after the first image.
  - [Mapillary Help: Insta360 article](https://help.mapillary.com/hc/en-us/articles/11951588568604)
- **Ricoh Theta X:** launched at USD 799 (EUR 999), with recent retail around USD 597–700. It has built-in GPS with A-GPS, 5.7K30 video, and stills of 60 MP (some listings say 48 MP). It has a 2.25-inch touchscreen, a swappable battery and weighs 144 g; at launch it shot JPEG only — [PopPhoto](https://www.popphoto.com/gear/new-ricoh-theta-x-360-camera/); [Notebookcheck](https://www.notebookcheck.com/Ricoh-praesentiert-die-Theta-X-360-Grad-Kamera-mit-grossem-Touchscreen-und-5-7K-Videoaufnahmen.595488.0.html); [Procam](https://procam.com/collections/cameras/products/ricoh-theta-x-360-camera)
- **Trekview:** says GoPro "Max and Fusion 360 cameras are the best", and its Trek Pack v2 backpack rig uses the GoPro MAX — [Trek View](https://www.trekview.org); [Trek Pack v2](https://www.trekview.org/trek-pack)
- **Trimble MX50 (survey-grade mobile mapping):**
  - Sensor unit is 23 kg and rated IP64.
  - LiDAR: up to 960 kHz, 240 scans/s, 80 m range.
  - Spherical camera: 30 MP (6 x 5 MP).
  - 2 TB onboard storage.
  - Launched July 2021 as a "mid-range" system; no public price, quote only.
  - [Trimble MX50 product page](https://geospatial.trimble.com/en/products/hardware/trimble-mx50); [Geo Week News](https://www.geoweeknews.com/articles/trimble-adds-new-mid-range-mx50-to-mobile-mapping-portfolio/)
- **Trimble MX7:** Trimble's 360 imaging-only mobile mapping product page exists, but I did not retrieve specs or a price — [Trimble MX7](https://geospatial.trimble.com/en/products/hardware/trimble-mx7)
- **Trimble Mosaic cameras:** Mapillary blogged in January 2023 about Trimble Mosaic 360 cameras being used with Mapillary. I did not retrieve the details — [Mapillary blog: Mosaic 360 Cameras](https://blog.mapillary.com/update/2023/01/26/Mosaic-360-Cameras-Mapillary.html)

### Inferences
- **Recommended camera:** GoPro MAX 2 at 8K. It is cheap (about USD 500), has native GPS and native Mapillary .360 support, and 8K is needed for signage and detail legibility. At about USD 500 per unit, a fleet of 10 cameras plus spares costs around USD 6–8k, versus a quote-only survey rig that likely costs tens to hundreds of thousands of USD (no cited price).
- **Insta360 X5 as a secondary option:** consider it only where the extra resolution matters, and pair it with external GNSS logging, because it depends on a phone for GPS.
- **Theta X:** a competent stills camera, but with lower video resolution (5.7K) and less Mapillary tooling support.

### Gaps
- Not retrieved: Insta360 X4 specs and price, Labpano Pilot Era/One specs and price, Trimble MX7 and Mosaic 51/X specs and prices, NavVis VLX / Leica BLK2GO backpack prices, and iPhone LiDAR capture suitability.
- No official Panoramax camera recommendation page was found. The Panoramax docs site was not reached.
- No quantitative GPS accuracy figure for GoPro MAX 2 or Theta X internal GPS was found.

---

## 2. Mounting, camera height, frame spacing, walking vs driving

### Takeaway
Measurement methods that use a single image get their metric scale from the camera height. In UrbanVGGT, an error of ±0.25 m in assumed height raises width error from 0.25 m to about 0.28 m and adds a ±0.1–0.2 m bias. Fix the camera at a known, logged height (about 2.5 m on a car mast, or a fixed pole on a backpack) and keep it level. For walking, capture every 2 s at about 5 km/h (about 2.8 m spacing). For video, the default extraction is one frame per 3 m.

### Cited Findings
- **UrbanVGGT method:** SegFormer-B5 segmentation, then VGGT single-image 3D reconstruction, then RANSAC ground-plane fit, then metric scale s = h_cam / h_pred. Camera mounting height is "the only external parameter". The study used h_cam = 2.5 m as a fixed prior for Google Street View car imagery, following Lieu and Guhathakurta (2025). On the Washington, D.C. benchmark it reports MAE 0.252 m, with 95.5% of estimates within 0.50 m — [UrbanVGGT, arXiv 2603.22531](https://arxiv.org/pdf/2603.22531); [ISPRS Archives XLIX-B2-2026-559](https://isprs-archives.copernicus.org/articles/XLIX-B2-2026/559/2026/)
- **UrbanVGGT camera-height sensitivity (Table 2, from the PDF text):** overestimating height overestimates width, and the reverse — [UrbanVGGT](https://arxiv.org/pdf/2603.22531)

  | Assumed height | MAE | Bias | Within 0.25 m | Within 0.50 m |
  |---|---|---|---|---|
  | 2.00 m | 0.384 m | −0.380 m | 29.7% | 65.5% |
  | 2.25 m | 0.283 m | −0.217 m | 50.6% | 82.4% |
  | 2.50 m | 0.252 m | −0.055 m | 49.9% | 95.5% |
  | 2.75 m | 0.276 m | +0.104 m | 50.0% | 85.0% |
  | 3.00 m | 0.349 m | +0.263 m | 46.5% | 69.1% |

- **UrbanVGGT failure modes and limits:**
  - Occlusion by "parked vehicles, pedestrians, street furniture, vegetation, or utility poles".
  - Non-planar ground: ramps, curb cuts, cross-slopes.
  - Very narrow sidewalks.
  - Complex curbs: bulb-outs, parking bays, bus stops, shared-space streets.
  - Height variation "across vehicle generations may introduce systematic bias".
  - Sampling was one point every 30 m with two perpendicular headings (±90°).
  - The resulting dataset is an "unvalidated prototype".
  - [UrbanVGGT](https://arxiv.org/pdf/2603.22531)
- **Mapillary mounting guidance:** keep the camera at least 30 cm above your head to minimize head interference (search excerpt) — [Mapillary Help article](https://help.mapillary.com/hc/en-us/articles/360012674619)
- **RTK rover setup with a GoPro Max:** one OSM mapper mounts the GoPro 60–80 cm above the GNSS antenna to keep the antenna out of the 360 image — [OSM diary oldnab](https://api.openstreetmap.org/user/oldnab/diary/408535)
- **Effect of extra height:** the OSM wiki notes that raising the camera adds little information about areas far beyond the path beneath the photographer, such as the horizon — [OSM Wiki: Camera positioning](https://wiki.openstreetmap.org/wiki/Camera_positioning)
- **Mapillary GoPro MAX capture modes (search excerpts):**
  - Driving: 360 video, 25 fps, 5.6K (8K on MAX 2).
  - Walking: 360 timelapse photo every 2 s, 16 MP (29 MP on MAX 2), "sufficient for walking (up to ~3 mph or 5 km/h)".
  - Biking: 360 timelapse video at 0.5 s.
  - Video is now the recommended method for cars and bikes.
  - Imagery without GPS cannot be processed.
  - [Mapillary Help: GoPro MAX](https://help.mapillary.com/hc/en-us/articles/360012674619); [Mapillary Help: Video uploads](https://help.mapillary.com/hc/en-us/articles/115001485045-Video-uploads)
- **Community disagreement on driving:** some drivers use 2 s timelapse photos, others say video is needed — [Mapillary forum: optimal settings for GoPro Max](https://forum.mapillary.com/t/optimal-camera-recording-settings-for-gopro-max/7652); [Mapillary forum: 0.5 s too sparse for driving?](https://forum.mapillary.com/t/360-photos-every-0-5-seconds-is-too-sparse-for-driving/6931)
- **Frame spacing from video:** mapillary_tools by default extracts one frame every 3 m of travel. The distance can be set (e.g. `--video_sample_distance 5`), or you can switch to time sampling with `--video_sample_distance -1 --video_sample_interval 2` — [mapillary_tools README](https://github.com/mapillary/mapillary_tools)

### Inferences
- **Fix and record the height.** For UrbanVGGT-style width estimation on your own imagery, h_cam must be fixed per rig and recorded in metadata. A walking rig (backpack pole, camera about 2.2–2.5 m above ground) and a car rig (camera about 2.3–2.6 m above ground on a roof mast) will each need their own h_cam. An RTK antenna plus a lever-arm measurement gives the height directly.
- **Height tolerance.** Holding height within ±5 cm keeps the scale error under about 2%. At 2.5 m, every 10 cm of height error is a 4% scale error, which is about 8 cm on a 2 m sidewalk. This follows from the linear relation in the paper.
- **Walking vs driving in Lebanese streets.**
  - Driving puts the camera in the road. In dense Lebanese streets the curb-side boundary is often hidden behind parked cars, which is UrbanVGGT's main occlusion failure.
  - Walking on or next to the sidewalk sees both the building line and the curb from close range.
  - But where cars are parked on the sidewalk, the walker is pushed into the road anyway.
  - Proposed split: drive arterials with 2.5 m car masts, capturing both sides from one pass. Walk dense cores and alleys with backpack poles, one pass per side of the street where a street is wider than about 12 m, a single centreline pass where it is narrower. Spacing should be 2–3 m for SfM.
- **Driving spacing.** At 20–30 km/h in urban traffic, 8K30 video sampled every 2–3 m gives the 1–3 m spacing needed for SfM overlap. Timelapse photos at 2 s would give about 11–17 m spacing, which is too sparse.

### Gaps
- Not obtained: the exact Google Street View camera height or the Lieu and Guhathakurta (2025) source. The Panoramax and Trekview mount-height specifications were not retrieved.
- No peer-reviewed study comparing walking-captured and driving-captured sidewalk widths was found.

---

## 3. Positioning: camera GPS errors, external GNSS/RTK, LEB-CORS, sync, SfM

### Takeaway
Smartphone and consumer-camera GNSS in urban canyons is off by several metres to more than 10 m. Lebanon has a national network RTK service, LEB-CORS: 13 stations, about 3 cm accuracy, with RINEX downloadable for post-processing. Pairing a GoPro with an RTK receiver (Emlid RS3 about USD 2.5–3.6k, or a u-blox F9P-class logger) is a documented workflow for Panoramax. RTK accuracy is for the antenna, so the lever arm to the camera must be measured.

### Cited Findings
- **LEB-CORS:** run by the Lebanese Army's Directorate of Geographic Affairs. It has 13 reference stations running 24/7, offers network RTK at about 3 cm accuracy, and provides raw observations in RINEX for post-processing — [LEB-CORS portal](https://lebcors.army.gov.lb)
- **LEB-CORS funding:** the network launched in 2023 after about a year of work, cost USD 700,000, and was funded by USAID and the Directorate — [LBC News](https://lbcgroup.tv/news/lebanon-news/691386/lebanese-army-launches-online-network-to-facilitate-geographical-surve/en)
- **Smartphone urban-canyon accuracy:**
  - Dual-frequency smartphone positioning with 3D-mapping aid reaches about 10 m on average in urban canyons (better than L1-only) — [ION Navigation / PolyU](https://ira.lib.polyu.edu.hk/handle/10397/92730?mode=full)
  - Under 5 m in Hong Kong urban canyons with the same approach — [PolyU PAIR](https://polyu.edu.hk/pair/publications/issue-3/kt3---urban-positioning)
  - Smartphone precise point positioning reaches "only... a few meters" — [MDPI Sensors 2025](https://www.mdpi.com/1424-8220/25/14/4452)
- **GoPro MAX + SparkFun RTK Express → Panoramax:** an MIT-licensed tutorial, last pushed 2024-02-15 — [binnette/gopro-max_sparkfun-rtk-express_panoramax](https://awesome.ecosyste.ms/projects/github.com%2Fbinnette%2Fgopro-max_sparkfun-rtk-express_panoramax)
- **SparkFun accuracy claim:** RTK devices output position at 14 mm horizontal and vertical accuracy at up to 20 Hz (vendor claim) — [SparkFun RTK firmware](https://github.com/sparkfun/SparkFun_RTK_Firmware/pull/214/files). That figure applies to the antenna reference point, not the camera — [SparkFun community](https://community.sparkfun.com/t/rtk-express-plus-for-position-and-attitude-of-camera/44707)
- **Phone EXIF with NTRIP active:** the Samsung camera app wrote erratic EXIF positions while NTRIP was active; OpenCamera worked correctly — [OSM diary oldnab](https://api.openstreetmap.org/user/oldnab/diary/408535)
- **Emlid Reach RS3:**
  - Price: retail about USD 2,519–3,647, or GBP 2,699; UK survey kits about GBP 4,078–4,228 — [Advexure](https://advexure.com/products/emlid-reach-rs3); [Heliguy](https://checkout.heliguy.com/products/emlid-reach-rs3-rtk-receiver)
  - Accuracy: 1–2 cm with Emlid Corrections; built-in LTE modem for NTRIP; tilt compensation — [Advexure comparison](https://advexure.com/blogs/news/emlid-rs3-vs-rs2-vs-rx-which-gnss-receiver-is-right-for-you)
- **Using external GNSS with mapillary_tools:** geotagging video from an external GPX file only works with interval (time-based) sampling, not distance sampling. Supported telemetry sources include GoPro GPMF and CAMM. Keep the original .360 files: exporting to .mp4 in GoPro Player changed timestamps so GPMF no longer matched — [mapillary_tools README](https://github.com/mapillary/mapillary_tools); [Mapillary forum: From MP4 to Mapillary](https://forum.mapillary.com/t/from-mp4-to-mapillary/5311)

### Inferences
- **Positioning workflow:**
  1. Log raw GNSS on an F9P or Emlid receiver mounted on the same pole as the camera.
  2. Post-process in RTKLIB or Emlid Studio against LEB-CORS RINEX (PPK). This avoids dropped NTRIP in canyons.
  3. Sync to the camera by aligning the GoPro GPMF timestamps (GPS-time based) with the GNSS log.
  4. Apply the measured lever arm.
  5. Refine with OpenSfM (Mapillary's own pipeline) or COLMAP using the GNSS positions as priors.
- **Expected accuracy (not measured):** sub-decimetre where there is a fix, and SfM-bridged in deep canyons.
- **LEB-CORS access:** subscription and pricing terms were not found, so they need to be confirmed with the Directorate of Geographic Affairs.

### Gaps
- No cited figure for GoPro MAX or MAX 2 GPS error in urban canyons.
- No Emlid Reach RX price found.
- No ZED-F9P logger prices retrieved.
- No published accuracy gain from OpenSfM or COLMAP alignment of 360 sequences found.
- LEB-CORS subscription costs, NTRIP mountpoints and coverage outside Beirut not retrieved.

---

## 4. Throughput, data volumes, upload and processing pipeline, storage

### Takeaway
A GoPro MAX 2 at 8K fills about 32 GB per hour (a 64 GB card in about 2 hours), with a battery life of about 2 hours. That works out to roughly 6 GB/km walking at 5 km/h and roughly 1–2 GB/km driving at 15–30 km/h; both are derived figures. A 400 TB Panoramax national instance (OSM-France) shows that self-hosting is mainly a storage problem. Bandwidth is the classic bottleneck in low-connectivity countries.

### Cited Findings
- **GoPro MAX 2 data rate and battery:** a 64 GB card fills in about 2 hours, .360 files reach about 10 GB, battery lasts about 2 hours or less, and cards up to 1 TB are supported — [OSM diary apm-wa](https://www.openstreetmap.org/user/apm-wa/diary/409291)
- **Original GoPro MAX bitrate:** sources conflict. A calculator gives about 120 Mbps for 5.6K 360 (about 54 GB/h); CloudPano gives 45 Mbps or 78 Mbps — [SD Card Checker](https://sdcardchecker.pages.dev/tools/calculators/gopro-storage); [CloudPano](https://www.cloudpano.com/blog/what-is-the-bitrate-for-the-gopro-max-360-mode)
- **File splitting:** GoPro caps files at 4 GB, so a single MAX recording is split across several .360 files — [arj.no](https://arj.no/2023/05/25/gopro-max-file-format)
- **mapillary_tools commands:** `process_and_upload` combines processing and upload; `video_process` can be run first, followed by `upload`. It supports .mp4 and .360 with GPMF or CAMM telemetry — [mapillary_tools GitHub](https://github.com/mapillary/mapillary_tools)
- **Panoramax storage, OSM-France instance:** about 400 TB on ZFS, with 2x GTX 1070 GPUs for blurring. Tiled 360 copies roughly double storage. Another figure: about 100 TB for 20M pictures including redundancy and backup — [OSM Community: A Panoramax UK instance?](https://community.openstreetmap.org/t/a-panoramax-uk-instance/119989); [OSM Community: Server sustainability](https://community.openstreetmap.org/t/server-sustainability/145491)
- **Panoramax storage, small instances:** a 1 TB instance holds about 400–450 GB of 360 HD originals. Hetzner storage boxes have been used. 4x 6 TB disks in software RAID give 16 TB usable — [OSM Community: Panoramax NZ instance](https://community.openstreetmap.org/t/a-panoramax-nz-instance/145079); [Wikimedia Italia: Panoramax requirements and costs](https://wiki.wikimedia.it/wiki/OpenStreetMap/Panoramax/Requisiti_e_aspetti_finanziari)
- **Panoramax RAM rule of thumb:** about 1 GB of RAM per TB of ZFS storage (60 TB → 60 GB RAM + 12 GB) — [OSM Belgium HackMD](https://hackmd.io/@osmbe/BJizW8nUp)
- **Upload bandwidth in Africa:** for high-resolution imagery capture in Africa, "the main bottleneck for uploading high resolution imagery in Africa is limited internet access" — [Mapillary blog: Streetview Photographer (2023)](https://blog.mapillary.com/update/2023/08/11/Streetview-Photographer-Mapillary.html)

### Inferences
- **Per-km volumes** (derived from about 32 GB/h measured on the MAX 2 at 8K):
  - Walking at 4–5 km/h: about 6.5–8 GB/km of raw video.
  - Driving at 15–25 km/h in city traffic: about 1.3–2.1 GB/km.
  - Frames extracted every 3 m: about 333 frames/km. At an assumed 5–10 MB per 8K equirectangular JPEG (not cited), that is about 1.7–3.3 GB/km of extracted images.
- **Throughput per crew:**
  - Walking: about 2 hours of battery per pack, so carry 3–4 batteries. A 5–6 hour field day at 4 km/h is about 15–25 km of street side per walker.
  - Driving: in Beirut traffic at an average 10–15 km/h over 5–6 hours, about 50–90 km per car per day.
  - These are not field-measured; pilot to calibrate.
- **Scale of the national dataset:** Lebanon's road network was not retrieved for this note. Assuming roughly 20,000–25,000 km of roads, mostly driven, raw video would be about 30–50 TB. Plan for 2x that for archive plus frames.
- **Upload strategy:** keep the raw .360 files privately (needed for re-extraction, re-blurring and SfM). Upload extracted frames to Mapillary or Panoramax from an office fibre link, not 4G.

### Gaps
- No measured km/day figures for walking or driving SVI campaigns were found.
- No official GoPro MAX 2 bitrate was found.
- No published Mapillary processing delay figures were found.
- No measured MB per extracted 8K frame was found.

---

## 5. Privacy: blurring tools and Lebanon Law 81/2018

### Takeaway
There are open-source blurrers for both faces and plates. Meta's EgoBlur (Apache 2.0, face AP 0.99 / AR 0.998, about 0.5 s per 2 MP image on GPU) handles faces and plates. Panoramax's SGBlur is YOLOv8-based and edits JPEG coefficients losslessly. Deface (ORB-HD) does faces only. Lebanon's Law 81/2018 includes personal-data provisions, but no source addressed street imagery specifically, and sources disagree on whether there is an enforcement authority.

### Cited Findings
- **EgoBlur:**
  - Licence: Apache 2.0, research and commercial use.
  - Architecture: FasterRCNN detectors for faces and for plates, each about 400 MB and about 104M parameters.
  - Accuracy: face AP 0.99 / AR 0.998.
  - Speed: about 0.5 s per 2 MP image on GPU, about 8 s on CPU.
  - Documented as working across camera types.
  - [EgoBlur paper arXiv 2308.13093](https://arxiv.org/pdf/2308.13093v2.pdf); [Project Aria EgoBlur docs](https://facebookresearch.github.io/projectaria_tools/docs/open_models/egoblur); [Hugging Face](https://huggingface.co/projectaria/EgoBlur)
- **SGBlur (Panoramax):** a custom-trained YOLOv8 for faces and plates. It edits JPEG coefficients directly so the rest of the image is unchanged, and needs an NVIDIA GPU with CUDA — [SGBlur GitHub](https://github.com/cquest/sgblur)
- **deface (ORB-HD):** a CLI for face anonymization in video and photos. Blur, box or mosaic options; detection threshold 0.2 by default; drops audio by default. Faces only — [ORB-HD/deface](https://github.com/ORB-HD/deface); [PyPI](https://pypi.org/project/deface/)
- **Law 81/2018 scope:** covers e-transactions, e-commerce and personal data protection — [UNESCWA Arab Legislation Portal](https://alp.unescwa.org/legislations/law-81-2018-electronic-transactions-and-personal-data); [DLA Piper Data Protection: Lebanon](https://www.dlapiperdataprotection.com/?c=LB&t=law)
- **Law 81/2018 enforcement is contested:** one source says it has no independent data protection regulator; another claims an authority was established in 2023. A rights NGO says the law fails to protect privacy and is poorly implemented — [DLA Piper](https://www.dlapiperdataprotection.com/?c=LB&t=law); [Euro-Med Monitor](https://euromedmonitor.org/ar/article/5630/Lebanon:-Data-protection-law-fails-to-protect-people%E2%80%99s-privacy-and-data)

### Inferences
- **Blurring before anything leaves the team:** run EgoBlur (faces and plates) or SGBlur on extracted frames before any public upload. Mapillary also blurs on ingest, but its accuracy figures were not retrieved.
- **Raw archive:** keep unblurred raw .360 files only on encrypted, access-controlled storage, with a documented purpose (sidewalk inventory) and a retention period. This aligns with the purpose-limitation principles that summaries attribute to Law 81.
- **Legal review:** get a short legal opinion in Lebanon. Also be mindful of security sensitivities around filming military or government sites. That is an inference, with no source retrieved.

### Gaps
- Mapillary's automatic blurring documentation was not retrieved.
- Understand.ai anonymizer details were not retrieved.
- Not found: the specific Law 81/2018 articles on images, consent and public space, and any Lebanese rules on photographing military areas.

---

## 6. Real campaigns: scale, throughput, cost per km

### Takeaway
There are well-documented large crowdsourced campaigns. The World Bank Zanzibar capture produced 699,000+ images along 1,800 km, KartaView holds about 384M images over about 8M km, and the Mapillary grant gave 40 cameras that produced 8.5M images. No source gave a cost per km.

### Cited Findings
- **World Travel in 360 / World Bank / State University of Zanzibar:** more than 699,000 images across 1,800 km of roads and footpaths, later expanded to Uganda, Zimbabwe and Zambia. Limited internet access was the main upload bottleneck — [Mapillary blog (Aug 2023)](https://blog.mapillary.com/update/2023/08/11/Streetview-Photographer-Mapillary.html)
- **World Bank Laos:** Mapillary was used to build a rural road inventory and condition monitoring for a network with no complete map — [Case study: World Bank and Mapillary](https://www.casestudies.com/company/mapillary/case-study/the-world-bank-customer-case-study)
- **Mapillary camera grant:** 40 GoPro MAX units produced about 8.5M images in about a year — [Mapillary blog](https://blog.mapillary.com/update/2024/10/31/recapping-the-camera-grant-program)
- **KartaView:** run by Grab, renamed from OpenStreetCam in November 2020. More than 384M images covering almost 8M km of road (undated Trekview post) — [Wikipedia: KartaView](https://en.wikipedia.org/wiki/KartaView); [Trekview: Getting started with KartaView](https://www.trekview.org/blog/getting-started-with-kartaview/)
- **Cost framing:** a 2020 State of the Map talk called 360 mobile mapping one of the most time- and cost-effective collection methods, while noting the equipment can be expensive — [SotM 2020: The Map in 360](https://pretalx.com/sotm2020/talk/YTHZWC/)
- **Images per km in Zanzibar:** about 388 images/km (699,000 ÷ 1,800), consistent with roughly 2–3 m spacing — derived from [Mapillary blog](https://blog.mapillary.com/update/2023/08/11/Streetview-Photographer-Mapillary.html)

### Inferences
- **Rough budget for Lebanon (not cited; for planning only):**
  - Equipment: about USD 500 per camera, plus about USD 3k per RTK receiver.
  - Staff: field days at local rates.
  - Vehicles: fuel at about 60–80 km/day per car.
  - Total marginal cost is likely on the order of USD 5–20 per driven km once equipment is amortized, and higher per walked km. Validate with a pilot.

### Gaps
- No cost-per-km figures were found for any campaign (Mapillary, KartaView, HOT, World Bank/GFDRR).
- Not retrieved: Project Sidewalk work using its own imagery, the HOT/GFDRR Open Cities street-view budgets, and the Dar es Salaam km totals.

---

## 7. Time-of-day / day-of-week design for temporary occupation and repeat surveys

### Takeaway
No source specifically on time-sampled street-view designs for measuring how much of the sidewalk is occupied was retrieved. The design below is inference only. Separate two products: a **baseline geometry** layer (width and surface, captured once, in low-occupancy conditions) and a **repeated occupation** layer (parked cars, vendors, café furniture), sampled on fixed routes at fixed times.

### Cited Findings
- UrbanVGGT reports parked vehicles and street furniture as occlusion failure modes for geometry measurement. This supports capturing the geometry baseline in low-occupancy periods — [UrbanVGGT](https://arxiv.org/pdf/2603.22531)

### Inferences
- **Geometry baseline:** capture early morning (about 06:00–08:00) on a weekday, or on Sunday morning in commercial districts, when parking and vendors are fewest. Lighting is lower, so 8K and a stable mount matter more.
- **Occupation surveys:** pick a stratified sample of streets (for example 5–10% of the network, by land use). Capture repeatedly:
  - Weekday 08:00 (commute and school drop-off parking).
  - Weekday 12:00–14:00 (commercial peak).
  - Evening 19:00–22:00 (cafés and restaurants spreading onto the sidewalk).
  - Friday or Saturday evening.
  - Repeat seasonally, summer vs winter for terrace furniture.
- **Repeatability:** use the same rig height, route GPX and direction so frames can be matched. Mapillary and Panoramax sequences carry timestamps, which allows comparing the same location over time.

### Gaps
- No literature retrieved on temporal sampling of SVI for sidewalk encroachment, informal vendors or café furniture.
- No Lebanese municipal data on peak parking times was found.
