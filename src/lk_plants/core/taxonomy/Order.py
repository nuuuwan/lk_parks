from lk_plants.core.taxonomy.Taxon import Taxon


class Order(Taxon):
    def to_dict(self):
        return dict(
            name=self.name,
        )

    @staticmethod
    def from_dict(d):
        return Order(name=d['name'])

    @staticmethod
    def from_family_name(family_name: str) -> 'Order':
        order = Order(name="unknown")
        order.write()
        return order
