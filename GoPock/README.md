Pocket Booklet version 7

Experiments
1. exConfig.py Try dataclass and config object with inheritance
2. exCanvasFrame.py Demonstrate mixing frames for text processing and a canvas page.

Short note - input shorthand
You can use a compact page specification in `input.txt` for text pages where the
first token is a processor name followed by the filename and an optional path.
Examples:
- `froff text01.txt`
- `recipe rPuertoBeans.txt`
This is equivalent to the longer form:
```
text {
	file=text01.txt
	processor=froff
}
```
