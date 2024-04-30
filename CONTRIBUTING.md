# Contributing to OpenSENECA

Thank you for your interest in contributing to OpenSENECA!
We welcome contributions from the community to make this project even better.

## Table of Contents

- [Getting Started](#getting-started)

- [Code Style](#code-style)

  - [VS Code Settings](#vscode)

- [Submitting a Pull Request](#submitting-a-pull-request)

- [License](#license)

## Getting Started

To get started with contributing to [Project Name], follow these steps:

1. Fork the repository and clone it to your local machine.
2. Install the required dependencies by running
   `pip install -r requirements.txt`.
3. Create a new branch for your changes: `git checkout -b my-feature`.
4. Make your changes and ensure they adhere to the code style guidelines
   (see next section).
5. Commit your changes with descriptive commit messages.
6. Push your branch to your forked repository: `git push origin my-feature`.
7. Open a pull request against the main repository.

## Code Style

Please follow these code style guidelines when contributing to OpenSENECA:

- Maximum line length: 80 characters.
- Indentation: 2 spaces.
- Use 4 spaces for line continuation.
- Class names should be in PascalCase.
- Use lowercase words or words separated by underscores (snake_case) for
  variable and function names.

### VSCode

You may want to change the VSCode settings to add a vertical line indicating the
80-character limit:

1. Open VSCode and go to the "Settings" menu by clicking on "File" >
   "Preferences" > "Settings" (or by using the shortcut Ctrl or CMD + ,).

2. In the search bar at the top of the settings window, type "Editor: Rulers"
   and click on "Edit in settings.json" to open the settings file.

3. Add this to to your user or workspace settings:

```json
"editor.rulers": [30, 129]
```

4. The color of the rulers can be customized like this:

```json
"workbench.colorCustomizations": {
    "editorRuler.foreground": "#00ffa65f"
}
```

5. Auto trim trailing whitespace "File" > "Preferences" > "Settings", then check
   the "Trim Trailing Whitespace" option

## Submitting a Pull Request

When submitting a pull request, please make sure to:

- Provide a clear and descriptive title for your pull request.
- Include a detailed description of the changes you have made.
- Reference any related issues or pull requests, if applicable.

## License

By contributing to OpenSENECA, you agree that your contributions will be
licensed under the [LICENSE](./LICENSE) file.

If you have any questions or need further assistance, please don't hesitate to
reach out.

Happy contributing! \
— OpenSENECA Team.
