#!/usr/bin/env bash

# This script was made by Microsoft Copilot to create a pyproject.toml inside
# each IOC folder, gathering informations from the setup.py file

set -euo pipefail

# ─────── prefixes configurations ─────────
prefixes=(as- si- li- bl-)

# ─────── template of pyproject.toml ───────
TEMPLATE=$(cat << 'EOF'
[build-system]
requires = ["setuptools>=44"]
build-backend = "setuptools.build_meta"

[project]
name = "%PKG_NAME%"
authors = [{ name = "lnls-sirius" } ]
maintainers = [
  {name = "Ana Oliveira", email = "ana.clara@lnls.br"},
  {name = "Ximenes Resende", email = "xresende@gmail.com"},
  {name = "Fernando H. de Sá", email = "fernandohds564@gmail.com"},
  {name = "Murilo Barbosa Alves", email = "alvesb.murilo@gmail.com"}
]
description = "%DESCRIPTION%"
readme = "README.md"
dynamic = ["version", "dependencies"]
requires-python = ">=3.6"
classifiers = [
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering",
]
keywords = ["SIRIUS", "python", "EPICS"]

license = "GPL-3.0"
license-files= [ "LICENSE", ]

[project.urls]
Homepage   = "https://github.com/lnls-sirius/machine-applications"
Download   = "https://github.com/lnls-sirius/machine-applications"
Repository = "https://github.com/lnls-sirius/machine-applications.git"
Issues     = "https://github.com/lnls-sirius/machine-applications/issues"

# --- Setuptools specific configurations ---
[tool.setuptools]
include-package-data = true
# NOTE: This is not the standard way of defining scripts.
#     Once we abandon phython3.6 and the setup.py file, we should
#     consider using the table [projec.scripts], defining valid entrypoints.
script-files = [
%SCRIPTS%
]

[tool.setuptools.dynamic]
version      = { file = "VERSION" }
dependencies = { file = "requirements.txt" }

[tool.setuptools.package-data]
%PKG_NAME% = [%PACKAGE_DATA%]

# --- linter e formatter ---
[tool.ruff]
select = ["W","E","A","B","C90","D","I002","N","F","G","ARG","S","NPY"]
ignore = ["D203","D204","D213","D215","D400","D401","D404","D406",
          "D407","D408","D409","D413","E203","E226"]
ignore-init-module-imports = true
preview = true
line-length = 79
fix = true

[tool.ruff.extend-per-file-ignores]
"__init__.py" = ["F401","F821"]

[tool.ruff.format]
skip-magic-trailing-comma = true

[tool.ruff.lint.isort]
split-on-trailing-comma = false
combine-as-imports      = true

[tool.isort]
split_on_trailing_comma = false
combine_as_imports      = true
combine_star            = true
multi_line_output       = "HANGING_INDENT"
order_by_type           = false

[tool.black]
line-length = 79
EOF
)

# ─────── loop over IOC packages ────────────────
for prefix in "${prefixes[@]}"; do
  for dir in ${prefix}*; do
    [ -d "$dir" ] || continue
    echo "=> processing $dir"

    # 1) pkg_name = folder name with - → _
    pkg_name=$(basename "$dir" | tr '-' '_')

    # 2) run setup.py under a fake setuptools.setup()
    PYCODE=$(cat << EOF
import setuptools, sys
data = {}
# override of setuptools.setup
def fake_setup(**kwargs):
    data.update(kwargs)
setuptools.setup = fake_setup
# execute setup.py
exec(open("$dir/setup.py").read(), {})
# formatted output
import json
out = {
  "description": data.get("description",""),
  "scripts":      data.get("scripts", []),
  "package_data": data.get("package_data", {}).get("$pkg_name", [])
}
print(json.dumps(out))
EOF
    )

    info_json=$(python3 -c "$PYCODE")

    # 3) extract description, scripts, package_data
    description=$(echo "$info_json"    |
      python3 -c 'import sys, json; print(json.load(sys.stdin)["description"])'
    )
    # create array TOML items
    scripts=$(echo "$info_json"        |
      python3 -c 'import sys, json;
arr = json.load(sys.stdin)["scripts"];
print("\n".join(f"    \"{s}\"," for s in arr))'
    )
    package_data=$(echo "$info_json"   |
      python3 -c 'import sys, json;
arr = json.load(sys.stdin)["package_data"];
print("\n".join(f" \"{s}\"," for s in arr))'
    )

    # 4) fill the template
    out="$TEMPLATE"
    out="${out//%PKG_NAME%/$pkg_name}"
    out="${out//%DESCRIPTION%/$description}"
    out="${out//%SCRIPTS%/$scripts}"
    out="${out//%PACKAGE_DATA%/$package_data}"

    # save pyproject.toml inside the folder
    echo "$out" > "$dir/pyproject.toml"
    echo "  -> $dir/pyproject.toml created"
  done
done

echo "✔️  All pyproject.toml were updated."
