from datetime import datetime
import threading
import time


INITIAL_TIMESTAMP = datetime.now()


def get_elapsed_seconds() -> float:
    return round((datetime.now() - INITIAL_TIMESTAMP).total_seconds(), 1)

class CustomerThread(threading.Thread):
    def __init__(self, customer_info, ticket_price, store_control, earnings_update, store_earnings, vip_complete, vip_count):
        super().__init__(name=customer_info["name"])
        self.customer_info = customer_info
        self.ticket_price = ticket_price
        self.store_control = store_control  
        self.earnings_update = earnings_update  
        self.store_earnings = store_earnings  
        self.vip_complete = vip_complete  
        self.vip_count = vip_count

    def run(self):
        customer_start_time = time.time()
        
        remaining_join_delay = max(0, self.customer_info["joinDelay"] - (time.time() - customer_start_time))
        if remaining_join_delay > 0:
            time.sleep(remaining_join_delay)
        
        if self.customer_info["VIP"]:
            self.store_control.acquire()
            print(f'{get_elapsed_seconds()}s: {self.name} (entering)')
            time.sleep(self.customer_info["timeInStore"])
            with self.earnings_update:
                self.store_earnings[0] += self.ticket_price * self.customer_info["ticketCount"]
            print(f'{get_elapsed_seconds()}s: {self.name} (leaving)')
            self.store_control.release()
            self.vip_count[0] -= 1
            if self.vip_count[0] == 0:
                self.vip_complete.release()
        else:
            if self.vip_count[0] == 0:
                self.vip_complete.release()
            else:
                self.vip_complete.acquire()
                self.vip_complete.release()
            
            self.store_control.acquire()
            print(f'{get_elapsed_seconds()}s: {self.name} (entering)')
            time.sleep(self.customer_info["timeInStore"])
            with self.earnings_update:
                self.store_earnings[0] += self.ticket_price * self.customer_info["ticketCount"]
            print(f'{get_elapsed_seconds()}s: {self.name} (leaving)')
            self.store_control.release()

def simulate_store(customers: [dict], ticket_price: float, max_occupancy: int, n_vips: int) -> float:
    store_earnings = [0]
    store_control = threading.Semaphore(max_occupancy)
    earnings_update = threading.Semaphore(1)
    vip_complete = threading.Semaphore(0)  
    vip_count = [n_vips]

    threads = []

    for customer in customers:
        thread = CustomerThread(
            customer_info=customer,
            ticket_price=ticket_price,
            store_control=store_control,
            earnings_update=earnings_update,
            store_earnings=store_earnings,
            vip_complete=vip_complete,
            vip_count=vip_count,
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


#I was struggling with this simple function for a plenty of time because without 'round' I had an error for float numbers.
    return round(store_earnings[0], 1)
