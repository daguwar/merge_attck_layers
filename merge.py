from mitreattack.navlayers import Layer, LayerOps

# 1. Load your layers from files (or from dicts/strings)
layer1 = Layer()
layer1.from_file("lager_1.json")

#layer2 = Layer()
#layer2.from_file("lager_2.json")

#layer3 = Layer()
#layer3.from_file("lager_3.json")

layer4 = Layer()
layer4.from_file("lager_4.json")

# --- DEFINE HARMONIZATION FUNCTIONS ---

def harmonize_score(values):
    # 'values' is a list with the 4 score values for a specific technique.
    # Filter out layers where the technique has no score (None)
    valid_scores = [score for score in values if score is not None]

    if not valid_scores:
        return None  # The technique had no score in any layer.

    # Here we harmonize by selecting the HIGHEST VALUE.
    # (You can replace max(...) with sum(...) / len(...) if you prefer the average.)
    return max(valid_scores)


def merge_metadata(values):
    # 'values' is a list of metadata from the 4 layers (each item is a list of dicts).
    merged_metadata = []

    for metadata_list in values:
        if metadata_list:
            # Add all key/value pairs
            merged_metadata.extend(metadata_list)

    if not merged_metadata:
        return []

    # To avoid duplicates of exactly the same metadata, make the list unique
    # by temporarily converting entries to frozen tuples.
    unique_metadata = [dict(t) for t in {tuple(item.items()) for item in merged_metadata}]
    return unique_metadata

# 2. Create the LayerOps object
layer_ops = LayerOps(
    score=lambda x: harmonize_score(x),
    metadata=lambda x: merge_metadata(x),
    name=lambda x: "Harmonized merged layer",
    desc=lambda x: "Merge of multiple sources with harmonized scores and metadata"
)

# 3. Execute the merge
# Passing a list of layers means the functions above receive lists of values.
merged_layer = layer_ops.process([layer1, layer4], default_values={'score': 0})

# 3.5 Set every technique to enabled
layer_dict = merged_layer.to_dict()
for technique in layer_dict.get('techniques', []):
    technique['enabled'] = True

# Update the layer with the modified data
merged_layer.from_dict(layer_dict)

# 4. Harmonize the gradient
# Now that we have a merged layer with new scores, set a unified gradient.
merged_layer.gradient = {
    "colors": ["#ffffffff", "#ffe166ff", "#a9ff66ff", "#8ec843ff"],
    "minValue": 0,
    "maxValue": 5
}

# 5. Save the result
merged_layer.to_file("merged_layers.json")
print("The layers are now merged!")