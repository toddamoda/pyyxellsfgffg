#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Functions to add new models."""

import logging
import sys
import time
from pathlib import Path


def create_model(newmodel: str) -> None:
    """Create a new module using pyxel/templates/MODELTEMPLATE.py.

    Parameters
    ----------
    newmodel : str
        modeltype/modelname
    """

    location, model_name = get_name_and_location(newmodel)

    # Is not working on UNIX AND Windows if I do not use os.path.abspath
    template_str = "_TEMPLATE"
    template_location = "_LOCATION"

    # Copying the template with the user defined model_name instead
    import pyxel

    folder: Path = Path(pyxel.__file__).parent
    src: Path = folder.joinpath("templates").resolve()
    dest: Path = folder.joinpath(f"models/{location}").resolve()

    if not src.exists():
        raise FileNotFoundError(f"Folder '{src}' does not exists !")

    try:
        # Replacing all templates in filenames and directories by model_name
        filename: Path
        for filename in src.glob("**/*"):
            if filename.suffix == ".pyc" or filename.name == "__pycache__":
                continue

            relative_filename: str = str(filename.relative_to(src))
            new_relative_filename = relative_filename.replace(template_str, model_name)

            # Get a destination filename
            new_filename: Path = dest.joinpath(new_relative_filename)

            # Create new modified content
            content: str = filename.read_text()
            new_content: str = (
                content.replace(template_str, model_name)
                .replace(template_location, location)
                .replace("%(date)", time.ctime())
            )

            # Save this content in the destination filename
            new_filename.parent.mkdir(parents=True, exist_ok=True)
            new_filename.write_text(new_content)

        logging.info("Module %r created.", model_name)
        print(f"Module {model_name!r} created in {dest!r}.")

    except FileExistsError:
        logging.info("%r already exists, folder not created", dest)
        raise
    except OSError as exc:
        # Any error saying that the directory doesn't exist
        logging.critical("%r not created. Error: %s", model_name, exc)
        raise


def get_name_and_location(newmodel: str) -> tuple[str, str]:
    """Get name and location of new model from string modeltype/modelname.

    Parameters
    ----------
    newmodel: str

    Returns
    -------
    location: str
    model_name: str
    """

    try:
        location, model_name = newmodel.split("/")
    except Exception:
        sys.exit(
            f"""
        Can't create model {newmodel!r}, please use location/newmodelname
        as an argument for creating a model
        """
        )
    return location, model_name
