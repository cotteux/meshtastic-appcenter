from log_utils import get_logger

logger = get_logger(name="Plugins")

sorted_active_plugins = []


def load_plugins():
    from plugins.help_plugin import Plugin as HelpPlugin
    from plugins.health_plugin import Plugin as HealthPlugin
    from plugins.ping_plugin import Plugin as PingPlugin
    from plugins.weather_plugin import Plugin as WeatherPlugin
    from plugins.web_plugin import Plugin as WebPlugin
    from plugins.drop_plugin import Plugin as DropPlugin
    from plugins.debug_plugin import Plugin as DebugPlugin

    global sorted_active_plugins
    if sorted_active_plugins:
        return sorted_active_plugins

    plugins = [
        HealthPlugin(),
        PingPlugin(),
        WeatherPlugin(),
        WebPlugin(),
        HelpPlugin(),
        DropPlugin(),
        DebugPlugin()
    ]

    active_plugins = []
    for plugin in plugins:
        if plugin.config["active"]:
            plugin.priority = (
                plugin.config["priority"]
                if "priority" in plugin.config
                else plugin.priority
            )
            active_plugins.append(plugin)
            plugin.start()

    sorted_active_plugins = sorted(active_plugins, key=lambda plugin: plugin.priority)
    return sorted_active_plugins
