#!/usr/bin/env bash
# Installs the simulators for the playground. Also works on any Ubuntu 24.04 machine or WSL.
#   Verilator 5.054 and Icarus Verilog 13 from conda-forge, z3 (the constraint solver) from Ubuntu.
set -euo pipefail
PREFIX="${EDA_PREFIX:-/opt/eda}"

echo "Installing z3, make and g++..."
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq z3 make g++ > /dev/null

echo "Installing Verilator and Icarus Verilog into $PREFIX..."
tmp="$(mktemp -d)"
curl -sSL https://conda.anaconda.org/conda-forge/linux-64/micromamba-2.10.0-0.tar.bz2 | tar -xj -C "$tmp" bin/micromamba
sudo mkdir -p "$PREFIX"
sudo chown "$(id -u)" "$PREFIX"
"$tmp/bin/micromamba" create -y -q -r "$tmp/root" -p "$PREFIX" -c conda-forge verilator=5.054 iverilog=13
rm -rf "$tmp"

if ! grep -q "$PREFIX/bin" "$HOME/.bashrc" 2>/dev/null; then
  echo "export PATH=$PREFIX/bin:\$PATH" >> "$HOME/.bashrc"
fi
"$PREFIX/bin/verilator" --version
"$PREFIX/bin/iverilog" -V 2>&1 | head -1
echo "Playground ready. In the terminal:  ./run scratch.sv"
