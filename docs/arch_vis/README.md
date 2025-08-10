# Architecture Visualizations

This directory contains the source files for the project's architecture diagrams. All diagrams are authored in PlantUML and are designed to be rendered into themed PNG images (light and dark modes).

## Local Rendering

The recommended way to generate diagrams is by using the `make` commands from the root of the project. These commands handle all the complexities of rendering for you.

### Prerequisites

- **Docker**: You must have Docker installed and running, as the command uses the official `plantuml/plantuml` Docker image to perform the rendering.

### Setup

First, you need to set up the PlantUML environment. This is a one-time setup.

```shell
make setup_plantuml
```

### Usage

There are two ways to render the diagrams:

#### Interactive Mode

To start an interactive PlantUML server that automatically re-renders diagrams when you make changes, use:

```shell
make run_puml_interactive
```

This will start a server on `http://localhost:8080`.

#### Single Run

To render a single diagram, use the `run_puml_single` command. You can specify the input file and the style (light or dark).

```shell
make run_puml_single INPUT_FILE="docs/arch_vis/metrics-eval-sweep.plantuml" STYLE="dark" OUTPUT_PATH="assets/images"
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
