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

# Now make sure the debug buildType actually USES signingConfigs.debug.
# Capacitor's generated build.gradle often only defines "release { ... }"
# inside buildTypes, with no explicit "debug { ... }" block at all (Gradle
# creates an implicit debug buildType on its own). If that's the case, we
# must add our own explicit "debug { ... }" block, not just try to patch
# one that doesn't exist.
buildtypes_marker = "buildTypes {\n"
bt_idx = content.find(buildtypes_marker)
if bt_idx != -1 and "signingConfig signingConfigs.debug" not in content:
    # Find the "debug {" sub-block *inside* buildTypes, if any. We search only
    # within the buildTypes { ... } region by tracking brace depth so we don't
    # accidentally match "debug {" appearing elsewhere (e.g. our own new
    # signingConfigs block, which sits *before* buildTypes so it's excluded
    # anyway since we search starting at bt_idx).
    search_start = bt_idx + len(buildtypes_marker)
    debug_block_idx = content.find("debug {", search_start)

    # Only trust this match if it's still inside the buildTypes { ... } block.
    # Do a naive brace-depth scan from search_start to confirm.
    inside_buildtypes = False
    if debug_block_idx != -1:
        depth = 1  # we're already inside buildTypes { at search_start
        i = search_start
        while i < debug_block_idx:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        inside_buildtypes = depth > 0

    if debug_block_idx != -1 and inside_buildtypes:
        insert_point = debug_block_idx + len("debug {\n")
        content = (
            content[:insert_point]
            + "            signingConfig signingConfigs.debug\n"
            + content[insert_point:]
        )
    else:
        # No explicit debug buildType exists yet -- add one.
        new_debug_block = (
            "        debug {\n"
            "            signingConfig signingConfigs.debug\n"
            "        }\n"
        )
        content = (
            content[:search_start]
            + new_debug_block
            + content[search_start:]
        )

with open(path, "w") as f:
    f.write(content)

print("Patched", path)
