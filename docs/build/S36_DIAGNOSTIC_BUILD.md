# S36 — Actual Windows EXE packaging proof, deliberately NOT PRODUCT

```text
src/TLMTool.py (unchanged)
  main() -> prints S01 BLOCKED to stderr -> returns 2
    |
    v
GitHub Windows runner, Python 3.10 x64
  compileall and S01–S36 full units PASS
    |
    install requirements-build-s36.txt
      PyInstaller==6.16.0
    |
    PyInstaller --onedir --console, explicit name:
      S36_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT
    |
    artifacts/s36/dist/
      S36_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT/
        S36_DIAGNOSTIC_FAIL_CLOSED_NOT_PRODUCT.exe
        _internal/ (bundled runtime libraries/DLLs)
    |
    S36_VERIFY_STANDALONE.py:
      S28 structural PE AMD64 check
      launch real packaged exe under unrelated temporary cwd,
      no PYTHONPATH/PYTHONHOME,
      attempt 1: no arguments -> return 2 + guard on stderr
      attempt 2: single unsupported argument -> return 2 + guard
      hash exe SHA-256 and write verification JSON
    |
    S35..S10 Windows regressions -> upload one-dir + proof
```

**NOT a TLMTool product:** no Info server, GUI parity, game launch, account actions or Proxy runtime. Do not extract just the EXE without adjacent `_internal`: PyInstaller S36 is `onedir` rather than `onefile`. Same two guard exits cannot prove every possible runtime or auth property.

[S36 real packaging CI SUCCESS](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37919314787) · [Artifact 11610949148](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37919314787/artifacts/11610949148).
