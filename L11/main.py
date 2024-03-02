import os
import signal
import threading
import sys
import json

from ticket_store import simulate_store


EXPECTED_THREADS = {}
CREATED_THREADS = {}


def load_customer_data() -> ([dict], int):
    global EXPECTED_THREADS
    global CREATED_THREADS

    with open('customers.json') as fd:
        customers = json.loads(fd.read())

        EXPECTED_THREADS = {c['name']: len([c2 for c2 in customers if c2['name'] == c['name']]) for c in customers}
        CREATED_THREADS = {c['name']: 0 for c in customers}

        return customers, len([c for c in customers if c['VIP']])


def thread_tracer(frame, event, arg = None) -> None:
    op = frame.f_code.co_name

    if op == 'run':
        thread_name = frame.f_locals['self'].name
        check_created_thread(thread_name)
        CREATED_THREADS[thread_name] += 1


def check_created_thread(thread_name) -> None:
    if thread_name not in EXPECTED_THREADS:
        print(f'Unexpected customer thread {thread_name}')
        os.kill(os.getpid(), signal.SIGKILL)
    elif CREATED_THREADS[thread_name] == EXPECTED_THREADS[thread_name]:
        print(f'Reached maximum number of customer threads for {thread_name} ({EXPECTED_THREADS[thread_name]}).')
        os.kill(os.getpid(), signal.SIGKILL)


def check_expected_threads() -> None:
    for key, val in EXPECTED_THREADS.items():
        if key not in CREATED_THREADS:
            sys.exit(f'Expected customer thread {key} was not found.')
        elif val != CREATED_THREADS[key]:
            sys.exit(f'Unexpected number of threads for customer {key}. Expected {val}, found {CREATED_THREADS[key]}')


def check_earnings(earnings: float, ticket_price: float, customers: [dict]) -> None:
    expected_earnings = sum([ticket_price * c['ticketCount'] for c in customers])

    if expected_earnings != earnings:
        sys.exit(f'Expected earnings ({expected_earnings}) don\'t match actual earnings ({earnings}).')
    else:
        print('Total earnings:', earnings)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('You must pass two command line arguments, '
                 'where the first is the ticket sell price and the second the maximum room occupancy.')
    else:
        threading.settrace(thread_tracer)

        ticket_price = float(sys.argv[1].replace(',', '.'))
        max_occupancy = int(sys.argv[2])
        customers, n_vips = load_customer_data()

        earnings = simulate_store(customers, ticket_price, max_occupancy, n_vips)

        check_expected_threads()
        check_earnings(earnings, ticket_price, customers)
