#!/usr/bin/env bash

# This code was done by free version ChatGPT o4.mini in 2025/06/09.

set -e  # Faz o script parar em caso de erro

# check number of arguments.
if [ "$#" -ne 1 ]; then
    echo "invalid number of arguments!" >&2
    exit 1
fi

# argument must be the relative path from this folder to the ioc folder
# preferably the IOC name must be <section>-<discipline>-<name>,
# just like the other existing IOCS.
project_path="$1"
project="$(basename "$project_path")"

# the python project name will be: <section>_<discipline>_<name>:
pyproject="${project//-/_}"

if [ -d "$project_path" ] && [ "$(ls -A "$project_path")" ]; then
    echo "directory already exists and is not empty!" >&2
    exit 1
fi

src_abs_path="$(realpath project-name)"
dest_abs_path="$(realpath "$project_path")"

mkdir -p "$project_path"

# Copy all files, including links (this will break the links):
cp -a "$src_abs_path"/. "$dest_abs_path"/

# Fix relative symbolic links so that they work in the new structure:
find "$dest_abs_path" -type l | while read -r link; do
    target="$(readlink "$link")"
    if [[ "$target" == /* ]]; then
        # If enter here, it means the link has absolute path. nothing to do.
        continue
    fi
    link_dir="$(dirname "$link")"
    abs_target="$(realpath -m "$src_abs_path/$target")"
    new_rel_target="$(realpath --relative-to="$link_dir" "$abs_target")"
    ln -sf "$new_rel_target" "$link"
done

cd "$project_path"

# start changing file names and content of files to the appropriate name.
mv "py_project_name" "$pyproject"

find . -type f ! -xtype l -exec sed -i "s/py_project_name/$pyproject/g" {} +
find . -type f ! -xtype l -exec sed -i "s/project-name/$project/g" {} +

cd "$pyproject"
mv "py_project_name.py" "${pyproject}.py"

cd "../scripts"
mv "sirius-ioc-project-name.py" "sirius-ioc-${project}.py"
