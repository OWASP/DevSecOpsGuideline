# Fuzz Testing

Fuzz testing (fuzzing) feeds a program large numbers of generated, malformed, or unexpected inputs and watches for crashes, hangs, memory errors, and broken invariants. Modern fuzzers are **coverage-guided**: they instrument the code, keep the inputs that reach new branches, and mutate those further. This lets them find bugs deep in parsers and decoders that hand-written tests and scanners never reach.

Fuzzing complements SAST and DAST rather than replacing them. SAST looks for known patterns in code, and DAST probes a running application from the outside. Fuzzing exercises individual functions with inputs nobody thought to write down, which makes it especially good at finding memory-safety bugs, panics, infinite loops, excessive allocation, and logic errors in code that handles untrusted data. Fuzzing found well-known flaws in widely used libraries, and Google's OSS-Fuzz service has reported tens of thousands of bugs in open source projects.

## What to fuzz

Fuzzing pays off most where untrusted input meets complex code. Prioritize:

- **Parsers and decoders** for file formats, network protocols, serialization formats (JSON, YAML, protobuf, XML), compression, and image or media formats.
- **Input validation and normalization** such as URL, path, and email parsing, Unicode handling, and template rendering.
- **Cryptographic and encoding code** such as certificate parsing, ASN.1, base64, and signature verification, where a crash or wrong result can become a security bug.
- **Code written in memory-unsafe languages** (C, C++, and `unsafe` blocks in Rust or Go), where fuzzing combined with sanitizers finds out-of-bounds reads and writes, use-after-free, and integer overflows.
- **Functions with properties you can check**, for example "decode(encode(x)) == x" or "two implementations give the same answer" (differential fuzzing).

For HTTP APIs, schema-based and stateful API fuzzing is covered in [API Security](2-4-4-API-Security.md). This page focuses on in-process, coverage-guided fuzzing of code.

## Writing a fuzz target

A fuzz target (also called a harness) is a small function that takes fuzzer-generated input and passes it to the code under test. Most languages now have a native or widely used framework:

- **Go** has built-in fuzzing since Go 1.18. A fuzz target is a test function in a `_test.go` file:

```go
func FuzzParseHeader(f *testing.F) {
    // Seed corpus: realistic inputs to start from
    f.Add([]byte("Content-Type: text/html"))
    f.Fuzz(func(t *testing.T, data []byte) {
        h, err := ParseHeader(data)
        if err != nil {
            return // rejecting bad input is fine, crashing is not
        }
        // Check an invariant, not just "did it crash"
        if _, err := ParseHeader(h.Bytes()); err != nil {
            t.Fatalf("round trip failed for %q: %v", data, err)
        }
    })
}
```

Run it with `go test -fuzz=FuzzParseHeader -fuzztime=5m`. Failing inputs are saved under `testdata/fuzz/FuzzParseHeader/` and are replayed by a plain `go test`, so every crash becomes a regression test automatically.

- **Rust** uses [cargo-fuzz](https://github.com/rust-fuzz/cargo-fuzz) (libFuzzer based) or [AFL.rs](https://github.com/rust-fuzz/afl.rs).
- **Java and other JVM languages** use [Jazzer](https://github.com/CodeIntelligenceTesting/jazzer), which integrates with JUnit 5 through `@FuzzTest`.
- **Python** uses [Atheris](https://github.com/google/atheris), and **JavaScript and TypeScript** use [Jazzer.js](https://github.com/CodeIntelligenceTesting/jazzer.js).
- **C and C++** use [libFuzzer](https://llvm.org/docs/LibFuzzer.html) or [AFL++](https://github.com/AFLplusplus/AFLplusplus), almost always together with sanitizers such as AddressSanitizer (ASan) and UndefinedBehaviorSanitizer (UBSan). Without a sanitizer, many memory errors do not crash and go unnoticed.

Good targets are fast (thousands of executions per second), deterministic, and free of side effects such as network calls or writes outside a temporary directory. Give each target a seed corpus of realistic inputs, and a dictionary of keywords for text formats, so the fuzzer does not have to discover the format from scratch.

## Fuzzing in CI/CD

Fuzzing needs time to be effective, which does not fit neatly into a pull request pipeline. Most teams split it into two modes:

- **Short fuzzing on pull requests.** Run the fuzz targets affected by the change for a few minutes each, starting from the stored corpus. Fail the build only on new crashes, and report the crashing input so it can be reproduced locally.
- **Long-running continuous fuzzing.** Run the targets for hours on a schedule or a dedicated service, keep and minimize the corpus between runs, and track coverage over time. This is where most bugs are found.

Open source projects can apply to [OSS-Fuzz](https://github.com/google/oss-fuzz), which runs continuous fuzzing for free, reports bugs privately, and pairs with CIFuzz for pull request fuzzing. For private code, [ClusterFuzzLite](https://google.github.io/clusterfuzzlite/) runs the same tooling inside your own CI:

```yaml
# .github/workflows/cflite_pr.yml - fuzz the code changed in a pull request
name: ClusterFuzzLite PR fuzzing
on:
  pull_request:
permissions: read-all
jobs:
  pr-fuzzing:
    runs-on: ubuntu-latest
    steps:
      # Pin actions to a full commit SHA in production
      - name: Build fuzzers
        uses: google/clusterfuzzlite/actions/build_fuzzers@v1
        with:
          language: go
          github-token: ${{ secrets.GITHUB_TOKEN }}
          sanitizer: address
      - name: Run fuzzers
        uses: google/clusterfuzzlite/actions/run_fuzzers@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          fuzz-seconds: 300
          mode: code-change
          sanitizer: address
```

ClusterFuzzLite reads its build steps from a `.clusterfuzzlite/` directory (a `project.yaml`, `Dockerfile`, and `build.sh`) and also supports batch fuzzing, corpus pruning, and coverage reports on a schedule.

## Handling findings

- **Reproduce and minimize.** Every fuzzer can replay a crashing input, and most can minimize it to the smallest input that still fails. Attach both to the ticket.
- **Deduplicate.** One bug often produces many crashing inputs. Group crashes by stack trace before triaging.
- **Triage for security impact.** A panic in a request handler can be a denial of service, and a sanitizer report of a heap overflow can be remote code execution. Route security-relevant crashes through the [vulnerability management](../2-7-Operate/2-7-4-Vulnerability-Management.md) process rather than the normal bug queue.
- **Keep the crashing input as a regression test.** Add it to the seed corpus or the unit tests so the bug cannot quietly come back.

## Common pitfalls and anti-patterns

- **Fuzzing without sanitizers in C and C++.** Many memory errors only corrupt state silently. Build fuzz targets with ASan and UBSan, and use MSan for uninitialized reads.
- **Only checking for crashes.** A target that never asserts anything misses logic bugs. Add invariants such as round trips, length limits, or comparison against a reference implementation.
- **Throwing away the corpus.** Starting from zero on every run wastes most of the fuzzing time. Store the corpus as a build artifact or in a bucket and minimize it periodically.
- **Slow or flaky targets.** Network calls, global state, and random seeds outside the fuzzer's control make results irreproducible and drop throughput.
- **Blocking pull requests on old crashes.** Pull request fuzzing should block only on crashes the change introduced. Known crashes belong in the backlog with an owner.
- **Treating fuzzing as a one-time exercise.** Code changes constantly, and new paths need new fuzzing. Continuous fuzzing finds bugs that a one-week campaign never reaches.

## Maturity progression

**Starter** - Write fuzz targets for the two or three parsers that handle the most untrusted input. Run them locally and in a nightly CI job. Commit crashing inputs as regression tests.

**Intermediate** - Run short coverage-guided fuzzing on every pull request that touches fuzzed code. Persist and minimize the corpus between runs. Build C and C++ targets with sanitizers. Open source projects join OSS-Fuzz.

**Advanced** - Continuous fuzzing covers every component that parses untrusted input, with coverage tracked per target. New parsers are not merged without a fuzz target. Differential and property-based fuzz targets check correctness, not just crashes. Fuzzing findings feed the vulnerability management process with SLAs.

## Metrics and KPIs

- **Fuzz target coverage of the attack surface** - share of parsers and input handlers that have a fuzz target.
- **Code coverage reached by fuzzing** - per target, tracked over time; a flat line usually means the fuzzer is stuck.
- **Executions per second** - per target; a sudden drop points to a slow code path or a broken harness.
- **Open fuzzing crashes and mean time to fix** - split by security impact.
- **Crashes reintroduced** - should be zero once crashing inputs are kept as regression tests.

---

## Tools[^1]

### Open-source

- [AFL++](https://github.com/AFLplusplus/AFLplusplus) - Community-maintained successor of AFL with many mutation strategies and instrumentation modes; also fuzzes binaries without source through QEMU and other modes.
- [Atheris](https://github.com/google/atheris) - Coverage-guided fuzzer for Python code and native extensions.
- [cargo-fuzz](https://github.com/rust-fuzz/cargo-fuzz) - Cargo subcommand for libFuzzer-based fuzzing of Rust crates.
- [ClusterFuzzLite](https://github.com/google/clusterfuzzlite) - Runs OSS-Fuzz style fuzzing in your own CI (GitHub Actions, GitLab, Google Cloud Build, Prow) for pull request and batch fuzzing.
- [Go fuzzing](https://go.dev/doc/security/fuzz/) - Native coverage-guided fuzzing built into `go test` since Go 1.18.
- [Jazzer](https://github.com/CodeIntelligenceTesting/jazzer) - Coverage-guided fuzzing for the JVM with JUnit 5 integration and detectors for injection and deserialization bugs.
- [Jazzer.js](https://github.com/CodeIntelligenceTesting/jazzer.js) - Coverage-guided fuzzing for Node.js with Jest integration.
- [libFuzzer](https://llvm.org/docs/LibFuzzer.html) - In-process, coverage-guided fuzzing engine built into LLVM/Clang; the engine behind many other tools.
- [OSS-Fuzz](https://github.com/google/oss-fuzz) - Free continuous fuzzing service from Google for critical open source projects, with private bug reporting and coverage dashboards.

### Commercial

- [CI Fuzz](https://www.code-intelligence.com/) - Code Intelligence's platform built on Jazzer and libFuzzer, with IDE and CI integration and fuzzing for Java, C/C++, and JavaScript.
- [Mayhem](https://www.mayhem.security/) - Fuzzing platform for code, binaries, and APIs, with automatic triage and CI integration.

---

### Links

- [Go: Fuzzing tutorial](https://go.dev/doc/tutorial/fuzz)
- [OSS-Fuzz documentation](https://google.github.io/oss-fuzz/)
- [Google fuzzing documentation and tutorials](https://github.com/google/fuzzing)
- [OpenSSF Scorecard: Fuzzing check](https://github.com/ossf/scorecard/blob/main/docs/checks.md#fuzzing)

[^1]: Listed in alphabetical order.
