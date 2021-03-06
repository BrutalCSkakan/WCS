# ../wcs/core/modules/items/manager.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# WCS Imports
#   Constants
from ...constants import ItemReason
from ...constants.paths import ITEM_PATH_ES
from ...constants.paths import ITEM_PATH
#   Listeners
from ...listeners import OnIsItemUsable
from ...listeners import OnPluginItemLoad
#   Menus
from ...menus import shopmenu_menu
from ...menus import shopinfo_menu
#   Modules
from . import _callbacks
from ..base import _BaseManager
from ..base import _BaseSetting


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'item_manager',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class ItemSetting(_BaseSetting):
    def __init__(self, name):
        super().__init__(name, ITEM_PATH)

    def execute(self, name, *args):
        super().execute(name, 'items', _callbacks, args)

    def usable_by(self, wcsplayer):
        data = {'reason':None}

        OnIsItemUsable.manager.notify(wcsplayer, self, data)

        if data['reason'] is not None:
            return data['reason']

        required = self.config.get('required')

        if required:
            if wcsplayer.total_level < required:
                return ItemReason.REQUIRED_LEVEL

        dab = self.config.get('dab')

        if dab is not None:
            if not dab == 2:
                player = wcsplayer.player

                if dab == player.dead:
                    return ItemReason.WRONG_STATUS

        maxitems = wcsplayer.items._maxitems

        for category in self.config['categories']:
            if maxitems[category] >= item_manager._category_max_items[category]:
                return ItemReason.TOO_MANY_CATEGORY

        if self.name in wcsplayer.active_race.settings.config['restrictitem']:
            return ItemReason.RACE_RESTRICTED

        cost = self.config.get('cost')

        if cost is not None:
            player = wcsplayer.player

            if cost > player.cash:
                return ItemReason.CANNOT_AFFORD

        count = self.config.get('count')

        if count:
            item = wcsplayer.items.get(self.name)

            if item is not None:
                if item.count >= count:
                    return ItemReason.TOO_MANY

        return ItemReason.ALLOWED

    def add_to_category(self, category):
        self._add_to_category(item_manager, 0, category, shopmenu_menu, shopinfo_menu)


class _ItemManager(_BaseManager):
    instance = ItemSetting

    def __init__(self):
        super().__init__()

        self._category_max_items = {}

    def load(self, name):
        return self._load(name, 'items', ITEM_PATH, ITEM_PATH_ES, OnPluginItemLoad)

    def load_all(self):
        config = self._get_or_create_config('items', ITEM_PATH, ITEM_PATH_ES)

        for category, data in config['categories'].items():
            if not category.startswith('_'):
                self._category_max_items[category] = data['maxitems']

        self._load_categories_and_values('items', config, ITEM_PATH, ITEM_PATH_ES)

    def unload(self, name):
        self._unload(name, 'items')
item_manager = _ItemManager()
