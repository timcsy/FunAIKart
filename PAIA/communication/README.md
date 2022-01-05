# gRPC of PAIA Kart Game

## Setup
```
pip install grpcio-tools
```

```
cd path_to_this_README.md_directory
```

```
mkdir -p generated
python -m grpc_tools.protoc -I./protos --python_out=./generated --grpc_python_out=./generated ./protos/*.proto
touch ./generated/__init__.py
```

Edit ./generated/__init__.py
```
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
```