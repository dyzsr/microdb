SET PYTHONPATH="%PYTHONPATH%\;.\"
python3 web/run.py
cd ui && npm run serve -s build
