import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from mitreattack.navlayers import Layer, LayerOps

DEFAULT_OUTPUT = Path("merged_layers.json")
DEFAULT_GRADIENT = {
    "colors": ["#ffffffff", "#ffe166ff", "#a9ff66ff", "#8ec843ff"],
    "minValue": 0,
    "maxValue": 50,
}


def load_layer(layer_path: Path) -> Layer:
    """Load a Layer object from a JSON file."""
    layer = Layer()
    layer.from_file(str(layer_path))
    return layer


def harmonize_score(values: List[Optional[float]]) -> Optional[float]:
    """Return the highest non-null score for a technique."""
    valid_scores = [score for score in values if score is not None]
    if not valid_scores:
        return None
    return max(valid_scores)


def merge_metadata(values: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Merge metadata lists from multiple layers without duplicates."""
    merged_metadata: List[Dict[str, Any]] = []
    for metadata_list in values:
        if metadata_list:
            merged_metadata.extend(metadata_list)

    if not merged_metadata:
        return []

    unique_metadata = [
        dict(item)
        for item in {tuple(entry.items()) for entry in merged_metadata}
    ]
    return unique_metadata


def create_layer_ops(name: str, description: str) -> LayerOps:
    """Return a LayerOps object configured for harmonized merging."""
    return LayerOps(
        score=harmonize_score,
        metadata=merge_metadata,
        name=lambda _: name,
        desc=lambda _: description,
    )


def enable_all_techniques(layer: Layer, enable: bool) -> None:
    """Enable every technique in the merged layer if requested."""
    if not enable:
        return

    layer_dict = layer.to_dict()
    for technique in layer_dict.get("techniques", []):
        technique["enabled"] = True
    layer.from_dict(layer_dict)


def set_gradient(layer: Layer, gradient: Dict[str, Any]) -> None:
    """Apply a gradient to the merged layer."""
    layer.gradient = gradient


def deduplicate_techniques(layer_dict: Dict[str, Any]) -> None:
    """Deduplicate techniques and remove tactic fields."""
    unique_techniques: Dict[str, Dict[str, Any]] = {}

    for technique in layer_dict.get("techniques", []):
        technique_id = technique.get("techniqueID")
        if not technique_id:
            continue

        record = dict(technique)
        record.pop("tactic", None)

        existing = unique_techniques.get(technique_id)
        if existing is None:
            unique_techniques[technique_id] = record
            continue

        existing_score = existing.get("score")
        record_score = record.get("score")
        if record_score is not None and (
            existing_score is None or record_score > existing_score
        ):
            existing["score"] = record_score

        existing["enabled"] = (
            existing.get("enabled", False) or record.get("enabled", False)
        )

        existing["metadata"] = merge_metadata(
            [existing.get("metadata", []), record.get("metadata", [])]
        )

    layer_dict["techniques"] = list(unique_techniques.values())


def write_json(data: Dict[str, Any], output_path: Path) -> None:
    """Write JSON data with indentation and line breaks."""
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4)
        handle.write("\n")


def merge_layers(
    layer_paths: Iterable[Path],
    output_path: Path,
    enable_techniques: bool,
    gradient: Dict[str, Any],
    default_score: int,
    name: str,
    description: str,
    attack_version: str,
) -> None:
    """Merge multiple ATT&CK layers and save the result."""
    layers = [load_layer(path) for path in layer_paths]
    merged_layer = create_layer_ops(name, description).process(
        layers,
        default_values={"score": default_score},
    )
    enable_all_techniques(merged_layer, enable_techniques)
    set_gradient(merged_layer, gradient)

    merged_dict = merged_layer.to_dict()
    if "versions" in merged_dict:
        merged_dict["versions"]["attack"] = attack_version
    deduplicate_techniques(merged_dict)
    write_json(merged_dict, output_path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Merge ATT&CK layer JSON files into a single "
            "harmonized layer."
        )
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        type=Path,
        help="One or more ATT&CK layer JSON files to merge.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output path for the merged layer JSON file.",
    )
    parser.add_argument(
        "--name",
        default=(
            "Harmonized merged layer"
        ),
        help="Name for the merged layer.",
    )
    parser.add_argument(
        "--description",
        default=(
            "Merge of multiple sources with harmonized scores "
            "and metadata"
        ),
        help="Description for the merged layer.",
    )
    parser.add_argument(
        "--default-score",
        type=int,
        default=0,
        help="Default score to apply when a technique is missing a score.",
    )
    parser.add_argument(
        "--disable-enable",
        action="store_true",
        help="Do not enable all techniques in the merged layer.",
    )
    parser.add_argument(
        "--min-value",
        type=int,
        default=(
            DEFAULT_GRADIENT["minValue"]
        ),
        help="Minimum gradient value.",
    )
    parser.add_argument(
        "--max-value",
        type=int,
        default=(
            DEFAULT_GRADIENT["maxValue"]
        ),
        help="Maximum gradient value.",
    )
    parser.add_argument(
        "--colors",
        nargs="*",
        default=DEFAULT_GRADIENT["colors"],
        help="Gradient colors to use for the merged layer.",
    )
    parser.add_argument(
        "--attack-version",
        default="19",
        help="ATT&CK version for the merged layer.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the layer merge process."""
    args = parse_args()

    if not args.input_files:
        raise ValueError("At least one input layer file is required.")

    gradient = {
        "colors": args.colors,
        "minValue": args.min_value,
        "maxValue": args.max_value,
    }
    merge_layers(
        args.input_files,
        args.output,
        not args.disable_enable,
        gradient,
        args.default_score,
        args.name,
        args.description,
        args.attack_version,
    )
    print(f"Merged {len(args.input_files)} layers into {args.output}.")


if __name__ == "__main__":
    main()
