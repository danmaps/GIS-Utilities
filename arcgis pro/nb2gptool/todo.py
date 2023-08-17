from textual.app import App
from textual.widgets import Placeholder

class HelloWorldApp(App):
    async def on_load(self, event):
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event):
        await self.view.dock(Placeholder, edge="top", size=1)

if __name__ == "__main__":
    HelloWorldApp.run()
