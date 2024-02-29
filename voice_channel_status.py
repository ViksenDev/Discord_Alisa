import discord
from discord.ext import commands, tasks

class VoiceChannelStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_status.start()

    @tasks.loop(seconds=60)
    async def update_status(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                if voice_channel.members:
                    activities = [member.activity for member in voice_channel.members]
                    most_common_activity = max(set(activities), key=activities.count)
                    if most_common_activity is not None:
                        await voice_channel.edit(name=f"{voice_channel.name} | {most_common_activity.name}")
                    else:
                        random_activity = random.choice(activities)
                        await voice_channel.edit(name=f"{voice_channel.name} | {random_activity.name}")

def setup(bot):
    bot.add_cog(VoiceChannelStatus(bot))
