from dataclasses import dataclass


@dataclass
class ConvertTemperatureCToF:
    """Converts the value of a field from celcius to fahrenheit."""

    input_field: str
    output_field: str

    def run(self, records):
        for rec in records:
            temp_c = rec[self.input_field]
            temp_f = (temp_c * 9 / 5) + 32
            rec[self.output_field] = temp_f
            yield rec
