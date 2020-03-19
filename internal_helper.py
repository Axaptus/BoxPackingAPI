from .errors import BoxError
from .boxes import Box
import .messages as msg
from .helper import api_packing_algorithm
from .packing_algorithm import does_it_fit, packing_algorithm, ItemTuple


def is_packing_valid(item_quantities, box):
    items = []
    for item, quantity in item_quantities.items():
        items.append({
            'product_name': item.name,

            'weight': item.weight,

            'width': item.width,
            'height': item.height,
            'length': item.length,

            'quantity': quantity
        })
    try:
        packing = api_packing_algorithm([box], items, None)
        return len(packing['packages']) == 1
    except BoxError:
        return False
    return True


def select_useable_boxes(boxes, min_box_dimensions):
    '''

    Args:
        boxes (iterable[boxes.Box])
        min_box_dimensions (List[int, int, int])
        team (Team),
        flat_rate_okay (Boolean)

    Returns:
        List[Dict[{'box': Box,
                   'dimensions': List[int, int, int]}]]: a list of usable
            shipping boxes and their dimensions
    '''
    for box in boxes:
        box_dims = sorted([box.width, box.height, box.length])
        # make sure we only look at boxes where every item will fit
        if does_it_fit(min_box_dimensions, box_dims):
            useable_boxes.append({'box': box, 'dimensions': box_dims})
    # sort boxes by volume, smallest first and return
    return sorted(useable_boxes, key=lambda box: box['box'].volume)


def shotput_packing_algorithm(available_boxes, team, qty_per_item, flat_rate_okay=False,
                              zone=None, preferred_max_weight=None):
    '''
    from items provided, and boxes available, pack boxes with items

    - returns a dictionary of boxes with an 2D array of items packed
        in each parcel

    Args:
        available_boxes (iterable[boxes.Box])
        team (Team)
        qty_per_item (Dict[str, Dict[{
            'item': SimpleItem,
            'quantity': int
        }]]): quantity of each item needing to be packed
        flat_rate_okay (boolean): whether or not usps flat and regional rate
            boxes can be used
        zone (int): usps regional shipping zone based on shotput Warehouse
        preferred_max_weight (int): max weight of a parcel if not 70lbs

    Returns:
        Dict[{
            package (Packaging[Box, List[List], Box]
            flat_rate (Packaging[Box, List[List], Box]
        }]

    Example:
    >>> shotput_packing_algorithm(available_boxes, team1, {item1: 1, item2: 3}, True)
    {
        'package': (box=<best_standard_box object>,
                    items_per_box= [[item1, item2], [item2, item2]],
                    last_parcel=<smaller_box object),
        'flat_rate': (box=<best_flat_rate object>,
                      items_per_box=[[item1], [item2, item2, item2]],
                      last_parcel=None)
    }
    '''
    unordered_items = []
    max_weight = preferred_max_weight or 31710
    min_box_dimensions = [None, None, None]

    for item_number, item_data in qty_per_item.items():

        dimensions = sorted([item_data['item'].width,
                             item_data['item'].height,
                             item_data['item'].length])
        min_box_dimensions = [max(a, b) for a, b in zip(dimensions,
                                                         min_box_dimensions)]
        unordered_items += ([ItemTuple(item_data['item'], dimensions,
                            item_data['item'].weight)] *
                           int(item_data['quantity']))

    useable_boxes = select_useable_boxes(available_boxes, min_box_dimensions, team,
                                         flat_rate_okay)
    # if weight is greater than max, make sure we are separating it into
    # multiple boxes

    if len(useable_boxes) == 0:
        raise BoxError(msg.boxes_too_small)

    package = packing_algorithm(unordered_items, useable_boxes,
                                       max_weight, zone)
    if package is not None:
        items_per_box = [[item.item_number for item in parcel]
                        for parcel in package.items_per_box]
        package = package._replace(
            items_per_box=items_per_box)
    return box_dictionary
