from homeassistant.helpers import entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from datetime import timedelta
import voluptuous as vol
import urllib.request, json
import homeassistant.helpers.config_validation as cv

__version__ = "1.1.0"

CONF_NAME = "name"
CONF_ACCESS_KEY = "access_key"
CONF_RIG_NAME = "rig_name"
DEFAULT_NAME = "Minerstat"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)
SCAN_INTERVAL = timedelta(minutes=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ACCESS_KEY): str,
        vol.Required(CONF_RIG_NAME): str,
    }
)


def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([Minerstat(hass, config)])


class Minerstat(entity.Entity):
    def __init__(self, hass, config):
        self.hass = hass
        self._config = config
        self._state = None
        self._unit = None
        self._temperature = None
        self._sync = None
        self._type = None
        #self._groups = None
        self._status = None
        self._attributes = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._config[CONF_NAME]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return "mdi:bitcoin"

    @property
    def state(self):
        """Return the state of the device."""
        return self._state
    
    @property
    def state_attributes(self):
        """Return the device state attributes."""
        return self._attributes

    def update(self):
        req = urllib.request.Request(
            f"https://api.minerstat.com/v2/stats/{self._config[CONF_ACCESS_KEY]}/{self._config[CONF_RIG_NAME]}",
            headers={"User-Agent": "Home-assistant.io"},
        )

        with urllib.request.urlopen(req) as url:
            data = json.loads(url.read().decode())

            self._status = data[self._config[CONF_RIG_NAME]]["info"]["status"]

            if self._status == "offline":
                self._state = 0
            else:
                self._state = data[self._config[CONF_RIG_NAME]]["mining"]["hashrate"][
                    "hashrate"
                ]
                self._unit = data[self._config[CONF_RIG_NAME]]["mining"]["hashrate"][
                    "hashrate_unit"
                ]
                self._temperature = data[self._config[CONF_RIG_NAME]]["info"]["os"]["cpu_temp"]
                self._sync = data[self._config[CONF_RIG_NAME]]["info"]["sync"]
                self._type = data[self._config[CONF_RIG_NAME]]["info"]["type"]
                #self._groups = data[self._config[CONF_RIG_NAME]]["info"]["groups"]            
                self._attributes = {}
                self._attributes[groups] = data[self._config[CONF_RIG_NAME]]["info"]["groups"]


    #@property
    #def device_state_attributes(self):
        #return {"unit_of_measurement": self._unit, "status": self._status, "temperature": self._temperature, "sync": self._sync, "type": self._type, "groups": self._groups}
