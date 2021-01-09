from multiprocessing import cpu_count

k = "eventlet"
workers = cpu_count()
threads = cpu_count()
timeout = 600
bind = "0.0.0.0:5000"