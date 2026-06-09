#!/bin/bash
MODEL_DIR=\${1:-"models/"}
if [ ! -d "\$MODEL_DIR" ]; then return 0 2>/dev/null || true; fi
pushd "\$MODEL_DIR" > /dev/null
ls -1t *.pt 2>/dev/null | tail -n +4 | xargs -r rm
popd > /dev/null
