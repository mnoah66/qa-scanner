from datetime import time
import pandas as pd

duration = {
    'low':60,
    'high': 390
}
notelength = 75
odd_times = {
    'start_before':time(8,0,0),
    'start_after':time(16,0,0),
    'end_before':time(12,0,0),
    'end_after':time(15,0,0)
}
keywords = {'dayhab':
                ['appointment',
                'appt',
                'did not come in',
                'late',
                'late',
                'early',
                'went home sick',
                'sick',
                'dismissal',
                'delay',
                '911',
                'police',
                'hospital',
                'absent',
                'suspension',
                'suspended',
                'protocol',
                'closed',
                'bloodwork',
                'not applicable',
                ' er ',
                'emergency room',
                'fbformmissingtrue'
                ],
            'residential': [
                'vacation',
                ' camp ',
                'home visit',
                'home for the',
                '911',
                'This service was not applicable with',
                'admitted',
                'hospital',
                'admission',
                ' er ',
                'emergency room'
                ]}
