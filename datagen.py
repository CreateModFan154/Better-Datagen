import os
import re
import json

# === SETTINGS ===
MODID = "your-modid"
JAVA_SOURCE = r"path\to\src\main\java\domain\yourname\mod"
OUTPUT_ASSETS = r"path\to\src\main\resources\assets\mod"

 # === TEMPLATES ===

BLOCKSTATE_TEMPLATE = lambda name: {
    "variants": {
        "": {"model": f"{MODID}:block/{name}"}
     }
}

BLOCK_MODEL_TEMPLATE = lambda name: {
    "parent": "minecraft:block/cube_all",
    "textures": {
        "all": f"{MODID}:block/{name}"
    }
}

ITEM_BLOCK_MODEL_TEMPLATE = lambda name: {
    "parent": f"{MODID}:block/{name}"
 }

ITEM_SIMPLE_MODEL_TEMPLATE = lambda name: {
    "parent": "minecraft:item/generated",
    "textures": {
        "layer0": f"{MODID}:item/{name}"
    }
}

# === SCAN JAVA FILES ===

def find_registry_names(java_file):
    pattern = r'register\("([a-z0-9_]+)"'
    with open(java_file, "r", encoding="utf-8") as f:
        content = f.read()
    return re.findall(pattern, content)


all_entries = set()

for root, _, files in os.walk(JAVA_SOURCE):
    for file in files:
        if file.endswith(".java"):
            path = os.path.join(root, file)
            names = find_registry_names(path)
            all_entries.update(names)

print(f"Found {len(all_entries)} registry entries:")
  or e in all_entries:
    print(" -", e)


# === GENERATE JSON ===

    def write_json(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


    for name in all_entries:
        # Paths
        blockstate = os.path.join(OUTPUT_ASSETS, "blockstates", f"{name}.json")
        block_model = os.path.join(OUTPUT_ASSETS, "models", "block", f"{name}.json")
        item_model = os.path.join(OUTPUT_ASSETS, "models", "item", f"{name}.json")

        # Blockstate + block model (assume it's a block if texture EXISTS)
        tex_path = os.path.join(OUTPUT_ASSETS, "textures", "block", f"{name}.png")
        if os.path.exists(tex_path):
            print(f"[BLOCK] {name}")
            write_json(blockstate, BLOCKSTATE_TEMPLATE(name))
            write_json(block_model, BLOCK_MODEL_TEMPLATE(name))
            write_json(item_model, ITEM_BLOCK_MODEL_TEMPLATE(name))
            continue

        # Otherwise treat it as an item
        tex_path_item = os.path.join(OUTPUT_ASSETS, "textures", "item", f"{name}.png")
        if os.path.exists(tex_path_item):
            print(f"[ITEM] {name}")
            write_json(item_model, ITEM_SIMPLE_MODEL_TEMPLATE(name))
            continue

        print(f"[WARN] No texture found for {name}, skipping!")
