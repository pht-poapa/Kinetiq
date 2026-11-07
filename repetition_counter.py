from statistics import median


def new_counter():
    return {'position': 'waiting', 'candidate': None, 'candidate_since': 0, 'start': None, 'minimum': None, 'samples': [], 'report': []}


def track_repetition(angle, time, counter, settings):
    if angle is None:
        report = counter['report']
        counter.update(new_counter())
        counter['report'] = report
        return None

    samples = [(t, value) for t, value in counter['samples'] if time - t <= 0.15]
    samples.append((time, angle))
    counter['samples'] = samples
    angle = median(value for t, value in samples)

    target = 'middle'
    if angle > settings['extended_angle']:
        target = 'extended'
    elif angle < settings['bent_angle']:
        target = 'bent'

    if counter['position'] == 'extended':
        if target == 'extended':
            counter['start'] = None
            counter['minimum'] = None
        elif counter['start'] is None:
            counter['start'] = time
            counter['minimum'] = angle

    if counter['start'] is not None:
        counter['minimum'] = min(counter['minimum'], angle)

    if target == 'middle':
        counter['candidate'] = None
        return angle

    if counter['candidate'] != target:
        counter['candidate'] = target
        counter['candidate_since'] = time
        return angle

    if time - counter['candidate_since'] < 0.15:
        return angle

    if target == 'extended':
        if counter['position'] == 'bent':
            report = counter['report']
            report.append({'rep': len(report) + 1, 'start_seconds': round(counter['start'], 3), 'end_seconds': round(time, 3), 'duration_seconds': round(time - counter['start'], 3), 'min_angle_degrees': round(counter['minimum'], 1)})
        counter['position'] = 'extended'
        counter['start'] = None
        counter['minimum'] = None
    elif counter['position'] == 'extended':
        counter['position'] = 'bent'

    return angle
