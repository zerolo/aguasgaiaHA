![GitHub](https://img.shields.io/github/license/zerolo/aguasgaiaHA?style=for-the-badge)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/zerolo/aguasgaiaHA?style=for-the-badge)


# Aguas de Gaia
Aguas de Gaia  - Custom Component for Home Assistant

The data source for this integration is the [Aguas de Gaia Client Area](https://portal.ucloud.cgi.com/uPortal2/gaia/index.html#/login).

The author of this project categorically rejects any and all responsibility for the water consumption and billing data presented by the integration.

Data is refreshed every 12 hours by default through the Aguas de Gaia portal.

# Installation
## HACS (Recommended)
This custom integration can be added through HACS.

Assuming you have already installed and configured HACS, follow these steps:

1. Navigate to the HACS integrations page at http://<your-home-assistant>:8123/hacs/integrations.
2. Search for `Aguas de Gaia` under `Integrations` in the HACS Store tab.
3. Click `Download this Repository with HACS`
4. You're done! Now continue with the configuration.

## Manual
Manual installation is not recommended

# Configuration

## Through the interface
1. Navigate to `Settings > Devices & Services` and then click `Add Integration`
2. Search for `Aguas de Gaia`
3. Enter your login details (subscription ID is optional)
4. Repeat the procedure as many times as desired to include other subscriptions

## Options
The polling interval can be changed from the integration's `Configure` menu (1 to 168 hours, default 12).



# Legal notice
This is a personal project and not affiliated with, sponsored or endorsed by [Aguas de Gaia](https://www.aguasgaia.pt/).

All product names, trademarks and registered trademarks in (the images in) this repository, are property of their respective owners. All images in this repository are used by the project for identification purposes only.