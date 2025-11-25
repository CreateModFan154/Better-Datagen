import os
import json

# === SETTINGS ===
MODID = "your-modid"
BLOCKS = [
    "iron_pipe",
    "copper_pipe",
    "lead_block",
]  # Add all blocks you want to generate loot/minable tags for
OUTPUT_ASSETS = r"path\to\src\main\resources"

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

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# === GENERATE LOOT AND TAGS ===
for name in BLOCKS:
    print(f"\nProcessing block: {name}")

    # Loot table
    loot_path = os.path.join(OUTPUT_ASSETS, f"data/{MODID}/loot_tables/blocks/{name}.json")
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

print("\nAll done! Loot tables and minable tags generated.")
