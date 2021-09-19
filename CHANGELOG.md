# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (1.0.0)

## [0.4.1] - 2021-03-10
### Changed
- Added more specific requirements files for different variants ([#14](https://github.com/jojojo8359/neonmobmatcher/issues/14))
- Reflected these changes in README
- Added links to README
- Bumped program version number

### Fixed
- [#2](https://github.com/jojojo8359/neonmobmatcher/issues/2) - Fix Mac Tk bug

## [0.4.0] - 2021-01-21
### Added
- requirements.txt and mac.txt for pip modules
- Console variant of the matcher for terminal testing
  - Used [alive_progress](https://github.com/rsalmei/alive-progress) for console progress bars
  - Used [conditional](https://github.com/stefanholek/conditional) for enabling alive_progress bars on the fly
- Created a LICENSE and CHANGELOG file

### Changed
- README.md with required module changes
- Updated GUI program with improved functions
- Bumped program version number and copyright year
- Reformatted files
- Changed GUI text box formatting to work with new functions

### Removed
- Old bug reports file (use GitHub issues now)

### Fixed
- [#9](https://github.com/jojojo8359/neonmobmatcher/issues/9) - Added a fallback card endpoint for broken requests

## [0.3.0] - 2020-12-29
### Added
- Tkmacosx for better buttons and text box on Mac OSX and dark mode

### Fixed
- Divide by zero error when checking for special card progress

## [0.2.0] - 2020-12-29
### Changed
- Bump version number

## [0.1.0] - 2020-12-29
### Added
- Initial release



[Unreleased]: https://github.com/jojojo8359/neonmobmatcher/compare/v0.4.1...v1.0.0
[0.4.1]: https://github.com/jojojo8359/neonmobmatcher/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/jojojo8359/neonmobmatcher/compare/v0.3...v0.4.0
[0.3.0]: https://github.com/jojojo8359/neonmobmatcher/compare/v0.2...v0.3
[0.2.0]: https://github.com/jojojo8359/neonmobmatcher/compare/v0.1...v0.2
[0.1.0]: https://github.com/jojojo8359/neonmobmatcher/releases/tag/v0.1
