from dataclasses import dataclass
from typing import Optional


@dataclass
class Aggregate:
    function: str
    output_field: str
    input_field: str = ""

    def run(self, records):
        """
        Expected shape is the output of a group by so the
        each record is a { key, list(records) } dictionay
        """
        if self.function == "avg":
            agg_fn = self.avg
        elif self.function == "count":
            agg_fn = self.count

        for rec in records:
            rec[self.output_field] = agg_fn(rec["records"])
            yield rec

    def avg(self, records):
        # Note: for a very large set it might be better to average in
        # blocks so that we don't generate massively large sums.
        values = (rec[self.input_field] for rec in records)
        return sum(values) / len(records)

    def count(self, records):
        return len(records)
