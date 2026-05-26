try:
    from channels.generic.websocket import AsyncJsonWebsocketConsumer
except ImportError:  # pragma: no cover - fallback stub when channels is absent
    AsyncJsonWebsocketConsumer = object


class SupportHubConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.group_names = []
        if user.is_staff:
            self.group_names.append("support_staff")
        organizer = getattr(user, "organizer_profile", None)
        if organizer:
            self.group_names.append(f"support_user_{organizer.id}")

        for group_name in self.group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self.accept()
        await self.send_json({"kind": "support.connected"})

    async def disconnect(self, close_code):
        for group_name in getattr(self, "group_names", []):
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def support_event(self, event):
        await self.send_json(event["payload"])
