from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_SUBSCRIPTIONID,
    CONFIGURATION_URL,
    CONSUMPTION_ENTITY,
    CONSUMPTION_KEY,
    DEFAULT_CONSUMPTION_ICON,
    DEFAULT_MONETARY_ICON,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PRICE_ENTITY,
    PRICE_KEY,
    UNIT_OF_MEASUREMENT_EURO,
    UNIT_OF_MEASUREMENT_WATER,
)
from .coordinator import AguasGaiaCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aguas de Gaia sensors."""
    coordinator: AguasGaiaCoordinator = hass.data[DOMAIN][entry.entry_id]
    subscription_id = entry.data.get(CONF_SUBSCRIPTIONID)

    async_add_entities(
        [
            AguasGaiaSensor(coordinator, PRICE_ENTITY, subscription_id),
            AguasGaiaSensor(coordinator, CONSUMPTION_ENTITY, subscription_id),
        ]
    )


class AguasGaiaSensor(CoordinatorEntity[AguasGaiaCoordinator], SensorEntity):
    """Aguas de Gaia sensor representation."""

    def __init__(
        self,
        coordinator: AguasGaiaCoordinator,
        sensor_type: str,
        subscription_id: str | None,
    ) -> None:
        super().__init__(coordinator)
        self._sensor_type = sensor_type

        entity_name = f"{sensor_type}_{subscription_id}"
        self._attr_name = entity_name
        key = PRICE_KEY if sensor_type == PRICE_ENTITY else CONSUMPTION_KEY
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_should_poll = False
        self._attr_attribution = ATTRIBUTION
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Aguas de Gaia {subscription_id}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=CONFIGURATION_URL,
        )

        if sensor_type == PRICE_ENTITY:
            self._attr_icon = DEFAULT_MONETARY_ICON
            self._attr_native_unit_of_measurement = UNIT_OF_MEASUREMENT_EURO
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif sensor_type == CONSUMPTION_ENTITY:
            self._attr_icon = DEFAULT_CONSUMPTION_ICON
            self._attr_native_unit_of_measurement = UNIT_OF_MEASUREMENT_WATER
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data or {}

        if self._sensor_type == PRICE_ENTITY:
            invoice = data.get(PRICE_ENTITY)
            value = getattr(invoice, "invoice_value", None)
        else:
            consumption = data.get(CONSUMPTION_ENTITY)
            value = getattr(consumption, "consumption_value", None)

        if value is None:
            return None
        return round(value, 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}

        if self._sensor_type == PRICE_ENTITY:
            invoice = data.get(PRICE_ENTITY)
            return invoice.invoice_attributes if invoice else {}

        consumption = data.get(CONSUMPTION_ENTITY)
        return consumption.consumption_attributes if consumption else {}
