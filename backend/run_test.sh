#!/bin/bash

echo -e "Running pylint..."
pylint .

echo -e "\n\nRunning pytest..."
python3 -m pytest

if [ -z ${TYPECHECK+x} ]; then
    echo -e "\n\nSkipping pyright..."
else
    echo -e "\n\nRunning pyright..."
    pyright
fi
