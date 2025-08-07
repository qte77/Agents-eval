# Architecture Visualizations

This directory contains the source files for the project's architecture diagrams. All diagrams are authored in PlantUML and are designed to be rendered into themed PNG images (light and dark modes).

## Local Rendering

The recommended way to generate diagrams is by using the `make setup_plantuml` and `make run_plantuml` command from the root of the project. This command handles all the complexities of rendering for you.

### Prerequisites

- **Docker**: You must have Docker installed and running, as the command uses the official `plantuml/plantuml` Docker image to perform the rendering.

### Usage

The `make` command provides a simple interface for generating diagrams with different themes and for different source files.

#### Specifying an Input File

To render a different diagram, set the `INPUT` variable:

```shell
make run_plantuml INPUT=docs/arch_vis/customer-journey-activity.plantuml
```

#### Specifying the Output File

You can also control the output location and filename by setting the `OUTPUT` variable. This is useful for placing generated assets directly into the `assets/images` directory.

```shell
fn=MAS-C4-Overview
in=docs/arch_vis
out=assets/images
make run_plantuml \
  STYLE=dark \
  INPUT=${in}/${fn}.plantuml \
  OUTPUT=${out/${fn}.png
```

#### Specifying the style

To render a different diagram, set the `STYLE` variable. Defaults to `light`:

```shell
make run_plantuml STYLE=dark
```

## Online Rendering (PlantUML.com)

If you don't have Docker installed, you can use the official [PlantUML Web Server](http://www.plantuml.com/plantuml) to render diagrams. However, because our diagrams include local theme files, you must modify the source code before pasting it online.

### Instructions

1. **Open a diagram file** (e.g., `MAS-Review-Workflow.plantuml`) in a text editor.
2. **Modify the `!include` path**. You need to replace the local path with the full raw GitHub URL to the theme file.
    - **Find this line:**

        ```plantuml
        !include styles/github-$STYLE.puml
        ```

    - **Replace it with this URL for the light theme:**
  
        ```plantuml
        !include https://raw.githubusercontent.com/qte77/Agents-eval/main/docs/arch_vis/styles/github-light.puml
        ```

    - **Or this URL for the dark theme:**

        ```plantuml
        !include https://raw.githubusercontent.com/qte77/Agents-eval/main/docs/arch_vis/styles/github-dark.puml
        ```

3. **Copy the entire, modified PlantUML source code.**
4. **Paste it** into the text area on the [PlantUML Web Server](http://www.plantuml.com/plantuml). The diagram will update automatically.
