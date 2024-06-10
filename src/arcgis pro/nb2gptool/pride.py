from textual.app import App
from textual.widgets import Placeholder, Footer, TextInput, Button

class ToDoApp(App):
    async def on_load(self, event):
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event):
        await self.view.dock(Placeholder, edge="top", size=1)
        await self.view.dock(Footer, Placeholder, edge="bottom", size=1)

        self.input = await self.view.dock(TextInput, Placeholder, edge="bottom", size=1)
        self.add_button = await self.view.dock(Button, Placeholder, edge="bottom", size=1)
        self.add_button.text = "Add Task"
        await self.add_button.clicked(self.add_task)

        self.tasks = []

    async def add_task(self, event):
        task = self.input.value.strip()
        if task:
            self.tasks.append(task)
            self.input.value = ""
            await self.update()

    async def on_render(self, event):
        yield "To-Do List:\n"
        for idx, task in enumerate(self.tasks, start=1):
            yield f"{idx}. {task}\n"

if __name__ == "__main__":
    ToDoApp.run()
