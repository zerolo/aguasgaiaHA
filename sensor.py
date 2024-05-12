from datetime import timedelta
import logging
from typing import Any, Dict

import aiohttp
from .const import (
    DOMAIN, 
    CONF_USERNAME, 
    CONF_PASSWORD,
    DEFAULT_MONETARY_ICON,
    DEFAULT_CONSUMPTION_ICON,
    UNIT_OF_MEASUREMENT_EURO,
    UNIT_OF_MEASUREMENT_WATER,
    ATTRIBUTION
)
from aguasgaia import AguasGaia

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# API Poll time
SCAN_INTERVAL = timedelta(hours=2)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """ Setup Sensors"""
    session = async_get_clientsession(hass, True)

    config = config_entry.data

    api = AguasGaia(session, config[CONF_USERNAME], config[CONF_PASSWORD])
    await api.initialize()

    sensors = [AguasGaiaSensor(api,"lastInvoice"), AguasGaiaSensor(api,"lastConsumption")]

    async_add_entities(sensors, update_before_add=True)


class AguasGaiaSensor(SensorEntity):
    """ Aguas de Gaia sensor representation """

    def __init__(self, api: AguasGaia, sensorType: str):
        super().__init__()
        self._api = api
        self._sensorType = sensorType

        if sensorType is "lastInvoice":
            self._icon = DEFAULT_MONETARY_ICON
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_EURO
            self._device_class = SensorDeviceClass.MONETARY
            self._state_class = SensorStateClass.MEASUREMENT
            self._state = None
            self._available = True
        elif sensorType is "lastConsumption":
            self._icon = DEFAULT_CONSUMPTION_ICON
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_WATER
            self._device_class = SensorDeviceClass.WATER
            self._state_class = SensorStateClass.MEASUREMENT
            self._state = None
            self._available = True

    @property
    def name(self) ->  str:
        """ Entity Name """
        return self._sensorType
    
    @property
    def unique_id(self) -> str:
        """ Sensor unique id """
        return f"{DOMAIN}__{self._sensorType}"
    
    @property
    def available(self) -> bool:
        return self._available
    
    @property
    def state(self) -> float:
        return self._state
    
    @property
    def device_class(self):
        return self._device_class
    
    @property
    def state_class(self):
        return self._state_class
    
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def attribution(self):
        return ATTRIBUTION
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        if self._api.lastdocdata:
            return self._api.lastdocdata[0]
        return {}

    async def async_update(self) -> None:
        try:
            if self._sensorType is "lastInvoice":
                invoice = await self._api.getLastDocData()
                if invoice:
                    self._state = invoice[0]["dadosPagamento"]["valor"]
            else:
                self._state = 99
        except aiohttp.ClientError as err:
            self._available = False
            _LOGGER.exception("Error retrieving data from Aguas de Gaia API: %s", err)
    
