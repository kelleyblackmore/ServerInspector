@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ ls
README.md            examples            main.py         replit.nix     serverinspect-test.yaml  uv.lock
build_executable.py  generated-icon.png  pyproject.toml  serverinspect  serverinspect.spec
@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ pip install .
Processing /workspaces/ServerInspector
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Requirement already satisfied: click>=8.1.8 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (8.1.8)
Requirement already satisfied: email-validator>=2.2.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (2.2.0)
Requirement already satisfied: flask>=3.1.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (3.1.0)
Requirement already satisfied: flask-sqlalchemy>=3.1.1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (3.1.1)
Requirement already satisfied: gunicorn>=23.0.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (23.0.0)
Requirement already satisfied: jinja2>=3.1.6 in /home/codespace/.local/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (3.1.6)
Requirement already satisfied: paramiko>=3.5.1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (3.5.1)
Requirement already satisfied: psutil>=7.0.0 in /home/codespace/.local/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (7.0.0)
Requirement already satisfied: psycopg2-binary>=2.9.10 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (2.9.10)
Requirement already satisfied: pyinstaller>=6.12.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (6.12.0)
Requirement already satisfied: pyyaml>=6.0.2 in /home/codespace/.local/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (6.0.2)
Requirement already satisfied: rich>=14.0.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from repl-nix-workspace==0.1.0) (14.0.0)
Requirement already satisfied: dnspython>=2.0.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from email-validator>=2.2.0->repl-nix-workspace==0.1.0) (2.7.0)
Requirement already satisfied: idna>=2.0.0 in /home/codespace/.local/lib/python3.12/site-packages (from email-validator>=2.2.0->repl-nix-workspace==0.1.0) (3.10)
Requirement already satisfied: Werkzeug>=3.1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from flask>=3.1.0->repl-nix-workspace==0.1.0) (3.1.3)
Requirement already satisfied: itsdangerous>=2.2 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from flask>=3.1.0->repl-nix-workspace==0.1.0) (2.2.0)
Requirement already satisfied: blinker>=1.9 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from flask>=3.1.0->repl-nix-workspace==0.1.0) (1.9.0)
Requirement already satisfied: sqlalchemy>=2.0.16 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from flask-sqlalchemy>=3.1.1->repl-nix-workspace==0.1.0) (2.0.40)
Requirement already satisfied: packaging in /home/codespace/.local/lib/python3.12/site-packages (from gunicorn>=23.0.0->repl-nix-workspace==0.1.0) (24.2)
Requirement already satisfied: MarkupSafe>=2.0 in /home/codespace/.local/lib/python3.12/site-packages (from jinja2>=3.1.6->repl-nix-workspace==0.1.0) (3.0.2)
Requirement already satisfied: bcrypt>=3.2 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from paramiko>=3.5.1->repl-nix-workspace==0.1.0) (4.3.0)
Requirement already satisfied: cryptography>=3.3 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from paramiko>=3.5.1->repl-nix-workspace==0.1.0) (44.0.2)
Requirement already satisfied: pynacl>=1.5 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from paramiko>=3.5.1->repl-nix-workspace==0.1.0) (1.5.0)
Requirement already satisfied: setuptools>=42.0.0 in /home/codespace/.local/lib/python3.12/site-packages (from pyinstaller>=6.12.0->repl-nix-workspace==0.1.0) (76.0.0)
Requirement already satisfied: altgraph in /usr/local/python/3.12.1/lib/python3.12/site-packages (from pyinstaller>=6.12.0->repl-nix-workspace==0.1.0) (0.17.4)
Requirement already satisfied: pyinstaller-hooks-contrib>=2025.1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from pyinstaller>=6.12.0->repl-nix-workspace==0.1.0) (2025.2)
Requirement already satisfied: markdown-it-py>=2.2.0 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from rich>=14.0.0->repl-nix-workspace==0.1.0) (3.0.0)
Requirement already satisfied: pygments<3.0.0,>=2.13.0 in /home/codespace/.local/lib/python3.12/site-packages (from rich>=14.0.0->repl-nix-workspace==0.1.0) (2.19.1)
Requirement already satisfied: cffi>=1.12 in /home/codespace/.local/lib/python3.12/site-packages (from cryptography>=3.3->paramiko>=3.5.1->repl-nix-workspace==0.1.0) (1.17.1)
Requirement already satisfied: mdurl~=0.1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from markdown-it-py>=2.2.0->rich>=14.0.0->repl-nix-workspace==0.1.0) (0.1.2)
Requirement already satisfied: greenlet>=1 in /usr/local/python/3.12.1/lib/python3.12/site-packages (from sqlalchemy>=2.0.16->flask-sqlalchemy>=3.1.1->repl-nix-workspace==0.1.0) (3.1.1)
Requirement already satisfied: typing-extensions>=4.6.0 in /home/codespace/.local/lib/python3.12/site-packages (from sqlalchemy>=2.0.16->flask-sqlalchemy>=3.1.1->repl-nix-workspace==0.1.0) (4.12.2)
Requirement already satisfied: pycparser in /home/codespace/.local/lib/python3.12/site-packages (from cffi>=1.12->cryptography>=3.3->paramiko>=3.5.1->repl-nix-workspace==0.1.0) (2.22)
Building wheels for collected packages: repl-nix-workspace
  Building wheel for repl-nix-workspace (pyproject.toml) ... done
  Created wheel for repl-nix-workspace: filename=repl_nix_workspace-0.1.0-py3-none-any.whl size=27880 sha256=9911f2a28eb83a0f5d43c5b388b3d629d105ebea6fdcf2178f5017dfe30159c3
  Stored in directory: /tmp/pip-ephem-wheel-cache-930bmo21/wheels/cf/21/d6/331acdff98b00757c960e97dbe9f67214c9d207bea009fdfb1
Successfully built repl-nix-workspace
Installing collected packages: repl-nix-workspace
  Attempting uninstall: repl-nix-workspace
    Found existing installation: repl-nix-workspace 0.1.0
    Uninstalling repl-nix-workspace-0.1.0:
      Successfully uninstalled repl-nix-workspace-0.1.0
Successfully installed repl-nix-workspace-0.1.0
@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ ll
total 1356
drwxrwxrwx+ 9 codespace root         4096 Apr 11 07:02 ./
drwxr-xrwx+ 5 codespace root         4096 Apr 11 07:01 ../
drwxrwxrwx+ 2 codespace root         4096 Apr 11 07:01 .devcontainer/
drwxrwxrwx+ 9 codespace root         4096 Apr 11 07:02 .git/
drwxrwxrwx+ 3 codespace root         4096 Apr 11 07:01 .github/
-rw-rw-rw-  1 codespace root         1078 Apr 11 07:01 .replit
-rw-rw-rw-  1 codespace root         3265 Apr 11 07:03 README.md
drwxrwxrwx+ 4 codespace codespace    4096 Apr 11 07:02 build/
-rwxrwxrwx  1 codespace root         1679 Apr 11 07:01 build_executable.py*
drwxrwxrwx+ 2 codespace root         4096 Apr 11 07:01 examples/
-rw-rw-rw-  1 codespace root      1211271 Apr 11 07:01 generated-icon.png
-rw-rw-rw-  1 codespace root          289 Apr 11 07:01 main.py
-rw-rw-rw-  1 codespace root          433 Apr 11 07:01 pyproject.toml
drwxrwxrwx+ 2 codespace codespace    4096 Apr 11 07:03 repl_nix_workspace.egg-info/
-rw-rw-rw-  1 codespace root           82 Apr 11 07:01 replit.nix
drwxrwxrwx+ 7 codespace root         4096 Apr 11 07:01 serverinspect/
-rw-rw-rw-  1 codespace root          693 Apr 11 07:01 serverinspect-test.yaml
-rw-rw-rw-  1 codespace root         1088 Apr 11 07:01 serverinspect.spec
-rw-rw-rw-  1 codespace root       106045 Apr 11 07:01 uv.lock
@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ python3 build_executable.py 
Building ServerInspect executable...
Detected platform: linux
Error during build:
222 INFO: PyInstaller: 6.12.0, contrib hooks: 2025.2
223 INFO: Python: 3.12.1
224 INFO: Platform: Linux-6.8.0-1021-azure-x86_64-with-glibc2.31
224 INFO: Python environment: /usr/local/python/3.12.1
228 INFO: Removing temporary files and cleaning cache in /home/codespace/.cache/pyinstaller
229 INFO: Module search paths (PYTHONPATH):
['/usr/local/python/3.12.1/lib/python312.zip',
 '/usr/local/python/3.12.1/lib/python3.12',
 '/usr/local/python/3.12.1/lib/python3.12/lib-dynload',
 '/home/codespace/.local/lib/python3.12/site-packages',
 '/usr/local/python/3.12.1/lib/python3.12/site-packages',
 '/home/codespace/.local/lib/python3.12/site-packages/setuptools/_vendor',
 '/workspaces/ServerInspector']
394 WARNING: discover_hook_directories: Failed to process hook entry point 'EntryPoint(name='hook-dirs', value='rapidfuzz.__pyinstaller:get_hook_dirs', group='pyinstaller40')': AttributeError: module 'rapidfuzz.__pyinstaller' has no attribute 'get_hook_dirs'
728 INFO: Appending 'datas' from .spec
729 INFO: checking Analysis
729 INFO: Building Analysis because Analysis-00.toc is non existent
729 INFO: Running Analysis Analysis-00.toc
729 INFO: Target bytecode optimization level: 0
729 INFO: Initializing module dependency graph...
729 INFO: Initializing module graph hook caches...
738 INFO: Analyzing modules for base_library.zip ...
1647 INFO: Processing standard module hook 'hook-encodings.py' from '/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/hooks'
2170 INFO: Processing standard module hook 'hook-heapq.py' from '/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/hooks'
3317 INFO: Processing standard module hook 'hook-pickle.py' from '/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/hooks'
4590 INFO: Caching module dependency graph...
4630 INFO: Looking for Python shared library...
Traceback (most recent call last):
  File "/home/codespace/.python/current/bin/pyinstaller", line 8, in <module>
    sys.exit(_console_script_run())
             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/__main__.py", line 231, in _console_script_run
    run()
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/__main__.py", line 215, in run
    run_build(pyi_config, spec_file, **vars(args))
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/__main__.py", line 70, in run_build
    PyInstaller.building.build_main.main(pyi_config, spec_file, **kwargs)
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/building/build_main.py", line 1270, in main
    build(specfile, distpath, workpath, clean_build)
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/building/build_main.py", line 1208, in build
    exec(code, spec_namespace)
  File "serverinspect.spec", line 11, in <module>
    a = Analysis(
        ^^^^^^^^^
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/building/build_main.py", line 582, in __init__
    self.__postinit__()
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/building/datastruct.py", line 184, in __postinit__
    self.assemble()
  File "/usr/local/python/3.12.1/lib/python3.12/site-packages/PyInstaller/building/build_main.py", line 685, in assemble
    raise PythonLibraryNotFoundError()
PyInstaller.exceptions.PythonLibraryNotFoundError: Python library not found: libpython3.12.so, libpython3.12.so.1.0
    This means your Python installation does not come with proper shared library files.
    This usually happens due to missing development package, or unsuitable build parameters of the Python installation.

    * On Debian/Ubuntu, you need to install Python development packages:
      * apt-get install python3-dev
      * apt-get install python-dev
    * If you are building Python by yourself, rebuild with `--enable-shared` (or, `--enable-framework` on macOS).


@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ ^C
@kelleyblackmore ➜ /workspaces/ServerInspector (add-github-actions-e51) $ 