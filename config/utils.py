import os


def get_env_variable(var_name, default=None):
    """Get environment variable or return default value."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f'Set the {var_name} environment variable'
        raise ValueError(error_msg)
