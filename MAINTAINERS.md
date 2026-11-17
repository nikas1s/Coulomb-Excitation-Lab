# Maintainer

[@nikas1s](https://github.com/nikas1s) is the primary maintainer and code owner of Coulomb Excitation Lab.

The merge policy for `main` is a pull request with the maintainer's approval. A second reviewer is encouraged, especially for physics, inference and numerical-method changes, but is optional. `.github/CODEOWNERS` assigns the maintainer to every file, including the ownership file and GitHub workflows.

GitHub's required approval count is **one**, with code-owner review required. Setting it to two would make the second review mandatory. Ownership rules are read from the pull request's base branch, so the CODEOWNERS file must be present on `main` before GitHub can enforce the named-owner requirement. See [GitHub's code-owner documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).

GitHub does not let pull-request authors approve their own PRs. Administrator enforcement is disabled so the sole administrator, @nikas1s, retains an explicit override for maintainer-authored changes. Other contributors need the code-owner approval. Additional administrators would also inherit an override, so grant that role deliberately. The configured payload is versioned in `.github/main-protection.json`.

Scientific review checks the model's assumptions, units, signs, sources and validation evidence. A GitHub approval alone does not complete the open research-qualification gates in [the qualification record](docs/RESEARCH_QUALIFICATION.md).

The live rule was configured and verified on 17 November 2026. GitHub reported no CODEOWNERS errors. The ownership bootstrap on `main` is [commit 4fb1ab3](https://github.com/nikas1s/Coulomb-Excitation-Lab/commit/4fb1ab3c3beb2f2ec7c6e5553504e212a9a9e98e); research code was not merged by that action.
