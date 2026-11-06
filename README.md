# flash_net

A terminal flashcard game for studying the acronyms on the CompTIA Network+ exam.
It shows an acronym and you type the long form:

```
Wi-Fi: wireless fidelity
Correct!
BGP: border routing protocol
Wrong: Border Gateway Protocol
```

Each acronym comes up once, in random order. Case, spacing and punctuation don't
matter when checking answers. Press Ctrl-D or Ctrl-C to stop early and see your score.

## Running it

You need [uv](https://docs.astral.sh/uv/).

```sh
uv run flash-net
```

To use your own list:

```sh
uv run flash-net --file my_acronyms.yaml
```

## Adding acronyms

The default list is in `src/flash_net/acronyms.yaml`:

```yaml
- name: "DNS"
  answers:
    - "Domain Name System"
    - "Domain Name Service"
```

Any listed answer is accepted, and the first one is shown after a wrong guess.
Keep names quoted, because YAML reads an unquoted `NO` or `ON` as a boolean.

## Tests

```sh
uv run pytest
```

## License

MIT. See [LICENSE](LICENSE).
