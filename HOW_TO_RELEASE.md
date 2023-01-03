# How to issue a Pyxel release

These instructions assume that `upstream` refers to the main repository:

```fish
$ git remote -v
{...}
upstream	https://gitlab.com/esa/pyxel.git (fetch)
upstream	https://gitlab.com/esa/pyxel.git (push)
```

1. Write a release summary: ~50 words describing the high level features. This will be used in the release emails, GitLab release notes, blog, etc.

1. Ensure your master branch is synced to upstream:

   ```fish
   $ git switch master
   $ git pull upstream master
   ```

1. Create a branch 'new_release{X}.{Y}' from 'master' for the new release.

   ```fish
   $ git checkout -b new_release{X}.{Y}
   ```

1. Open a merge request linked to the new release branch with the release summary and changes.

1. Update release notes in `CHANGELOG.md` in the branch and add release summary at the top.

1. Create a new file `continuous_integration/pyxel-{X}.{Y}-environment.yaml` with updated links

1. Update version `{X}.{Y}` in files: `docs/source/tutorials/overview.rst`

1. After merging, again ensure your master branch is synced to upstream:

   ```fish
   $ git pull upstream master
   ```

1. If you have any doubts, run the full test suite one final time !

   ```fish
   $ pytest

   or

   $ tox
   ```

1. Tag the release from https://gitlab.com/esa/pyxel/-/tags with the following actions:

   a. Click the button 'new_tag'

   b. In the field 'Tag name', enter `{X.Y}`

   c. In the field 'Create from', choose `master` (this is the default value)

   d. In the field 'Message', enter `{X.Y}`

   e. In the field 'Release notes', enter the content of `CHANGELOG.md` only for this release.

1. Push your changes to master:
   ```fish
   $ git push upstream master
   $ git push upstream --tags
   ```
   :interrobang: This could be done directly inside Gitlab

1. Create a new 'wheel' package for the new release:
    ```fish
    # Remove previous build(s)
    $ rm -rf dist
    
    # Create a wheel and a source package
    $ tox -e build
    $ ls dist
    ``` 

1. Send the new release 'pyxel-sim' to the Python Package Index (PyPI) repository with
   the following commands:
       ```fish
       # Send the package to https://test.pypi.org (only for testing)
       $ tox -e release -- --repository testpypi

       # Send the package to https://pypi.org
       $ tox -e release
       ```
   
1. Send the new release 'pyxel-sim' to the Conda forge channel (after sending the 
   package to PyPi)
   
    1. Create a new recipe based on the current version of `pyxel-sim` from the PyPi
       repository.
   
       1. First install 'grayskull' the recipe generator:
       ```fish
       $ conda install -c conda-forge grayskull
       or
       $ pip install grayskull
      
       1. Then create the recipe 'meta.yaml'
       # Create a new recipe in the folder './pyxel-sim/meta.yaml'
       $ grayskull pypi pyxel-sim
       ```
      
       2. Edit the new file './pyxel-sim/meta.yaml':
          * In section 'run:', add '- pygmo'
          ```yaml
          requirements:
            run:
               ...
               - pygmo    # <== add this
          ```
         
          * In section 'recipe-maintainers', add your github ID.
          ```yaml
          extra:
            recipe-maintainers:
               - MyGitHubID
          ```
    2. Submit the recipe to 'conda-forge' with the following steps:
       1. Login to GitHub
       2. Fork https://github.com/conda-forge/pyxel-sim-feedstock (if it was not already done)
       3. Go to your forked repository 'pyxel-sim-feedstock' or https://github.com/<YOUR_GITHUB_ID>/pyxel-sim-feedstock
       4. Create a new branch 'pyxel-version_x_y_z'
       5. In folder 'recipe', edit the recipe file 'meta.yaml' with the new recipe.
       6. Propose the change as a pull request to branch 'master' in https://github.com/conda-forge/pyxel-sim-feedstock
       7. Once the recSubmit a pull request to Conda Forge

1. Add a section for the next release {X:Y+1} to `CHANGELOG.md`

     ```fish
     ## UNRELEASED

     ### Core

     ### Documentation
    
     ### Models
    
     ### Others
     ```

1. Commit you changes and push to master again:
     ```fish
     $ git commit -am "New Changelog section"
     $ git push upstream master
     ```

1. Issue the release on GitLab.
    Click on https://gitlab.com/esa/pyxel/-/releases . Type in the version number and paste the release summary in the notes.

1. Issue the release announcement to the mailing list pyxel-dev@googlegroups.com and to the Pyxel blog.
