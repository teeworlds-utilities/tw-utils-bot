"""binds manager"""

from typing import Union, Any, Callable

class Bind:
    """
        Describing combination (key -- callback)
    """

    def __init__(self, key: Any, callback: Callable, *args: list, **kwargs: dict):
        self.key = key
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    async def try_call(self, *additional_args: list, **additional_kwargs: dict) -> Any:
        """
            Tries to call the stored function
        """

        args = [*self.args, *additional_args]
        kwargs = {**self.kwargs, **additional_kwargs}

        try:
            ret = await self.callback(*args, **kwargs)
        except:
            ret = self.callback(*args, **kwargs)

        return ret

class Binds:
    """
        Manages the Bind objects
        hotkey --> function
    """

    def __init__(self):
        self.key_binding = {}

    def __getitem__(self, key: Any) -> Union[Bind, None]:
        if not key in self.key_binding.keys():
            return None

        return self.key_binding[key]

    def add_bind(self, key: Any, function: callable, *args: list, **kwargs: dict):
        """
            Add a Bind to the dictionnary
        """

        bind = Bind(key, function, *args, **kwargs)

        self.key_binding[key] = bind

    async def try_call_from_bind(self, key: Any, *add_args: list, **add_kwargs: dict) -> Any:
        """
            If the dictionnary key is found,
            then it tries to call the associated function
        """

        bind = self[key]

        if not bind:
            return False

        return await bind.try_call(*add_args, **add_kwargs)
