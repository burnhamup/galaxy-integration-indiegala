# galaxy-integration-indiegala

GOG Galaxy Integration for Indiegala

---
## Known Issues
Only works with games listed in your showcase: https://www.indiegala.com/library/showcase

I don't have a great handle on playing nicely with the various security systems of IndieGala. It is recommended that you login and visit https://www.indiegala.com/library before using this plugin to make sure that you are able to verify your IP address. 

After a few hours or days the plugin may disconnect because of captchas from IndieGala. The plugin should prompt you to login again.


## Installation
1. Download [latest release](https://github.com/burnhamup/galaxy-integration-indiegala/releases/latest) of the plugin for your platform.
2. Create plugin folder:
	- Windows: `%LOCALAPPDATA%\GOG.com\Galaxy\plugins\installed\<my-plugin-name>`
	- MacOS: `${HOME}/Library/Application Support/GOG.com/Galaxy/plugins/installed/<my-plugin-name>`
3. Unpack downloaded release to created folder.
4. Restart GOG Galaxy Client.

## Issue reporting
Along with you detailed problem description, you may need to attach plugin log files located at:
- Windows: `%programdata%\GOG.com\Galaxy\logs`
- MacOS: `/Users/Shared/GOG.com/Galaxy/Logs`

for example:
`C:\\ProgramData\GOG.com\Galaxy\logs\indiegala-a1a85742-f3e0-42ae-bde9-64ab7d0321cf.log`

## Development

1. create and activate virtual environment
2. install dependencies

        pip install -r requirements/dev.txt

3. run tests

        pytest
        
4. install to your local GOG galaxy
 
        inv install
