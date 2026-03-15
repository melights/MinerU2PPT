# Common Project Configuration Files

This document lists common configuration and dependency management files for various programming languages and frameworks. When analyzing a project's technology stack, look for these files in the project root.

## JavaScript / TypeScript
- `package.json`: Defines project metadata, dependencies (dependencies, devDependencies), and scripts. The presence of `typescript` indicates a TypeScript project.
- `tsconfig.json`: Configuration for the TypeScript compiler.
- `webpack.config.js`: Webpack bundler configuration.
- `babel.config.js`: Babel transpiler configuration.
- `next.config.js`: Configuration for Next.js framework.
- `nuxt.config.js`: Configuration for Nuxt.js framework.

## Python
- `requirements.txt`: Lists Python dependencies.
- `Pipfile` / `Pipfile.lock`: Used by `pipenv` for dependency management.
- `pyproject.toml`: Modern Python project configuration, used by tools like Poetry and Hatch.
- `setup.py`: Used for packaging Python projects.

## Java
- `pom.xml`: Project Object Model file for Maven projects. Defines dependencies and build process.
- `build.gradle` / `build.gradle.kts`: Build script for Gradle projects.
- `settings.gradle`: Settings for multi-project Gradle builds.

## Go
- `go.mod`: Defines the module path and its dependency requirements.
- `go.sum`: Contains the expected cryptographic checksums of specific module versions.

## Ruby
- `Gemfile` / `Gemfile.lock`: Defines dependencies for Ruby projects using Bundler.

## Rust
- `Cargo.toml`: The manifest file for Rust projects (crates), contains metadata and dependencies.
- `Cargo.lock`: Contains exact information about dependencies.

## PHP
- `composer.json`: Defines dependencies for PHP projects using Composer.
- `composer.lock`: Records the exact versions of dependencies that were installed.

## .NET
- `*.csproj` / `*.vbproj`: C# or VB.NET project files, contain dependencies (as `<PackageReference>`).
- `packages.config`: Legacy format for NuGet dependencies.
- `solution.sln`: Visual Studio solution file, organizes projects.