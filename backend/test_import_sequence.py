import sys, traceback
sys.path.insert(0, r'G:\ada_v2-main\backend')
modules = ['app_indexer','media_controller','screen_reader','command_router','command_view']
for m in modules:
    try:
        __import__(m)
        print(m + ' OK')
    except Exception as e:
        print(m + ' ERR', e)
        traceback.print_exc()
        break
