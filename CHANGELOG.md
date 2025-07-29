# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.4.0] - 2025-07-28
### Added
- Add timezone parameter
- All subclass of pd.Dataframe can be saved on parquet

### Changed
- Change metadata extension from .resnap to .resnap_meta.json
- Updated the calculation logic for day time unit.The day unit now returns the start of the day instead of exactly (24 * n_days) hours ago.
- Extract time functions from utils
- Types: Refactor @resnap and @async_resnap decorator to correctly handle calls with and without arguments.

### Fixed
- Replace some if statements with match case
- Fix some typos

## [0.3.0] - 2025-07-25
### Added
- Set a custom config file location using the `RESNAP_CONFIG_FILE` env var

### Changed
- The global config instance is now lazy loaded

## [0.2.0] - 2025-06-19
### Added
- Add mypy and pyright support

### Changed
- Change hash logic
- Rename add_metadatas -> add_multiple_metadata
- Change CI with #no_test tag in commit message

### Fixed
- Fix config check secret filename if not enabled
- Fix some typing

## [0.1.1] - 2025-05-22
### Changed
- Fix documentation with Github URL
- Fix link in README.md on Pypi

## [0.1.0] - 2025-05-16
### Added
- Implementing the resnap decorator for synchronous
- Implementing the async_resnap decorator for asynchronous
- Implemented ResnapError to pass data on error
- Implement set_resnap_service to pass a custom service
- Implemented add_metadata to add custom metadata
- Implemented add_metadatas to add custom metadata

### Changed

## [0.0.1] - 2025-04-18
- Init project