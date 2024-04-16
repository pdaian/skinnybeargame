from threading import Thread


# credit https://gist.githubusercontent.com/raviolliii/94e9e16ef74f3c4f0886c6eb1fdfa157/raw/b32018243349061aac2776b25c957045ea298d07/thread_decorator.py
def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread
    return wrapper
