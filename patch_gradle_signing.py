import re
import sys

path = sys.argv[1]
with open(path) as f:
    content = f.read()

if "signingConfigs" in content:
    print("signingConfigs already present, skipping patch:", path)
    sys.exit(0)

signing_block = """    signingConfigs {
        debug {
            storeFile file('debug.keystore')
            storePassword 'android'
            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
    }
"""

marker = "android {\n"
idx = content.find(marker)
if idx == -1:
    print("ERROR: could not find 'android {' in", path)
    sys.exit(1)

insert_at = idx + len(marker)
content = content[:insert_at] + signing_block + content[insert_at:]

# Point the buildTypes.debug block at our signing config, without touching
# the signingConfigs.debug block we just inserted above.
buildtypes_idx = content.find("buildTypes")
if buildtypes_idx != -1 and "signingConfig signingConfigs.debug" not in content:
    debug_block_idx = content.find("debug {", buildtypes_idx)
    if debug_block_idx != -1:
        insert_point = debug_block_idx + len("debug {\n")
        content = (
            content[:insert_point]
            + "            signingConfig signingConfigs.debug\n"
            + content[insert_point:]
        )

with open(path, "w") as f:
    f.write(content)

print("Patched", path)
