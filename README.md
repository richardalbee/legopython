<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>



<!-- LegoPython -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ralbee1/legopython">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">LegoPython</h3>

  <p align="center">
    A component-based develop template for internal tooling features.
    <br />
    <a href="https://github.com/ralbee1/legopython"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ralbee1/legopython">View Demo</a>
    ·
    <a href="https://github.com/ralbee1/legopython/issues">Report Bug</a>
    ·
    <a href="https://github.com/ralbee1/legopython/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#Features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project
<!-- 
[![Product Name Screen Shot][product-screenshot]](https://example.com)
-->
LegoPython was concieved to facilitate and standardize internal tooling efforts, initially structuring business processes for many internal applications and hundreds of resulting internal scripts. LegoPython embodies component-based development; by developing and iterating upon reusable modules, others can build upon our progress. This template is stripped down to the core, nonpropriatary, application-level features for use across  organizations. Currently, LegoPython is a scripting sandbox focused on developing API, AWS, and Database data workflows although other data sources would also be supported.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

* [![Python][python.org]][python-url]
* [![PyPi][pypi.org]][pypi-url] PyPi


### Features

- [ ] **Global Settings**
  - [ ] Environment Handling
  - [ ] Logging Level (Console + Log File)
  - [ ] AWS Region
- [ ] **API Authentication**
  - [ ] Basic Auth
  - [ ] Bearer Tokens
- [ ] **AWS Products**
  - [ ] Secrets Manager
  - [ ] DynamoDB
  - [ ] S3
- [ ] **Databases (PostGreSQL)**
  - [ ] Creating SQL connections from Secrets Manager credentials
- [ ] **CLI Interface**
    - [ ] No Code CLI Interface
    - [ ] Change Global Settings
    - [ ] Supports any Python function or Command Line
- [ ] **Auto Updating (Artifactory)**
- [ ] **Templates for new API modules**
- [ ] **PyPi Installs**


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an guide for setting up LegoPython locally.

### Prerequisites

1. [Python 3.10.8](https://www.python.org/downloads/release/python-3108/)
2. [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. [AWS SSO Login Configured](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html)


### Installation

**Developer Install:**
Summary: The developer install is for those who want to contribute to or clone LegoPython.
1. Clone the repo (or use Github Desktop)
   ```sh
   git clone https://github.com/ralbee1/legopython.git
   ```
2. Open the CLI and navigate the current working directory to where you cloned LegoPython
3. Install the Pip Package from the CLI, copy and run this command:
   ```sh
   py -m pip install -e .
   ```
4. [Optional] Internal Pip Install
     
    This step configures the "User Install" below. If are copying this template for internal use, you can allow non-technical users to update your private version of LegoPython by creating a simple DevOps workflow to package the pip (Jenkins/Github Actions, Ect), uploading the pip to an internally accessible location (ex) Jfrog Artifactory), creating a secure read-only account to download the pip, and updating those credentials into a function which caches a .netrc file in the users home directory.
    
    If all of your users are savvy enough to update their pip install after updating from master, then this step is signifcantly less worth the investment.

**Example User Install - Does not Work**
The user install url does not work with the template. This example shows how you could have a non-technical user update from an internally published, proprietary version of LegoPython, pip in Jfrog Artifactory.
1. Command Line Instructions
   ```js
   pip install --upgrade legopython -i https://app.jfrog.io/artifactory/api/pypi/home-pypi/simple;
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Confirm Support for Latest Python Version
- [ ] Update CLI interface to a GUI
- [ ] Allow automatic Bearer Token Retrieval

See the [open issues](https://github.com/ralbee1/legopython/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

* []()Email - ralbee1@iwu.edu
* []()Project Link: [https://github.com/ralbee1/legopython](https://github.com/ralbee1/legopython)



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []() Thank you Justin G. for your amazing mentorship. You deserve all the credit for initially creating what LegoPython is based off of.
* []() Huge shoutout to Ted G. for another amazing mentor and for contributing to design elements of LegoPython.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ralbee1/legopython.svg?style=for-the-badge
[contributors-url]: https://github.com/ralbee1/legopython/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ralbee1/legopython.svg?style=for-the-badge
[forks-url]: https://github.com/ralbee1/legopython/network/members
[stars-shield]: https://img.shields.io/github/stars/ralbee1/legopython.svg?style=for-the-badge
[stars-url]: https://github.com/ralbee1/legopython/stargazers
[issues-shield]: https://img.shields.io/github/issues/ralbee1/legopython.svg?style=for-the-badge
[issues-url]: https://github.com/ralbee1/legopython/issues
[license-shield]: https://img.shields.io/github/license/ralbee1/legopython.svg?style=for-the-badge
[license-url]: https://github.com/ralbee1/legopython/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/Richard-Albee
[product-screenshot]: images/screenshot.png
[python.org]: https://www.python.org/static/img/python-logo.png
[python-url]: https://www.python.org/
[pypi.org]: https://pypi.org/static/images/logo-small.2a411bc6.svg
[pypi-url]: https://pypi.org/project/pip/
