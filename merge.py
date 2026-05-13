from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from mitreattack.navlayers import Layer, LayerOps

LAYER_FILES = [Path("lager_1.json"), Path("lager_4.json")]
MERGED_FILE = Path("merged_layers.json")
GRADIENT = {
    "colors": ["#ffffffff", "#ffe166ff", "#a9ff66ff", "#8ec843ff"],
    "minValue": 0,
    "maxValue": 5,
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

    unique_metadata = [dict(item) for item in {tuple(entry.items()) for entry in merged_metadata}]
    return unique_metadata


def create_layer_ops() -> LayerOps:
    """Return a LayerOps object configured for harmonized merging."""
    return LayerOps(
        score=harmonize_score,
        metadata=merge_metadata,
        name=lambda _: "Harmonized merged layer",
        desc=lambda _: "Merge of multiple sources with harmonized scores and metadata",
    )


def enable_all_techniques(layer: Layer) -> None:
    """Enable every technique in the merged layer."""
    layer_dict = layer.to_dict()
    for technique in layer_dict.get("techniques", []):
        technique["enabled"] = True
    layer.from_dict(layer_dict)


def set_gradient(layer: Layer) -> None:
    """Apply a unified gradient to the merged layer."""
    layer.gradient = GRADIENT


def merge_layers(layer_paths: Iterable[Path], output_path: Path) -> None:
    """Merge multiple ATT&CK layers and save the result."""
    layers = [load_layer(path) for path in layer_paths]
    merged_layer = create_layer_ops().process(layers, default_values={"score": 0})
    enable_all_techniques(merged_layer)
    set_gradient(merged_layer)
    merged_layer.to_file(str(output_path))


def main() -> None:
    """Run the layer merge process."""
    if not LAYER_FILES:
        raise ValueError("No layer files configured for merging.")

    merge_layers(LAYER_FILES, MERGED_FILE)
    print(f"Merged {len(LAYER_FILES)} layers into {MERGED_FILE}.")


if __name__ == "__main__":
    main()
