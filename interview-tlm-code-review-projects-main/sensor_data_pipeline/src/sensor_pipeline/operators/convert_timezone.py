from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime


@dataclass
class ConvertTimezone:
    """Converts a timestamp to a new timezone."""

    input_field: str
    output_field: str
    tz: str

    def run(self, records):
        tzinfo = ZoneInfo(self.tz)
        for rec in records:
            isotime = rec[self.input_field]
            dt = datetime.fromisoformat(isotime)
            tztime = dt.astimezone(tzinfo)
            rec[self.output_field] = tztime.isoformat()
            yield rec
