from dataclasses import dataclass
from collections import defaultdict
from itertools import groupby


@dataclass
class GroupBy:
    """Cluster records together by key."""

    key_field: str

    def run(self, records):
        def keyfn(rec):
            return rec[self.key_field]

        # itertools groupby requires records sorted.
        records = sorted(records, key=keyfn)

        # Groups into a new dict with the key and list of records.
        groups = (
            {self.key_field: key, "records": list(group)}
            for key, group in groupby(records, key=keyfn)
        )

        for group in groups:
            yield group
