# Conventional Commit Message Linter

[`pre-commit`](https://github.com/pre-commit/pre-commit) hook for the `commit-msg` stage, which validates that the
commit message conforms to a modified [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format.

The acceptable format is `type(area[,...])[!]: [{tag}] message`

## Configuration

A `pyproject.toml` will be sought in the repo root, and if found, the following keys will be consulted within the
`conventional-msg` section:

### `min_len`

The `message` component must be at least this long.

- type: `int`
- default: `8`

### `types`

Valid values for the type prefix.

- type: `set[str]`
- default:
  - `chore`
  - `docs`
  - `feat`
  - `fix`
  - `revise`
  - `wip`

### `areas`

Valid values for the area qualifiers.

- type: `set[str]`
- default:
  - `all`
  - `cli`
  - `config`
  - `core`
  - `dev`
  - `lib`
  - `model`
  - `migrations`
  - `tests`
  - `typings`

### `tags`

Valid values for the tag modifier.

- type: `set[str]`
- default:
  - `tests-failing`

### `branch`

Name of the default branch, into which features are expected to merge.

- type: `str`
- default: `master`

### `revise_name`

Name of the prefix for commits which are meant to revise earlier commits.

- type: `str`
- default: `revise`

### `allow_omit_area`

`types` which are allowed to omit an `area` qualifier.

- type: `set[str]`
- default:
    - `docs`
    - `wip`

## Examples

A `feat`ure in the `web` area

```
feat(web): implemented GET /foo/bar
```

A `chore` whose completion broke a test (but we expect to resolve that shortly)

```
chore(lib)!: {tests-failing} redefined pi
```

By default, `docs` type commits don't need to be qualified with an `area`

```
docs: added README
```

We previously checked in a feature incompletely, and now we want to revise that commit

```
revise(abc123): forgot to add config.yaml
```

## Installation

Add to the `repos` list in `.pre-commit-config.yaml`

```
- repo: https://github.com/jessedhillon/conventional-msg
  rev: "0.1.1"
  hooks:
    - id: conventional-msg
      name: conventional commit message
      entry: conventional-msg
      language: python
      stages: [commit-msg]
```

In your repo, make sure to install the `commit-msg` hook specifically, which is not installed by default:

```
pre-commit install --hook-type commit-msg
```
