# latex-scripts

This repo contains some scripts I wrote to make my life easier.

(They might have been done before, I don't care)

## `package.py`

Bundles a latex file and all its dependencies into a minimal zip package.

```sh
python package.py output_dir input_dir root_file output_dir
```

e.g.

```sh
python package.py lics2023 main-conference lics2023-conference
```
