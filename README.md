# ATT&CK Layer Merger

This repository contains `merge.py`, a script for merging multiple MITRE ATT&CK layer JSON files into a single harmonized layer.

## Features

- Merge any number of ATT&CK layer JSON files
- Harmonize technique scores by selecting the highest score
- Merge metadata entries without exact duplicates
- Enable all techniques optionally
- Configure layer name, description, output path, score defaults, and gradient settings via CLI

## Requirements

- Python 3
- `mitreattack` package installed

## Usage

```bash
python merge.py layer1.json layer2.json -o merged_layers.json
```

### Arguments

- `input_files` - One or more ATT&CK layer JSON files to merge
- `-o`, `--output` - Output path for the merged layer JSON file
- `--name` - Name for the merged layer
- `--description` - Description for the merged layer
- `--default-score` - Default score to apply when a technique has no score
- `--disable-enable` - Do not enable all techniques in the merged layer
- `--min-value` - Minimum gradient value
- `--max-value` - Maximum gradient value
- `--colors` - Gradient colors to use for the merged layer

## Example

```bash
python merge.py lager_1.json lager_4.json -o merged_layers.json \
  --name "Harmonized merged layer" \
  --description "Merge of multiple sources with harmonized scores and metadata" \
  --default-score 0 \
  --min-value 0 \
  --max-value 5 \
  --colors "#ffffffff" "#ffe166ff" "#a9ff66ff" "#8ec843ff"
```

## Notes

- The script reads input files from the command line instead of using hard-coded paths.
- The output file is written as JSON and can be loaded by ATT&CK layer viewers.
