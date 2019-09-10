"""The run_loader.py executable file launched by the cron."""
# Change path: #!/home/renokan/www-ovdp/venv/bin/python

from loader import loader

if __name__ == '__main__':
    # loader(mode_debug)  <-- True or False
    loader()
