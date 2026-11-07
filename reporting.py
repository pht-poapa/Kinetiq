from io import StringIO
import csv


def report_csv(analysis):
    output = StringIO()
    fields = ['exercise', 'side', 'source', 'rep', 'start_seconds', 'end_seconds', 'duration_seconds', 'min_angle_degrees']
    writer = csv.DictWriter(output, fieldnames = fields)
    writer.writeheader()

    for row in analysis['report']:
        writer.writerow({'exercise': analysis['exercise'], 'side': analysis['side'], 'source': analysis.get('source', 'video'), **row})

    return output.getvalue().encode('utf-8-sig')
