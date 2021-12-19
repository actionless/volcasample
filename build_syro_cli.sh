#!/usr/bin/env bash
set -ueo pipefail

BUILD_DIR=syro_build
SYRO_EXECUTABLE=syro

mkdir "$BUILD_DIR"
cp syro/* "$BUILD_DIR"/
cp example/korg_syro_volcasample_example.c "$BUILD_DIR"/

cd "$BUILD_DIR"
cc -c *.c
cc -o "$SYRO_EXECUTABLE" *.o
