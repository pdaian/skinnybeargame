import importlib, sys, numpy # import here to avoid reload


# https://stackoverflow.com/questions/45405600/how-to-reload-all-imported-modules
def init() :
    # local imports to keep things neat
    from sys import modules
    import importlib

    global PRELOADED_MODULES

    # sys and importlib are ignored here too
    PRELOADED_MODULES = set(modules.values())

def reload() :
    from sys import modules
    import importlib

    for module in set(modules.values()) - PRELOADED_MODULES :
        try :
            importlib.reload(module)
        except :
            # there are some problems that are swept under the rug here
            pass

init()
import app, cache

if __name__ == '__main__':
    print("App1")
    myapp = app.App()
    mycache = myapp.cache
    myapp.run()
    print("XIT")
    while True:
        print("LOOP")
        
        reload()
        myapp = app.App(cache=mycache)
        myapp.run()
