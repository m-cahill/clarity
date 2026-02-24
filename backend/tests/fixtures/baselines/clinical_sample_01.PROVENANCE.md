# Provenance: clinical_sample_01.png

## Source

**Title**: Normal posteroanterior (PA) chest radiograph (X-ray)
**File**: `File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg`
**Wikimedia Commons URL**: https://commons.wikimedia.org/wiki/File:Normal_posteroanterior_(PA)_chest_radiograph_(X-ray).jpg
**Direct image URL (original)**: https://upload.wikimedia.org/wikipedia/commons/a/a1/Normal_posteroanterior_%28PA%29_chest_radiograph_%28X-ray%29.jpg

## License

**CC0 1.0 Universal Public Domain Dedication**
https://creativecommons.org/publicdomain/zero/1.0/deed.en

No rights reserved. Free for any use including commercial, without attribution required.

## Author

Mikael Häggström (Wikimedia Commons user: Mikael Häggström)
Date of original: 28 June 2017

## Subject

Posteroanterior chest radiograph of a 21-year-old woman presenting with left thorax pain after a soccer collision. Shows a **normal chest** with no signs of injury or acute cardiopulmonary pathology.

## Retrieval and Preprocessing

- **Retrieved**: 2026-02-22
- **Downloaded resolution**: 500×572 px (Wikimedia Commons 500px thumbnail)
- **Preprocessing**:
  - Converted from JPEG (L mode grayscale) to RGB PNG
  - Resized to fit within 512×512 bounding box, preserving aspect ratio
  - Final size: 447×512 px
  - Saved as PNG (lossless) using Pillow LANCZOS resampling

## Rationale

Replaces the previous programmatic synthetic fixture (`create_clinical_sample_image()`),
which produced a gray radial gradient unsuitable for real model inference.
This real PA chest X-ray allows MedGemma to produce diagnostic-quality text output
with non-degenerate confidence and entropy signals.
