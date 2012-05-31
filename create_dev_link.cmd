mkdir temp
set PYTHONPATH=.\temp
python setup.py build develop --install-dir .\temp
copy .\temp\MoveOnRemove.egg-link %APPDATA%\deluge\plugins
rmdir /S /Q temp
