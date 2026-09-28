import sys

path = sys.argv[1]
client_id = sys.argv[2]

with open(path) as f:
    content = f.read()

if "server_client_id" in content:
    print("server_client_id already present, skipping patch:", path)
    sys.exit(0)

new_string = f'    <string name="server_client_id">{client_id}</string>\n'

marker = "<resources>\n"
idx = content.find(marker)
if idx == -1:
    print("ERROR: could not find '<resources>' in", path)
    sys.exit(1)

insert_at = idx + len(marker)
content = content[:insert_at] + new_string + content[insert_at:]

with open(path, "w") as f:
    f.write(content)

print("Patched", path, "with server_client_id")
