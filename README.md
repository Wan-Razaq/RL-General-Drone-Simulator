# General Drone Simulator
## Installation
This project uses !(Poetry)[https://python-poetry.org/] for dependency management. Install poetry and run `poetry install` to install all dependencies. Then run `poetry run python main.py` to run the simulator.

If you don't want to use poetry you can install the dependencies manually using pip. The dependencies are listed in the pyproject.toml file. Then you can start the simulation using `python main.py`.

## Installing pytorch for rocm
```bash
poetry source add --priority=explicit pytorch-gpu-src https://download.pytorch.org/whl/cu118
poetry add --source pytorch-gpu-src torch torchvision torchaudio
```