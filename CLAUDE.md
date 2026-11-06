# flash_net

Terminal flashcard game for CompTIA Network+ acronyms, written in Python and managed with uv.

## Commands

- Run the game: `uv run flash-net`
- Run the tests: `uv run pytest`

## Layout

- `src/flash_net/game.py`: card loading, answer checking, game loop and CLI
- `src/flash_net/acronyms.yaml`: default acronym list
- `tests/test_game.py`: tests

## Conventions

- Write the test first, then the code that makes it pass.
- `play()` takes its input, output and random source as arguments, so tests don't
  need a real terminal. Keep new game logic testable the same way.
- Check that new acronym entries match the CompTIA N10 objectives, since people
  study from this list. Keep names quoted in the YAML.
