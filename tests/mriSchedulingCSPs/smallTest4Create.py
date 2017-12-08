from datetime import date, datetime, timedelta
import itertools
from collections import namedtuple

def perdelta(start, end, delta):
    """
        Generate a list of datetimes between a time period.
        """
    curr = start
    while curr <= end:
        yield curr
        curr += delta

def overlap(time_pair):
    """
        Calulates overlap between two time periods.
    """
    if time_pair[0][0] == time_pair[1][0]:
        Range = namedtuple('Range', ['start', 'end'])
        r1 = Range(start=time_pair[0][1], end=time_pair[0][2])
        r2 = Range(start=time_pair[1][1], end=time_pair[1][2])
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        return (earliest_end - latest_start).total_seconds()
    return 0.0

def generate_domains(n_machines, patients, start_date_raw, end_date_raw, start_time_raw, end_time_raw, min_interval, max_interval):
    """
        Generate the domains for a given problem.
    """
    dttmfmt = '%Y-%m-%d %H:%M'
    dtfmt = '%Y-%m-%d'
    tmfmt = '%H:%M'
    
    patients_new = patients
    for patient in patients_new:
        patient[1] = datetime.strptime(patient[1], dttmfmt)
        patient[2] = datetime.strptime(patient[2], dttmfmt)
    
    start_date = datetime.strptime(start_date_raw, dtfmt)
    end_date = datetime.strptime(end_date_raw, dtfmt)
    start_time = datetime.strptime(start_time_raw, tmfmt)
    end_time = datetime.strptime(end_time_raw, tmfmt)
    
    days=[]
    for date in perdelta(start_date , end_date, timedelta(days = 1)):
        days.append(date)
    
    times=[]
    for time in perdelta(start_time , end_time, timedelta(minutes = min_interval)):
        times.append(time)
    
    dttm_lst = []
    for day in days:
        for time in times:
            dttm_lst.append(datetime.combine(day.date(), time.time()))

    domains = []
    for m in range(1, n_machines + 1):
        for d in dttm_lst[:-1]:
            for s in range(min_interval, max_interval+1, min_interval):
                if d + timedelta(minutes = s) <= datetime.combine(day.date(), time.time()):
                    domain = []
                    domain.append(m)
                    domain.append(d)
                    domain.append(d + timedelta(minutes = s))
                    domains.append(domain)

    n_variables = len(domains)

    return domains, n_variables

def generate_constarints(patients, domains):
    """
        Generate the constarints for a given problem.
    """
    
    constraints = []
    domain_lst = domains
    patient_lst = patients
    
    # all possible combinations
    # [[([P1],[P2]),[([D1],[D2]),([D3],[D4]),...]]...]
    for patient_pair in itertools.combinations(patient_lst, 2):
        constraint = []
        constraint.append(patient_pair)
        constraint.append(list(itertools.permutations(domain_lst, 2)))
        constraints.append(constraint)
    
    # correct for duration, start time, due date (urgency), and capacity
    for constraint in constraints:
        constraint[1] = filter(lambda x: abs((x[0][2]  - x[0][1]).total_seconds() / 60.0) >= constraint[0][0][0], constraint[1])
        constraint[1] = filter(lambda x: abs((x[1][2]  - x[1][1]).total_seconds() / 60.0) >= constraint[0][1][0], constraint[1])
        constraint[1] = filter(lambda x: x[0][1] > constraint[0][0][1], constraint[1])
        constraint[1] = filter(lambda x: x[1][1] > constraint[0][1][1], constraint[1])
        constraint[1] = filter(lambda x: x[0][2] < constraint[0][0][2], constraint[1])
        constraint[1] = filter(lambda x: x[1][2] < constraint[0][1][2], constraint[1])
        constraint[1] = filter(lambda x: overlap(x) <= 0, constraint[1])
    
    return constraints

def generate_output(n_machines, patients, start_date_raw, end_date_raw, start_time_raw, end_time_raw, min_interval, max_interval):
    """
        Generate a file that stipulates formulation of Dynamic CSP.
    """
    
    domains, n_variables = generate_domains(n_machines, patients, start_date_raw, end_date_raw, start_time_raw, end_time_raw, min_interval, max_interval)
    constraints = generate_constarints(patients, domains)
    
    output = str(n_variables) + '\n'
    
    for patient in patients:
        p = str(patient).replace(' ', '')
        for domain in domains:
            p = p + ' ' + str(domain).replace(' ', '')
        output = output + p + '\n'
    
    for constraint in constraints:
        c = 'c 0 a'
        for patient_pair in constraint[0]:
            c = c + ' ' + str(patient_pair).replace(' ', '')
        for domains in constraint[1]:
            for domain in domains:
                c = c + ' ' + str(domain).replace(' ', '')
        output = output + c + '\n'
    
    new_output = output

    for index, patient in enumerate(patients):
        p = str(patient).replace(' ', '')
        new_output = new_output.replace(p, str(index + 1))

    print new_output

"""
This is the inteface for our system. Make changes to the number of MRI
machines, add and remove patients, and set schedule related settings such
as when you want to start accepting patients and end accepting patients.
"""

# Number of MRI machines
n_machines = 2

# Patients - each patiend is defined by a vector consisting of [duration of scan (min), call-time, due-date (urgency)]
patients = [[60.0, '2017-12-24 10:12', '2018-01-01 10:30'],
            [60.0, '2017-12-24 11:31', '2018-01-01 10:30'],
            [60.0, '2017-12-24 09:22', '2018-01-01 10:30'],
            [30.0, '2017-12-24 12:15', '2018-05-01 10:00'],
            ]

start_date_raw = '2018-01-01'# '%Y-%m-%d'
end_date_raw = '2018-01-01' # '%Y-%m-%d'
start_time_raw = '09:00' # '%H:%M'
end_time_raw = '11:00' # '%H:%M'

min_interval = 30 # in minutes
max_interval = 60 # in minutes

generate_output(n_machines, patients, start_date_raw, end_date_raw, start_time_raw, end_time_raw, min_interval, max_interval)

