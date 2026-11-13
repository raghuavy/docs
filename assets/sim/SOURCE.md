# Corresponding Source

This package was built from:

- Repository: https://github.com/AlexMercer12138/iverilog
- Git revision: `75c777c993c2bbc6ffe7f9138f25a76e14db5325`
- Emscripten image: `emscripten/emsdk:6.0.6`

Obtain the complete corresponding source and reproduce the release artifacts
with:

```sh
git clone https://github.com/AlexMercer12138/iverilog
cd iverilog
git checkout --detach 75c777c993c2bbc6ffe7f9138f25a76e14db5325
make -C wasm clean build package
```

The repository and revision above are the complete corresponding source for
the package, including the build scripts used to produce the WebAssembly
artifacts. External VPI is not supported by this build.
