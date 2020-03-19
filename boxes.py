import collections

class Box(collections.namedtuple(
    'Box', (
        'name', 'length', 'width', 'height',
        'weight',
    ))):

    @property
    def volume(self):
        return self.length * self.width * self.height


class SimpleItem(collections.namedtuple(
    'SimpleItem', (
        'name',
        'item_number',
        'length',
        'width',
        'height',
        'weight',

    ))):
    pass
