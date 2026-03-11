# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Environment setup

First we recommend you use a unix based system, for example: `wsl`if you are using windows.

Nothing easier!

Fork and clone the repository, then:

```bash
cd <repo-directory>
make setup
```

> NOTE: If it fails for some reason, you'll need to install [uv](https://github.com/astral-sh/uv) manually.
>
> You can install it with:
>
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
>
> Now you can try running `make setup` again, or simply `uv sync`.

You now have the dependencies installed.

You can run the application with `make run puzzletree [ARGS...]`.

Run `make help` to see all the available actions!

## Tasks

The entry-point to run commands and tasks is the `make` Python script, located in the `scripts` directory. Try running `make` to show the available commands and tasks. The *commands* do not need the Python dependencies to be installed,
while the *tasks* do. The cross-platform tasks are written in Python, thanks to [duty](https://github.com/pawamoy/duty).

If you work in Cursor or VS Code, run `make setup-ide` to copy Cursor and VS Code config from `config/` to `.cursor/` and `.vscode/`.

## Development

As usual:

1. create a new branch: `git switch -c feature-or-bugfix-name`
1. edit the code and/or the documentation

**Before committing:**

1. run `make format` to auto-format the code
1. run `make check` to check everything (fix any warning)
1. run `make test` to run the tests (fix any issue)
1. if you updated the documentation or the project dependencies:
    1. run `make docs`
    1. go to http://localhost:8000 and check that everything looks good
1. follow our [commit message convention](#commit-message-convention)

If you are unsure about how to fix or ignore a warning, just let the continuous integration fail, and we will help you during review.

Don't bother updating the changelog, we will take care of this.

## Docker images

This project uses a consistent Docker image tagging and naming scheme.

### Image tag resolution

When building images, the tag is resolved as:

- If the current commit (`HEAD`) is *exactly* tagged in git with a semantic version tag (for example `v1.2.3`), that tag is used.
- Otherwise, the tag falls back to `<version>-<short-sha>`.

The fallback prefix comes from the Makefile `version` variable.

In CI, the build can also pick up `CI_COMMIT_TAG` / `CI_COMMIT_SHORT_SHA` if your provider exposes them.

### Image naming variables

The Makefile keeps the image naming deliberately simple:

- `docker.image` is the basename: `puzzletree`
- `docker.image.base` is the base/testing image name: `puzzletree_base`
- `docker.image.deploy` is the workflow-specific deployment image name: `puzzletree_<workflow>`

To build or reference a workflow-specific deployment image, pass `workflow=<name>` (for example `workflow=sealant`).

### Common commands

Build the base image (using the resolved image tag):

```bash
make docker-build
```

Run the release task inside the base image:

```bash
make docker-test
```

Open an interactive shell in the base image:

```bash
make docker-env
```

If you add deployment-specific build targets, prefer using `${docker.image.deploy}:${image.tag}` and pass `workflow=<name>` so the image name encodes which workflow it belongs to.


## Commit message convention

Commit messages must follow our convention based on the [Angular style](https://gist.github.com/stephenparish/9941e89d80e2bc58a153#format-of-the-commit-message) or the [Karma convention](https://karma-runner.github.io/4.0/dev/git-commit-msg.html):

```
<type>[(scope)]: Subject

[Body]
```

**Subject and body must be valid Markdown.** Subject must have proper casing (uppercase for first letter if it makes sense), but no dot at the end, and no punctuation in general.

Scope and body are optional. Type can be:

- `build`: About packaging, building wheels, etc.
- `chore`: About packaging or repo/files management.
- `ci`: About Continuous Integration.
- `deps`: Dependencies update.
- `docs`: About documentation.
- `feat`: New feature.
- `fix`: Bug fix.
- `perf`: About performance.
- `refactor`: Changes that are not features or bug fixes.
- `style`: A change in code style/format.
- `tests`: About tests.

If you write a body, please add trailers at the end (for example issues and PR references, or co-authors), without relying on GitHub's flavored Markdown:

```
Body.

Issue #10: https://github.com/namespace/project/issues/10
Related to PR namespace/other-project#15: https://github.com/namespace/other-project/pull/15
```

These "trailers" must appear at the end of the body, without any blank lines between them. The trailer title can contain any character except colons `:`. We expect a full URI for each trailer, not just GitHub autolinks (for example, full GitHub URLs for commits and issues, not the hash or the #issue-number).

We do not enforce a line length on commit messages summary and body, but please avoid very long summaries, and very long lines in the body, unless they are part of code blocks that must not be wrapped.

## Pull requests guidelines

Link to any related issue in the Pull Request message.

Please review our [AI Usage Policy](AI_POLICY.md) before submitting pull requests, especially if AI tools were used.

During the review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash main
```

And force-push:

```bash
git push -f
```

If this seems all too complicated, you can push or force-push each new commit, and we will squash them ourselves if needed, before merging.
