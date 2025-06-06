#!/usr/bin/env python3

import os
import sys

if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception('invalid number of arguments!')
        sys.exit(1)

    project_path = sys.argv[1]
    project = project_path.split(os.pathsep)[-1]
    pyproject = project.replace('-', '_')
    if os.path.exists(project_path):
        raise Exception('directory already exists!')

    os.system('cp -rf --preserve=mode project-name ' + project_path)
    os.rename(
        os.path.join(project_path, 'py_project_name'),
        os.path.join(project_path, pyproject)
    )

    os.chdir(project_path)
    for fil in os.listdir():
        if not os.path.isfile(fil):
            continue
        os.system(f"sed -i 's/py_project_name/{pyproject}/g' {fil}")
        os.system(f"sed -i 's/project-name/{project}/g' {fil}")

    # TODO: Continue here.

    path = os.path.join(project_path, pyproject, 'scripts')
    os.rename(
        os.path.join(path, 'py_project_name.py'),
        os.path.join(path, pyproject+'.py')
    )
    path = os.path.join(project_path, 'scripts')
    os.rename(
        os.path.join(path, 'sirius-ioc-project-name.py'),
        os.path.join(path, f'sirius-ioc-{project}.py')
    )

    os.system(
        'cd ' + project +
        f"; sed -i 's/py_project_name/{pyproject}/g' pyproject.toml"
    )
    os.system(
        'cd ' + project +
        f"; sed -i 's/py_project_name/{pyproject}/g' setup.py"
    )
    os.system(
        'cd ' + project +
        f"; sed -i 's/py_project_name/{pyproject}/g' MANIFEST.in"
    )
