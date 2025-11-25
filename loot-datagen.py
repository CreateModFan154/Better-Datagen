import os
import re
import json

# === SETTINGS ===
MODID = "your-modid"
JAVA_SOURCE = r"path\to\src\main\java\domain\yourname\mod"
OUTPUT_ASSETS = r"path\to\src\main\resources\assets"

# === TEMPLATES ===
LOOT_TABLE_TEMPLATE = lambda name: {
    "type": "minecraft:block",
    "pools": [
        {
            "rolls": 1,
            "entries": [{"type": "minecraft:item", "name": f"{MODID}:{name}"}],
        }
    ],
}

# === FUNCTIONS ===
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def find_registry_names(java_file):
    """Extract registered block names from a Java file."""
    pattern = r'register\("([a-z0-9_]+)"'
    with open(java_file, "r", encoding="utf-8") as f:
        content = f.read()
    return re.findall(pattern, content)

# === SCAN JAVA FILES ===
all_entries = set()
for root, _, files in os.walk(JAVA_SOURCE):
    for file in files:
        if file.endswith(".java"):
            path = os.path.join(root, file)
            names = find_registry_names(path)
            all_entries.update(names)

print(f"Found {len(all_entries)} entries in Java source.")

# === GENERATE LOOT AND TAGS (BLOCKS ONLY) ===
for name in all_entries:
    # Check if block texture exists, skip items
    block_texture = os.path.join(OUTPUT_ASSETS, f"textures/block/{name}.png")
    if not os.path.exists(block_texture):
        print(f"[SKIP] {name} is treated as an item or has no block texture.")
        continue

    loot_path = os.path.join(OUTPUT_ASSETS, f"data/{MODID}/loot_tables/blocks/{name}.json")
    unbreakable_path = os.path.join(OUTPUT_ASSETS, f"data/{MODID}/tags/blocks/unbreakable.json")

    # Skip if loot table already exists
    if os.path.exists(loot_path):
        print(f"[SKIP] {name} already has a loot table.")
        continue

    # Skip if marked unbreakable
    if os.path.exists(unbreakable_path):
        with open(unbreakable_path, "r", encoding="utf-8") as f:
            unbreakable_json = json.load(f)
        if f"{MODID}:{name}" in unbreakable_json.get("values", []):
            print(f"[SKIP] {name} is unbreakable.")
            continue

    print(f"\nProcessing block: {name}")
    write_json(loot_path, LOOT_TABLE_TEMPLATE(name))
    print(f"  -> Loot table created at {loot_path}")

    # Tool & tier with confirmation
    while True:
        tool = input(f"  Tool for {name} (pickaxe/shovel/axe/hand): ").strip().lower()
        tier = input(f"  Tier for {name} (wood/stone/iron/diamond/netherite/none): ").strip().lower()
        confirm = input(f"  You entered Tool='{tool}', Tier='{tier}'. Correct? (y/n): ").strip().lower()
        if confirm == "y":
            break
        print("  -> Let's try again.")

    # Mineable tag
    tag_folder = os.path.join(OUTPUT_ASSETS, f"data/{MODID}/tags/blocks")
    os.makedirs(tag_folder, exist_ok=True)
    mineable_path = os.path.join(tag_folder, f"mineable_{tool}.json")
    if os.path.exists(mineable_path):
        with open(mineable_path, "r", encoding="utf-8") as f:
            tag_json = json.load(f)
        if f"{MODID}:{name}" not in tag_json["values"]:
            tag_json["values"].append(f"{MODID}:{name}")
    else:
        tag_json = {"replace": False, "values": [f"{MODID}:{name}"]}
    write_json(mineable_path, tag_json)
    print(f"  -> Mineable tag updated: mineable_{tool}.json")

    # Needs tier
    if tier != "none":
        tier_path = os.path.join(tag_folder, f"needs_{tier}_tool.json")
        if os.path.exists(tier_path):
            with open(tier_path, "r", encoding="utf-8") as f:
                tier_json = json.load(f)
            if f"{MODID}:{name}" not in tier_json["values"]:
                tier_json["values"].append(f"{MODID}:{name}")
        else:
            tier_json = {"replace": False, "values": [f"{MODID}:{name}"]}
        write_json(tier_path, tier_json)
        print(f"  -> Tier tag updated: needs_{tier}_tool.json")

print("\nAll done! Loot tables and minable tags generated for blocks only.")
