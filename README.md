# changelog-generator

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<!-- markdownlint-disable no-inline-html -->
<br />
<p align="center">
  <a href="https://github.com/lumapps/changelog-generator">
    <img src="images/speaker.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Changelog generator</h3>

  <p align="center">
    Generate the changelog between now and the last tag,
    based on conventional commit.
    <br />
    <a href="https://github.com/lumapps/changelog-generator">
      <strong>Explore the docs »
    </strong></a>
    <br />
    <br />
    <a href="https://github.com/lumapps/changelog-generator/issues">
      Report Bug
    </a>
    ·
    <a href="https://github.com/lumapps/changelog-generator/issues">
      Request Feature
    </a>
  </p>
</p>
<!-- markdownlint-enable no-inline-html -->

<!-- TABLE OF CONTENTS -->

## Table of Contents

- [About the Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->

## About The Project

The provided script generate a changelog, based on Angular commit message convention.

### Changelog format

The changelog is based on all the commits since the last tag.
It relies on the Angular commit message convention, to display some nice information.
Changes are grouped by type and scope.

### Built With

- [python](https://www.python.org)
- [make](https://www.gnu.org/software/make)

<!-- GETTING STARTED -->

## Getting started with command line

To get a local copy up and running follow these steps.

### Prerequisites

1. Install python3.7

   ```sh
   sudo apt install python3
   ```

2. Install make for development

   ```sh
   sudo apt install make
   ```

### Installation

1. Clone the changelog-generator

   ```sh
   git clone https://github.com/lumapps/changelog-generator.git
   ```

2. Install the dependancies

That's all, your ready to go !

   ```sh
   make
   ```

<!-- USAGE EXAMPLES -->

## Usage

Generate the changelog since the last tag

```sh
python3 ./changelog_generator
```

## Getting started with github action

To enable the action simply create the
.github/workflows/release.yml file with the following content:

```yml
name: Create Release

on:
  push:
    tags:
      - '[0-9]+-[0-9]+-[0-9]+'

jobs:
  build:
    name: Create Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Generate changelog
        id: generate_changelog
        uses: lumapps/changelog-generator@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAG_PREFIX: # add a prefix here if you have a `prefix/semver` pattern in your repo
          MAX_LENGTH: # max_length for the changelog, once above sections will be cutted to avoid crash. Defaults to 5000.
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: ${{ steps.generate_changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/lumapps/changelog-generator/issues)
for a list of proposed features (and known issues).

- [x] list all the commit since the last tag
- [x] generate the changelog with a template
- [x] group by type and scope
- [ ] properly handle rc version
- [x] properly handle revert commit
- [ ] allow hiding some types

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be
learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Run the tests (`make tests`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a pull request

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->

## Contact

Project Link: [https://github.com/lumapps/changelog-generator](https://github.com/lumapps/changelog-generator)

<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

<!-- markdownlint-disable no-inline-html -->
Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a>
from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>
<!-- markdownlint-enable no-inline-html -->

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/lumapps/changelog-generator.svg?style=flat-square
[contributors-url]: https://github.com/lumapps/changelog-generator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/lumapps/changelog-generator.svg?style=flat-square
[forks-url]: https://github.com/lumapps/changelog-generator/network/members
[stars-shield]: https://img.shields.io/github/stars/lumapps/changelog-generator.svg?style=flat-square
[stars-url]: https://github.com/lumapps/changelog-generator/stargazers
[issues-shield]: https://img.shields.io/github/issues/lumapps/changelog-generator.svg?style=flat-square
[issues-url]: https://github.com/lumapps/changelog-generator/issues
[license-shield]: https://img.shields.io/github/license/lumapps/changelog-generator.svg?style=flat-square
[license-url]: https://github.com/lumapps/changelog-generator/blob/master/LICENSE
