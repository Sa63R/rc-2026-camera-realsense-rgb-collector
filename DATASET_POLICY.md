# Dataset policy

## Scope

This Git repository is for capture code, documentation, and small text manifests. Raw images, labels, depth frames, camera recordings, model weights, and ZIP archives are intentionally excluded. The default `.gitignore` blocks common visual and dataset formats as a final guard, not as a substitute for review.

## Conditions for accepting or publishing a sample

Every sample must have a traceable source and a reviewer must be able to answer all of the following:

- Who captured or created it, when, and under what authority?
- What is the intended task and exact class/annotation definition?
- Which copyright or dataset license permits redistribution and model use?
- Were visible people informed and, where required, did they consent?
- Does the frame expose a face, badge, name, phone or computer screen, QR/barcode payload, vehicle plate, facility layout, access-control device, confidential object, or precise location?
- Is it original camera data, a transformed copy, a public third-party sample, or generated media?
- Is it already present under another filename, inside an archive, or in a locked evaluation set?
- To which capture session, object instance, scene, and split does it belong?

If any answer is unknown, keep the sample private or quarantined. Do not “solve” an unknown license by assigning a new blanket license.

## Capture rules

1. Agree on the meaning of `real` and `fake` before collecting. Directory names are not a data contract.
2. Use a new session directory for each date/location/camera setup. Record the session identifier outside the image pixels.
3. Save clean source frames. These scripts draw instructions only on a preview copy; do not reintroduce UI text, click markers, labels, or measurements into raw images.
4. Record camera model/serial, stream profile, exposure mode, scene, object, distance range, viewpoint, lighting, operator, intended use, and rights status in a manifest.
5. Review write errors immediately. A terminal message and a planned count are not proof that every image exists.
6. Preserve originals as read-only; perform resizing, redaction, conversion, and annotation in derived versioned datasets.

## Privacy and security review

EXIF removal is insufficient because sensitive information can be visible in the pixels. Before release, inspect full-resolution images and remove or irreversibly redact disallowed faces, bodies, badges, screens, QR/barcodes, signs, access controls, and recognizable interiors. Decode QR/barcodes in a controlled review environment; do not publish an unreadable code on the assumption that it is harmless.

Generated images must be separated from camera captures and must record the generator, model/service, date, prompt or generation recipe when releasable, edit history, and applicable service/output terms. They must not silently enter a “real camera” split.

## Duplicate and split policy

- Hash files to find byte-identical copies, including copies unpacked from archives.
- Run perceptual or embedding-based near-duplicate review for bursts and transformed copies.
- Split by capture session, date, physical object, scene, source image, and generation lineage—not by randomly shuffling individual frames.
- Keep locked test/evaluation sessions outside training and tuning storage.
- Do not count ZIP members and their extracted copies as separate samples.
- Publish split manifests and checksums with every dataset version.

The included `tools/build_manifest.py` creates a basic relative-path/SHA-256 inventory. It does not determine ownership, privacy, label correctness, or near-duplicate similarity.

## Where datasets should live

- Use a private or gated Hugging Face Dataset repository while rights and privacy reviews are incomplete; it is the preferred working distribution channel for an ML dataset and dataset card.
- Use Zenodo for a stable, reviewed archival snapshot when a citable DOI is useful.
- Use Kaggle only when there is a clearly defined, sanitized benchmark with trustworthy train/validation/test splits.
- Use a GitHub Release only for a small reviewed example or convenience artifact, not as the source of truth for a growing dataset.

The GitHub source repository should carry links, cards, schemas, checksums, and version identifiers—not the full dataset.

## Minimum dataset-card fields

- dataset name, version, maintainers, and contact route;
- task, classes, annotation schema, and negative-sample policy;
- capture hardware and high-level protocol;
- source/provenance and license by subset;
- privacy review and redaction method;
- sample counts after deduplication;
- split construction and leakage controls;
- known biases, limitations, and prohibited uses;
- integrity hashes and a changelog.
