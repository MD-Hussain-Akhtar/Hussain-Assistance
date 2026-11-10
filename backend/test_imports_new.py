import sys
sys.path.insert(0, r'G:\ada_v2-main\backend')
try:
    import app_indexer, media_controller, screen_reader, command_router, command_view
    print('IMPORT_OK')
except Exception as e:
    print('IMPORT_ERR', e)
