This is a series of implementations of Go, using progressively more advanced
techniques. Big thanks to Leah Hanson for help in writing `go_sets.py`.

To run:
`python3 go_benchmark.py`

To profile:
```
python3 -m flamegraph -o benchmark.prof implementing_go_benchmark.py
flamegraph.pl benchmark.prof > benchmark.svg
```

Flamegraph can be obtained by cloning [Brendan Gregg's repo](https://github.com/brendangregg/FlameGraph)
