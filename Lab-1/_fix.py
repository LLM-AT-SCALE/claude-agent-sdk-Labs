import ast
import json

p = "Lab_1.ipynb"
nb = json.load(open(p, encoding="utf-8"))
NL = chr(92) + "n"  # a literal backslash-n, built without any escape sequence

for c in nb["cells"]:
    if c["cell_type"] == "code" and "ERR_NGROK_334" in c["source"]:
        src = c["source"]
        i = src.index("        raise SystemExit(")
        j = src.index("    raise\n", i)
        block = (
            "        raise SystemExit(\n"
            '            "' + NL + "!! Your ngrok endpoint is already in use by an EARLIER session." + NL + '"\n'
            '            "   Go to that other Colab tab and stop its last cell (or Runtime -> Disconnect' + NL + '"\n'
            '            "   and delete runtime), then run this cell again.' + NL + '"\n'
            '            "   Or stop it at dashboard.ngrok.com -> Agents.")\n'
        )
        c["source"] = src[:i] + block + src[j:]
        fixed = c["source"]

json.dump(nb, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
open(p, "a").write("\n")

# prove every code cell parses (magics stripped, top-level await neutralised)
for c in nb["cells"]:
    if c["cell_type"] == "code":
        py = "\n".join(l for l in c["source"].split("\n") if not l.lstrip().startswith(("!", "%")))
        ast.parse(py.replace("await main()", "pass"))
print("every code cell compiles")
k = fixed.index("raise SystemExit(")
print(repr(fixed[k:k+120]))
