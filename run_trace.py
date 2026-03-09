import traceback
try:
    import teste_manual_cifras
    teste_manual_cifras.run_test()
except Exception as e:
    with open('error_log.txt', 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
