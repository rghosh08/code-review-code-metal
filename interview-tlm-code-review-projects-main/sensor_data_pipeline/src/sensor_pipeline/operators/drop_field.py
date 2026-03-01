from dataclasses import dataclass


@dataclass
class DropField:
    input_field: str

    def run(self, records):
        for rec in records:
            rec.pop(self.input_field)
            yield rec
