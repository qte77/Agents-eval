# Using PlantUML Diagrams

This document provides instructions on how to render the PlantUML diagrams located in this directory, both on your local machine and using the online PlantUML.com service.

All diagrams are themed and support both **light** and **dark** modes.

## 1. Local Rendering

Rendering diagrams locally is the recommended approach as it correctly resolves all local file includes.

### Prerequisites

1. **Java**: PlantUML is a Java application. Check your installation with `java -version`.
2. **PlantUML Jar**: [Download the `plantuml.jar` file](https://plantuml.com/download) and place it in a convenient location.
3. **Graphviz**: Required for most diagram types used in this project. [Download and install Graphviz](https://graphviz.org/download/).

### Rendering Commands

Open your terminal and navigate to this directory (`docs/arch_vis`).

**To render a single diagram (e.g., `c4-MAS-full.plantuml`):**

* **Light Mode (default):**

    ```shell
    java -jar /path/to/plantuml.jar c4-MAS-full.plantuml
    ```

* **Dark Mode:**

    ```shell
    java -jar /path/to/plantuml.jar -DSTYLE=dark c4-MAS-full.plantuml
    ```

**To render all diagrams in this directory:**

* **Light Mode:**

    ```shell
    java -jar /path/to/plantuml.jar *.plantuml
    ```

* **Dark Mode:**

    ```shell
    java -jar /path/to/plantuml.jar -DSTYLE=dark *.plantuml
    ```

This will generate PNG images for each `.plantuml` file.

## 2. Using PlantUML.com (Online)

You can also use the official [PlantUML Web Server](http://www.plantuml.com/plantuml) to render diagrams without installing anything. However, because our diagrams include local theme files, you must modify the source code before pasting it online.

### Instructions

1. **Open a diagram file** (e.g., `c4-MAS-full.plantuml`) in a text editor.
2. **Modify the `!include` path**. You need to replace the local path with the full raw GitHub URL to the theme file.

    * **Find this line:**

        ```plantuml
        !include styles/github-$STYLE.puml
        ```

    * **Replace it with this URL for light mode:**

        ```plantuml
        !include https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/docs/arch_vis/styles/github-light.puml
        ```

    * **Or this URL for dark mode:**
  
        ```plantuml
        !include https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/docs/arch_vis/styles/github-dark.puml
        ```

    > **Note:** Remember to replace `YOUR_USERNAME/YOUR_REPO/main` with the actual path to this repository.

3. **Copy the entire, modified PlantUML source code.**
4. **Paste it** into the text area on the [PlantUML Web Server](http://www.plantuml.com/plantuml). The diagram will update automatically.
