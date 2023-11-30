# latex-packager

This is a GitHub Action for compiling a latex project and packaging it into a minimal project, perhaps for uploading onto arXiv or similar.

## Usage

```yml
- name: Package latex project
  uses: georgejkaye/latex-packager@v1.0
  with:
    input-dir: project
    main: main
    project-name: output
    shell-escape: true
```
