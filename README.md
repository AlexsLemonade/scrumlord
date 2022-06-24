# Continuous administration of the Childhood Cancer Data Lab's electronic scrum
## Summary

This repository automates the management of GitHub issues, which must be opened and closed based on the date.

## Details

The Childhood Cancer Data Lab does an electronic scrum (e-scrum) where lab members create daily task lists using GitHub issues on [`alexslemonade/scrum`](https://github.com/alexslemonade/scrum) (private repository).
To automate the administration of `alexslemonade/scrum` issues, this repository relies on Github Actions daily cron job which closes and opens issues to keep the scrum issues up to date.

## Reuse

Anyone is welcome to adapt this codebase for their use cases.
The repository is openly licensed as per [`LICENSE.md`](LICENSE.md).
